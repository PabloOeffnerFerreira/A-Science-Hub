from __future__ import annotations
import os, re, json, gzip, requests
from urllib.parse import quote
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QTextEdit
)
from core.data.functions.log import add_log_entry
from core.data.functions.bio_utils import HTML_VIEWER
# ---- config/const ----
HUB_SUMMARY = "https://www.ebi.ac.uk/pdbe/pdbe-kb/3dbeacons/api/uniprot/summary/{acc}.json"
AF_FILES_BASE = "https://alphafold.ebi.ac.uk/files/"
CACHE_BASE = os.path.join(os.path.expanduser("~"), ".ash_cache", "alphafold")

def _ensure_dir(p): os.makedirs(p, exist_ok=True)
def _download(url, timeout=60): 
    r = requests.get(url, timeout=timeout); r.raise_for_status(); return r.content
def _maybe_gunzip(data: bytes, url: str) -> bytes: return gzip.decompress(data) if url.endswith(".gz") else data

def _basename_from_model_url(model_url: str) -> str | None:
    m = re.search(r'/files/(AF-[A-Za-z0-9]+-F\d+)-model_v\d+\.(?:pdb|cif)(?:\.gz)?$', model_url)
    return m.group(1) if m else None

# ---- viewer dialog ----
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEB_OK = True
except Exception:
    WEB_OK = False
    QWebEngineView = object  # type: ignore

from PyQt6.QtWebEngineCore import QWebEngineSettings

