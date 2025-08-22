# 1. Importing
import io
import json
import urllib.parse
import urllib.request
import PyQt6.QtWebEngineWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QGuiApplication
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit,
    QComboBox, QListWidget, QListWidgetItem, QWidget, QSplitter, QMessageBox, QFileDialog
)

# Dependencies for interactive 3D viewer
from PyQt6.QtWebEngineWidgets import QWebEngineView
import py3Dmol
from rdkit import Chem
from rdkit.Chem import AllChem, Draw

from core.data.functions.log import add_log_entry

try:
    from core.data.paths import IMAGES_DIR
except Exception:
    IMAGES_DIR = None


# 2. Constants
PUBCHEM = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


# 3. Helper functions (HTTP and JSON)
def _http_get(url: str, timeout: int = 20) -> bytes | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.read()
    except Exception:
        return None


def _json(url: str) -> dict | None:
    raw = _http_get(url)
    if not raw:
        return None
    try:
        return json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception:
        return None


# 4. PubChem query and parsing
def _resolve_cids(kind: str, term: str) -> list[int]:
    kind = kind.lower()
    term = term.strip()

    if kind in ("cid", "auto") and term.isdigit():
        return [int(term)]

    if kind == "auto":
        if term.upper().startswith("INCHIKEY=") or (len(term) == 27 and term.count("-") == 2):
            kind = "inchikey"
        elif term.upper().startswith("INCHI="):
            kind = "inchi"
        elif any(c in term for c in "=#()/\\"):
            kind = "smiles"
        else:
            kind = "name"

    enc = urllib.parse.quote(term)
    if kind == "name":
        url = f"{PUBCHEM}/compound/name/{enc}/cids/JSON"
    elif kind == "smiles":
        url = f"{PUBCHEM}/compound/smiles/{enc}/cids/JSON"
    elif kind == "inchi":
        url = f"{PUBCHEM}/compound/inchi/{enc}/cids/JSON"
    elif kind == "inchikey":
        url = f"{PUBCHEM}/compound/inchikey/{enc}/cids/JSON"
    elif kind == "cid":
        return [int(term)]
    else:
        return []

    obj = _json(url)
    if not obj:
        return []
    try:
        cids = obj["IdentifierList"]["CID"]
        return [int(c) for c in cids]
    except Exception:
        pass
    try:
        return [int(obj["PC_ID"]["ID"]["CID"])]
    except Exception:
        return []


def _properties_for_cid(cid: int) -> dict:
    props = ("CanonicalSMILES,IUPACName,IsomericSMILES,InChI,InChIKey,"
             "MolecularFormula,MolecularWeight,ExactMass,MonoisotopicMass,TPSA,"
             "HBondDonorCount,HBondAcceptorCount,RotatableBondCount,Charge,XLogP")
    url = f"{PUBCHEM}/compound/cid/{cid}/property/{props}/JSON"
    obj = _json(url) or {}
    out = {}
    try:
        out.update(obj["PropertyTable"]["Properties"][0])
    except Exception:
        pass
    syn = _json(f"{PUBCHEM}/compound/cid/{cid}/synonyms/JSON") or {}
    try:
        out["Synonyms"] = syn["InformationList"]["Information"][0]["Synonym"][:25]
    except Exception:
        pass
    return out


def _png_for_cid(cid: int, size: str = "large", record_type: str | None = None) -> bytes | None:
    url = f"{PUBCHEM}/compound/cid/{cid}/PNG?image_size={size}"
    if record_type:
        url += f"&record_type={urllib.parse.quote(record_type)}"
    img = _http_get(url)
    if img:
        return img
    url = f"{PUBCHEM}/compound/cid/{cid}/PNG?image_size={size}&record_type=3d"
    return _http_get(url)


# 5. Molecule data retrieval (3D MolBlocks)
def _molblock_3d_for_cid(cid: int) -> str | None:
    sdf_url = f"{PUBCHEM}/compound/cid/{cid}/record/SDF/?record_type=3d"
    raw = _http_get(sdf_url)
    if raw:
        try:
            return raw.decode("utf-8", errors="ignore")
        except Exception:
            return None
    sdf_url = f"{PUBCHEM}/compound/cid/{cid}/record/SDF/?record_type=2d"
    raw = _http_get(sdf_url)
    if raw:
        try:
            return raw.decode("utf-8", errors="ignore")
        except Exception:
            return None
    return None


