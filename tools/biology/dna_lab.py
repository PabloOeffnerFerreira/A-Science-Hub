#TODO
# Structural Tools
# - Add 3D visualization of DNA, RNA, and proteins
# - Integrate Alphafold (or other structure prediction tools) for protein folding
#
# Sequence Analysis
# - Extend codon usage statistics with organism-specific tables
# - Add motif and restriction site search
# - Implement RNA secondary structure prediction (hairpins, stems)
#
# Integration Features
# - Cross-link transcription → translation → 3D visualization pipeline
# - Batch processing for multiple sequences
# - Export results in CSV and JSON formats
#
# Advanced Analysis
# - Mutation simulator: silent, missense, nonsense detection
# - Phylogenetic alignment and tree building
# - Protein domain prediction with database lookups

from __future__ import annotations
import os, json
from typing import Dict, Callable
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QListWidget, QListWidgetItem, QSplitter, QStackedWidget, QFrame, QToolBar, QMessageBox,
    QLineEdit, QFileDialog, QMenu, QInputDialog
)
from Bio import SeqIO

# --- Import your DNA tools ---
from labs.dna.codon_lookup import Tool as CodonLookupTool
from labs.dna.frame_translation import Tool as FrameTranslationTool
from labs.dna.transcription_translation import Tool as TranscriptionTranslationTool
from labs.dna.gc_content import Tool as GCContentTool
from labs.dna.molecular_weight_calculator import Tool as MolecularWeightTool
from labs.dna.reverse_complement import Tool as ReverseComplementTool
from labs.dna.pairwise_align import Tool as PairwiseAlignTool
from labs.dna.seq_parser import Tool as SeqParserTool

DNA_SEQ_PATH = os.path.join("core", "data", "databases", "dna_sequences.json")


class _Embedded(QWidget):
    """Wrap a QDialog subclass as embeddable widget."""
    def __init__(self, dialog_cls: Callable[[], QDialog], parent: QWidget | None = None):
        super().__init__(parent)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)
        self.inner = dialog_cls()
        self.inner.setParent(self)
        self.inner.setWindowFlag(Qt.WindowType.Widget, True)
        lay.addWidget(self.inner)