class ViewerDialog(QDialog):
    def __init__(self, model_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AlphaFold 3D Viewer")
        self.resize(900, 640)
        lay = QVBoxLayout(self)

        if not WEB_OK:
            lay.addWidget(QLabel("pyqt6-webengine is not installed. 3D viewing unavailable."))
            return

        # Read structure text and decide ext for NGL
        try:
            with open(model_path, "r", encoding="utf-8", errors="replace") as f:
                self._model_text = f.read()
        except Exception:
            # Last resort: treat as binary then decode
            with open(model_path, "rb") as f:
                self._model_text = f.read().decode("utf-8", errors="replace")

        self._ext = "pdb" if model_path.lower().endswith(".pdb") else "cif"

        self.web = QWebEngineView(self)
        # Allow local content more freedom (not strictly needed with Blob approach,
        # but keeps things robust if you load external resources)
        s = self.web.settings()
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        s.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        self.web.setHtml(HTML_VIEWER, baseUrl=QUrl("https://nglviewer.org/"))
        lay.addWidget(self.web)

        # Inject after the HTML is fully loaded (ensures loadFromText exists)
        def _inject(_ok: bool):
            js = f'window.loadFromText({json.dumps(self._model_text)}, {json.dumps(self._ext)});'
            self.web.page().runJavaScript(js)
        self.web.loadFinished.connect(_inject)



# ---- main tool ----
class Tool(QDialog):
    TITLE = "AlphaFold"

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(860)
        self.setMinimumHeight(560)

        lay = QVBoxLayout(self)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("UniProt accession:"))
        self.acc = QLineEdit("A9VLF6"); row1.addWidget(self.acc)

        row1.addWidget(QLabel("Format:"))
        self.format = QComboBox(); self.format.addItems(["PDB", "mmCIF"]); row1.addWidget(self.format)

        self.want_conf = QCheckBox("Fetch pLDDT/PAE"); self.want_conf.setChecked(True); row1.addWidget(self.want_conf)

        self.btn_fetch = QPushButton("Fetch")
        self.btn_fetch.clicked.connect(self._fetch)
        row1.addWidget(self.btn_fetch)

        self.btn_view = QPushButton("Open 3D Viewer")
        self.btn_view.setEnabled(False)
        self.btn_view.clicked.connect(self._open_viewer)
        row1.addWidget(self.btn_view)

        lay.addLayout(row1)

        self.out = QTextEdit(); self.out.setReadOnly(True); lay.addWidget(self.out, 1)
        lay.addWidget(QLabel("AlphaFold DB predictions are CC-BY-4.0; include proper attribution in outputs."))

        self._model_path = None

    # ---- helpers ----
    def _log(self, msg: str): self.out.append(msg)

    def _hub_summary(self, acc: str):
        url = HUB_SUMMARY.format(acc=acc)
        self._log(f"Querying 3D-Beacons summary: {url}")
        r = requests.get(url, timeout=45); r.raise_for_status(); return r.json()

    def _pick_af(self, j):
        if isinstance(j, dict): structs = j.get("structures", [])
        else:
            structs = []
            for it in j:
                if isinstance(it, dict) and "structures" in it:
                    structs = it["structures"]; break
        cand = []
        for s in structs:
            provider = (s.get("summary") or {}).get("provider") or s.get("provider") or ""
            if provider.lower().startswith("alphafold"): cand.append(s)
        if not cand: return None
        cand.sort(key=lambda s: float((s.get("summary") or {}).get("coverage", 0.0)), reverse=True)
        return cand[0]

    def _swap_ext_for_format(self, url: str, want_fmt: str) -> str:
        want = want_fmt.lower()
        if want == "pdb":
            if url.endswith((".pdb", ".pdb.gz")): return url
            guess = re.sub(r'\.(?:cif|mmcif)(\.gz)?$', '.pdb.gz', url)
        else:
            if url.endswith((".cif", ".mmcif", ".cif.gz")): return url
            guess = re.sub(r'\.pdb(\.gz)?$', '.cif.gz', url)
        try:
            _download(guess, timeout=8)  # probe
            # Note: probe bytes ignored; we will download again below with normal timeout
            return guess
        except Exception:
            self._log("PDB variant not available, falling back to provider format.")
            return url

    def _fetch_conf(self, base_token: str, dest_dir: str):
        try:
            self._log("Fetching pLDDT JSON…")
            b = _download(f"{AF_FILES_BASE}{base_token}-confidence_v4.json")
            with open(os.path.join(dest_dir, f"{base_token}-confidence_v4.json"), "wb") as f: f.write(b)
        except Exception: pass
        try:
            self._log("Fetching PAE JSON…")
            b = _download(f"{AF_FILES_BASE}{base_token}-predicted_aligned_error_v4.json")
            with open(os.path.join(dest_dir, f"{base_token}-predicted_aligned_error_v4.json"), "wb") as f: f.write(b)
        except Exception: pass

    # ---- actions ----
    def _fetch(self):
        self.btn_view.setEnabled(False)
        self._model_path = None
        acc = self.acc.text().strip()
        if not acc:
            self._log("Provide a UniProt accession."); return
        try:
            j = self._hub_summary(acc)
            item = self._pick_af(j)
            if not item:
                self._log("No AlphaFold entries found."); 
                add_log_entry(self.TITLE, action="Fetch", data={"acc": acc, "status":"no_model"})
                return

            summ = item.get("summary", {})
            model_url = summ.get("model_url")
            if not model_url: raise RuntimeError("AlphaFold entry missing model_url")

            chosen = self._swap_ext_for_format(model_url, self.format.currentText())

            dest = os.path.join(CACHE_BASE, acc); _ensure_dir(dest)
            self._log(f"Downloading model:\n{chosen}")
            raw = _download(chosen); raw = _maybe_gunzip(raw, chosen)
            ext = ".pdb" if chosen.endswith(".pdb") or chosen.endswith(".pdb.gz") else ".cif"
            path = os.path.join(dest, f"{acc}_alphafold{ext}")
            with open(path, "wb") as f: f.write(raw)
            self._log(f"Saved → {path}")
            self._model_path = path

            base = _basename_from_model_url(chosen)
            if self.want_conf.isChecked() and base:
                self._fetch_conf(base, dest)

            self._log("\nSummary")
            self._log(f"Coverage: {summ.get('coverage')}")
            self._log(f"Created: {summ.get('created')}")
            self._log(f"Model ID: {summ.get('model_identifier')}")

            self.btn_view.setEnabled(True)
            add_log_entry(self.TITLE, action="Fetch", data={"acc":acc, "file":path})
        except Exception as e:
            self._log(f"Error: {type(e).__name__}: {e}")
            add_log_entry(self.TITLE, action="Error", data={"acc":acc, "msg":str(e)})

    def _open_viewer(self):
        if not self._model_path:
            self._log("No model loaded yet."); return
        if not WEB_OK:
            self._log("Install pyqt6-webengine to enable 3D viewing."); return
        dlg = ViewerDialog(self._model_path, self)
        dlg.exec()