def _molblock_from_smiles(smiles: str) -> str | None:
    if Chem is None or AllChem is None:
        return None
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, AllChem.ETKDG())
        AllChem.UFFOptimizeMolecule(mol)
        return Chem.MolToMolBlock(mol)
    except Exception:
        return None


# 6. 3D Viewer class
class Molecule3DViewer(QDialog):
    def __init__(self, cid: int, smiles: str | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"3D Viewer – CID {cid}")
        self.setMinimumSize(640, 640)

        vbox = QVBoxLayout(self)

        mb = _molblock_3d_for_cid(cid)
        if not mb and smiles:
            mb = _molblock_from_smiles(smiles)

        if not mb:
            lab = QLabel("No 3D model available.")
            lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox.addWidget(lab)
            return

        view = py3Dmol.view(width=800, height=800)
        view.addModel(mb, "sdf")
        view.setStyle({"stick": {}})
        view.zoomTo()
        html = view._make_html()

        self.web = QWebEngineView()
        self.web.setHtml(html)
        vbox.addWidget(self.web)


# 7. Main Molecule Library tool class
class Tool(QDialog):
    TITLE = "Molecule Library (PubChem)"

    def __init__(self):
        super().__init__()
        self.setMinimumSize(980, 680)

        # Top controls
        top = QHBoxLayout()
        top.addWidget(QLabel("Query:"))
        self.kind = QComboBox()
        self.kind.addItems(["auto", "name", "cid", "smiles", "inchi", "inchikey"])
        top.addWidget(self.kind)

        self.q = QLineEdit()
        self.q.setPlaceholderText("e.g., aspirin  |  2244  |  CC(=O)OC1=CC=CC=C1C(=O)O  |  InChI=...  |  BSYNRYMUTXBXSQ-UHFFFAOYSA-N")
        top.addWidget(self.q, 1)

        self.search_btn = QPushButton("Search")
        top.addWidget(self.search_btn)

        # Results and detail area
        self.results = QListWidget()
        self.results.setMaximumWidth(260)

        self.name_label = QLabel("<b>Name:</b> —")
        self.cid_label = QLabel("<b>CID:</b> —")
        self.img_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.img_label.setMinimumHeight(260)
        self.img_label.setStyleSheet("border: 1px solid #ccc; background: white;")
        self.save_btn = QPushButton("Save Image…")
        self.open3d_btn = QPushButton("Open 3D…")

        self.props_view = QTextEdit()
        self.props_view.setReadOnly(True)

        right_top = QHBoxLayout()
        right_top.addWidget(self.name_label, 1)
        right_top.addWidget(self.cid_label, 0)

        img_row = QHBoxLayout()
        img_row.addWidget(self.img_label, 1)
        col = QVBoxLayout()
        col.addWidget(self.save_btn)
        col.addWidget(self.open3d_btn)
        col.addStretch(1)
        img_row.addLayout(col, 0)

        right = QVBoxLayout()
        right.addLayout(right_top)
        right.addLayout(img_row)
        right.addWidget(QLabel("<b>Properties</b>"))
        right.addWidget(self.props_view, 1)

        container = QSplitter()
        left_w = QWidget(); lw = QVBoxLayout(left_w); lw.addWidget(QLabel("<b>Matches</b>")); lw.addWidget(self.results, 1)
        right_w = QWidget(); rw = QVBoxLayout(right_w); rw.addLayout(right)

        container.addWidget(left_w)
        container.addWidget(right_w)
        container.setStretchFactor(0, 0)
        container.setStretchFactor(1, 1)

        root = QVBoxLayout(self)
        root.addLayout(top)
        root.addWidget(container, 1)

        # Signals
        self.search_btn.clicked.connect(self._search)
        self.results.currentItemChanged.connect(self._select_current)
        self.save_btn.clicked.connect(self._save_image)
        self.open3d_btn.clicked.connect(self._open_3d)

        # State
        self._cid_list: list[int] = []
        self._cid_to_props: dict[int, dict] = {}
        self._cid_to_image: dict[int, bytes] = {}

    # 8. Methods for searching, selecting, saving, and opening 3D
    def _search(self):
        term = self.q.text().strip()
        if not term:
            QMessageBox.information(self, "Input", "Enter a query.")
            return

        kind = self.kind.currentText()
        cids = _resolve_cids(kind, term)
        if not cids:
            self.results.clear()
            self.props_view.setPlainText("No results.")
            self.img_label.clear()
            self.name_label.setText("<b>Name:</b> —")
            self.cid_label.setText("<b>CID:</b> —")
            add_log_entry("Molecule Library", action="QueryNoResults", data={"kind": kind, "q": term})
            return

        self._cid_list = cids
        self.results.clear()
        for cid in cids:
            it = QListWidgetItem(f"CID {cid}")
            it.setData(Qt.ItemDataRole.UserRole, cid)
            self.results.addItem(it)
        self.results.setCurrentRow(0)
        add_log_entry("Molecule Library", action="Query", data={"kind": kind, "q": term, "n": len(cids)})

    def _select_current(self, _cur: QListWidgetItem, _prev: QListWidgetItem = None):
        it = self.results.currentItem()
        if not it:
            return
        cid = it.data(Qt.ItemDataRole.UserRole)
        if not cid:
            return

        if cid not in self._cid_to_props:
            self._cid_to_props[cid] = _properties_for_cid(cid)
        props = self._cid_to_props.get(cid, {})

        if cid not in self._cid_to_image:
            img = _png_for_cid(cid, size="large")
            if not img:
                img = _png_for_cid(cid, size="medium")
            self._cid_to_image[cid] = img or b""

        name = props.get("IUPACName") or (props.get("Synonyms", [None])[0]) or "—"
        self.name_label.setText(f"<b>Name:</b> {name}")
        self.cid_label.setText(f"<b>CID:</b> {cid}")

        png = self._cid_to_image[cid]
        if png:
            pm = QPixmap()
            pm.loadFromData(png)
            self.img_label.setPixmap(pm.scaled(
                self.img_label.width(), self.img_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.img_label.setText("No image.")

        lines = []
        order = [
            "IUPACName","MolecularFormula","MolecularWeight","ExactMass","MonoisotopicMass",
            "CanonicalSMILES","IsomericSMILES","InChI","InChIKey","XLogP","TPSA",
            "HBondDonorCount","HBondAcceptorCount","RotatableBondCount","Charge",
        ]
        for k in order:
            v = props.get(k)
            if v is not None:
                lines.append(f"{k}: {v}")
        if "Synonyms" in props:
            lines.append("Synonyms: " + ", ".join(props["Synonyms"]))
        self.props_view.setPlainText("\n".join(lines))

    def _save_image(self):
        it = self.results.currentItem()
        if not it:
            return
        cid = it.data(Qt.ItemDataRole.UserRole)
        png = self._cid_to_image.get(cid, b"")
        if not png:
            QMessageBox.information(self, "Save", "No image to save.")
            return

        default_dir = IMAGES_DIR or ""
        path, _ = QFileDialog.getSaveFileName(self, "Save PNG", str(default_dir), "PNG Image (*.png)")
        if not path:
            return
        try:
            with open(path, "wb") as f:
                f.write(png)
            add_log_entry("Molecule Library", action="SaveImage", data={"cid": cid, "path": path})
        except Exception as e:
            QMessageBox.warning(self, "Save failed", str(e))

    def _open_3d(self):
        it = self.results.currentItem()
        if not it:
            return
        cid = it.data(Qt.ItemDataRole.UserRole)
        props = self._cid_to_props.get(cid) or {}
        smiles = props.get("CanonicalSMILES") if props else None

        viewer = Molecule3DViewer(cid=cid, smiles=smiles, parent=self)
        viewer.setModal(False)
        viewer.show()
        add_log_entry("Molecule Library", action="Open3D", data={"cid": cid, "has_smiles": bool(smiles)})