class Tool(QDialog):
    TITLE = "DNA Lab"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(self.TITLE); self.resize(1200, 760)

        # Global sequence + saved storage
        self.sequence: str = ""
        self.saved_sequences: Dict[str, str] = self._load_saved_sequences()

        # Layout
        root = QVBoxLayout(self)
        split = QSplitter(Qt.Orientation.Horizontal); split.setChildrenCollapsible(False)
        root.addWidget(split, 1)

        # Sidebar
        self.sidebar = self._build_sidebar(); split.addWidget(self.sidebar)

        # Tool stack
        self.stack = QStackedWidget(); split.addWidget(self.stack)

        # Tools
        self.codon_lookup   = _Embedded(CodonLookupTool)
        self.translation    = _Embedded(FrameTranslationTool)
        self.transcription  = _Embedded(TranscriptionTranslationTool)
        self.gc_content     = _Embedded(GCContentTool)
        self.mol_weight     = _Embedded(MolecularWeightTool)
        self.rev_complement = _Embedded(ReverseComplementTool)
        self.alignment      = _Embedded(PairwiseAlignTool)
        self.seq_parser     = _Embedded(SeqParserTool)

        for w in [self.codon_lookup, self.translation, self.transcription,
                  self.gc_content, self.mol_weight, self.rev_complement,
                  self.alignment, self.seq_parser]:
            self.stack.addWidget(w)

        # Toolbar AFTER tools exist
        root.insertWidget(0, self._build_toolbar())

        self.nav_select("Codon Lookup")

    # ---------- Toolbar ----------
    def _build_toolbar(self) -> QToolBar:
        tb = QToolBar(); tb.setIconSize(tb.iconSize())
        actions = {
            "Codon Lookup": self.codon_lookup,
            "Frame Translation": self.translation,
            "Transcription": self.transcription,
            "GC Content": self.gc_content,
            "Molecular Weight": self.mol_weight,
            "Reverse Complement": self.rev_complement,
            "Alignment": self.alignment,
            "Seq Parser": self.seq_parser,
        }
        for label in actions:
            act = QAction(QIcon.fromTheme("applications-science"), label, self)
            act.triggered.connect(lambda _, L=label: self.nav_select(L))
            tb.addAction(act)
        return tb

    # ---------- Sidebar ----------
    def _build_sidebar(self) -> QWidget:
        side = QFrame(); side.setMinimumWidth(320)
        lay = QVBoxLayout(side); lay.setContentsMargins(10,10,10,10); lay.setSpacing(8)

        # Title
        title = QLabel("DNA Sequences"); title.setStyleSheet("font-weight:600;font-size:16px;")
        lay.addWidget(title)

        # Input
        self.seq_entry = QTextEdit(); self.seq_entry.setPlaceholderText("Paste DNA sequence (A,T,C,G)...")
        self.seq_entry.setFixedHeight(100); lay.addWidget(self.seq_entry)

        # Buttons
        row = QHBoxLayout()
        self.apply_btn = QPushButton("Apply"); self.save_btn = QPushButton("Save")
        self.delete_btn = QPushButton("Delete"); self.clear_btn = QPushButton("Clear")
        row.addWidget(self.apply_btn); row.addWidget(self.save_btn); row.addWidget(self.delete_btn); row.addWidget(self.clear_btn)
        lay.addLayout(row)

        # Search
        self.search_entry = QLineEdit(); self.search_entry.setPlaceholderText("Search sequences...")
        self.search_entry.textChanged.connect(self._filter_saved_sequences)
        lay.addWidget(self.search_entry)

        # Saved list
        lay.addWidget(QLabel("Saved Sequences:"))
        self.saved_list = QListWidget()
        self.saved_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        for name, seq in self.saved_sequences.items():
            item = QListWidgetItem(name); item.setData(Qt.ItemDataRole.UserRole, seq)
            self.saved_list.addItem(item)
        lay.addWidget(self.saved_list, 1)

        # Export / Import row
        row2 = QHBoxLayout()
        self.export_one_btn = QPushButton("Export Selected"); self.export_all_btn = QPushButton("Export All")
        row2.addWidget(self.export_one_btn); row2.addWidget(self.export_all_btn)
        lay.addLayout(row2)

        self.import_btn = QPushButton("Import FASTA/GenBank"); lay.addWidget(self.import_btn)

        # Context menu
        self.saved_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.saved_list.customContextMenuRequested.connect(self._open_context_menu)

        # Connect
        self.apply_btn.clicked.connect(self._apply_sequence)
        self.save_btn.clicked.connect(self._save_sequence)
        self.delete_btn.clicked.connect(self._delete_sequence)
        self.clear_btn.clicked.connect(self._clear_sequence)
        self.saved_list.itemDoubleClicked.connect(self._load_saved)
        self.export_one_btn.clicked.connect(self._export_selected)
        self.export_all_btn.clicked.connect(self._export_all)
        self.import_btn.clicked.connect(self._import_sequences)

        return side

    # ---------- Sequence Handling ----------
    def _apply_sequence(self):
        self.sequence = self.seq_entry.toPlainText().strip().upper()
        self._broadcast_sequence()

    def _save_sequence(self):
        seq = self.seq_entry.toPlainText().strip().upper()
        if not seq: return
        name, ok = QInputDialog.getText(self, "Save Sequence", "Enter sequence name:")
        if not ok or not name.strip(): return
        self.saved_sequences[name] = seq; self._persist_sequences()
        item = QListWidgetItem(name); item.setData(Qt.ItemDataRole.UserRole, seq)
        self.saved_list.addItem(item)

    def _delete_sequence(self):
        items = self.saved_list.selectedItems()
        if not items: return
        for item in items:
            name = item.text()
            if name in self.saved_sequences: del self.saved_sequences[name]
            self.saved_list.takeItem(self.saved_list.row(item))
        self._persist_sequences()
        if self.sequence and self.sequence not in self.saved_sequences.values():
            self.seq_entry.clear(); self.sequence = ""

    def _clear_sequence(self):
        self.seq_entry.clear(); self.sequence = ""

    def _load_saved(self, item: QListWidgetItem):
        seq = item.data(Qt.ItemDataRole.UserRole)
        self.seq_entry.setPlainText(seq); self.sequence = seq; self._broadcast_sequence()

    def _broadcast_sequence(self):
        for tool in [self.codon_lookup, self.translation, self.transcription,
                     self.gc_content, self.mol_weight, self.rev_complement,
                     self.alignment]:
            inner = tool.inner
            for field in ["seq_entry", "seq", "entry"]:
                if hasattr(inner, field):
                    widget = getattr(inner, field)
                    try:
                        if hasattr(widget, "setText"): widget.setText(self.sequence)
                        elif hasattr(widget, "setPlainText"): widget.setPlainText(self.sequence)
                    except Exception: pass
                    break

    # ---------- Import / Export ----------
    def _import_sequences(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Sequences", "", "FASTA/GenBank (*.fasta *.fa *.gb *.gbk)")
        if not path: return
        try:
            try:
                records = list(SeqIO.parse(path, "fasta"))
                if not records: raise ValueError
            except Exception:
                records = list(SeqIO.parse(path, "genbank"))

            for rec in records:
                seq_str = str(rec.seq).upper()
                name = rec.id or f"Seq {len(self.saved_sequences)+1}"
                self.saved_sequences[name] = seq_str
                self._persist_sequences()
                item = QListWidgetItem(name); item.setData(Qt.ItemDataRole.UserRole, seq_str)
                self.saved_list.addItem(item)

            first_seq = str(records[0].seq).upper()
            self.seq_entry.setPlainText(first_seq); self.sequence = first_seq; self._broadcast_sequence()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to import:\n{e}")

    def _export_selected(self):
        items = self.saved_list.selectedItems()
        if not items: return
        path, _ = QFileDialog.getSaveFileName(self, "Export Selected", "selected_sequences.fasta", "FASTA (*.fasta)")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            for item in items:
                name, seq = item.text(), item.data(Qt.ItemDataRole.UserRole)
                f.write(f">{name}\n")
                for i in range(0, len(seq), 60): f.write(seq[i:i+60] + "\n")

    def _export_all(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export All", "all_sequences.fasta", "FASTA (*.fasta)")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            for name, seq in self.saved_sequences.items():
                f.write(f">{name}\n")
                for i in range(0, len(seq), 60): f.write(seq[i:i+60] + "\n")

    # ---------- Context Menu & Search ----------
    def _open_context_menu(self, pos):
        items = self.saved_list.selectedItems()
        if not items: return
        menu = QMenu(self)
        act_apply = menu.addAction("Apply (first selected)")
        act_export = menu.addAction("Export Selected")
        act_delete = menu.addAction("Delete Selected")
        action = menu.exec(self.saved_list.mapToGlobal(pos))
        if action == act_apply: self._load_saved(items[0])
        elif action == act_export: self._export_selected()
        elif action == act_delete: self._delete_sequence()

    def _filter_saved_sequences(self, text: str):
        text = text.strip().lower()
        for i in range(self.saved_list.count()):
            item = self.saved_list.item(i)
            item.setHidden(text not in item.text().lower())

    # ---------- Persistence ----------
    def _load_saved_sequences(self) -> Dict[str, str]:
        if not os.path.exists(DNA_SEQ_PATH): return {}
        try:
            with open(DNA_SEQ_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("dna_sequences", {})
        except Exception: return {}

    def _persist_sequences(self):
        try:
            with open(DNA_SEQ_PATH, "w", encoding="utf-8") as f:
                json.dump({"dna_sequences": self.saved_sequences}, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not save sequences:\n{e}")

    # ---------- Navigation ----------
    def nav_select(self, label: str):
        mapping = {
            "Codon Lookup": self.codon_lookup,
            "Frame Translation": self.translation,
            "Transcription": self.transcription,
            "GC Content": self.gc_content,
            "Molecular Weight": self.mol_weight,
            "Reverse Complement": self.rev_complement,
            "Alignment": self.alignment,
            "Seq Parser": self.seq_parser,
        }
        w = mapping.get(label)
        if not w:
            QMessageBox.warning(self, "Unknown", f"No view '{label}'"); return
        self.stack.setCurrentWidget(w); self.setWindowTitle(f"{self.TITLE} — {label}")
