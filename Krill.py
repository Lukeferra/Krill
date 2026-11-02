"""
Krill.py  v3.2
Convertitore universale nuvole di punti e mesh 3D
"""
import sys, gc, traceback
from pathlib import Path
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QProgressBar, QTextEdit,
    QGroupBox, QRadioButton, QButtonGroup, QCheckBox,
    QDoubleSpinBox, QFormLayout, QLineEdit, QMessageBox,
    QFrame, QTabWidget, QComboBox, QSlider, QDialog,
    QListWidget, QListWidgetItem, QAbstractItemView, QScrollArea)
from PyQt5.QtCore import Qt, QThread, QSettings, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPalette

NUVOLA_INPUT_FILTER = (
    "Nuvole di punti (*.e57 *.las *.laz *.ply *.pts *.ptx *.xyz *.txt *.csv);;"
    "E57 (*.e57);;LAS/LAZ (*.las *.laz);;PLY (*.ply);;"
    "PTS/PTX (*.pts *.ptx);;XYZ/TXT/CSV (*.xyz *.txt *.csv);;Tutti i file (*)")
NUVOLA_OUTPUT_FORMATS = ["LAZ","LAS","PLY","PTS","XYZ"]
NUVOLA_OUTPUT_EXT = {"LAZ":".laz","LAS":".las","PLY":".ply","PTS":".pts","XYZ":".xyz"}
MESH_INPUT_FILTER = (
    "Mesh 3D (*.stl *.obj *.ply *.glb *.gltf *.dae *.off);;"
    "STL (*.stl);;OBJ (*.obj);;PLY (*.ply);;GLB (*.glb);;"
    "GLTF (*.gltf);;DAE (*.dae);;OFF (*.off);;Tutti i file (*)")
MESH_OUTPUT_FORMATS = ["STL","OBJ","PLY","GLB","GLTF","DAE"]
MESH_OUTPUT_EXT = {"STL":".stl","OBJ":".obj","PLY":".ply","GLB":".glb","GLTF":".gltf","DAE":".dae"}

def safe_output_path(input_path, output_dir, fmt_ext):
    inp  = Path(input_path)
    outd = Path(output_dir)
    stem = inp.stem
    if outd.resolve() == inp.parent.resolve():
        stem = stem + "_krill"
    return str(outd / (stem + fmt_ext))

THEMES = {
    "light": dict(
        bg="#f4f6f8", surface="#ffffff", surface2="#f8f9fb", border="#e1e5ea", border_strong="#cfd5dc",
        text="#262b31", muted="#6a737d", faint="#9aa3ad",
        accent="#2e7d32", accent_hover="#276b2b", accent_press="#205a24", accent_soft="#e6f2e7",
        accent_on="#ffffff", warn="#b8691f", disabled="#cfd5dc", log_bg="#fbfcfd"),
    "dark": dict(
        bg="#14171a", surface="#1d2125", surface2="#23282d", border="#2d333a", border_strong="#3d454e",
        text="#e4e7eb", muted="#9aa3ad", faint="#6b747e",
        accent="#4caf50", accent_hover="#5cc260", accent_press="#43a047", accent_soft="#1f3524",
        accent_on="#0b1a0c", warn="#e0a05a", disabled="#3a4149", log_bg="#181b1f"),
}

STYLE_TEMPLATE = """
* { font-family: "Segoe UI", sans-serif; font-size: 10pt; }
QMainWindow, QDialog { background: @bg; }
QWidget { color: @text; }
QWidget#root, QTabWidget > QWidget, QDialog { background: @bg; }
QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; border: none; }
QToolTip { background: @surface; color: @text; border: 1px solid @border_strong; padding: 4px 6px; }

/* Tabs */
QTabWidget::pane { border: 1px solid @border; border-radius: 10px; background: @bg; top: -1px; }
QTabBar::tab { background: transparent; color: @muted; padding: 10px 22px; border: none;
               border-bottom: 2px solid transparent; margin-right: 6px; font-weight: 600; }
QTabBar::tab:selected { color: @accent; border-bottom: 2px solid @accent; }
QTabBar::tab:hover:!selected { color: @text; }

/* GroupBox */
QGroupBox { border: 1px solid @border; border-radius: 10px; margin-top: 14px;
            padding: 16px 12px 12px 12px; font-weight: 600; background: @surface; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: @muted; }
QGroupBox#slider_box { background: @surface2; margin-top: 0; padding: 8px; border-radius: 8px; }

/* Pulsanti */
QPushButton { background: @surface; border: 1px solid @border_strong; border-radius: 7px;
              padding: 7px 16px; color: @text; }
QPushButton:hover { background: @accent_soft; border-color: @accent; color: @accent; }
QPushButton:pressed { background: @border; }
QPushButton:disabled { color: @faint; border-color: @border; }
QPushButton:focus { border-color: @accent; }

QPushButton#btn_converti { background: @accent; color: @accent_on; font-weight: 600;
                           font-size: 11pt; padding: 9px 36px; border: none; border-radius: 8px; }
QPushButton#btn_converti:hover { background: @accent_hover; color: @accent_on; }
QPushButton#btn_converti:pressed { background: @accent_press; }
QPushButton#btn_converti:disabled { background: @disabled; color: @faint; }

QPushButton#btn_icon { background: transparent; border: 1px solid @border_strong; border-radius: 14px;
                       color: @muted; font-size: 11pt; padding: 0; }
QPushButton#btn_icon:hover { border-color: @accent; color: @accent; background: transparent; }

QPushButton#btn_link { background: transparent; border: none; color: @accent; padding: 4px 8px; }
QPushButton#btn_link:hover { text-decoration: underline; background: transparent; }

/* Input */
QLineEdit { background: @surface; border: 1px solid @border_strong; border-radius: 7px;
            padding: 6px 10px; color: @text; selection-background-color: @accent; selection-color: @accent_on; }
QLineEdit:focus { border-color: @accent; }

/* Log */
QTextEdit { background: @log_bg; border: 1px solid @border; border-radius: 8px;
            color: @muted; font-family: "Consolas", monospace; font-size: 9pt; padding: 4px; }

/* ProgressBar */
QProgressBar { background: @border; border: none; border-radius: 4px; max-height: 8px; text-align: center;
               color: transparent; }
QProgressBar::chunk { background: @accent; border-radius: 4px; }

/* Radio / Check */
QRadioButton, QCheckBox { color: @text; spacing: 8px; padding: 3px 0; }
QRadioButton::indicator { width: 14px; height: 14px; border-radius: 9px;
                          border: 2px solid @border_strong; background: @surface; }
QRadioButton::indicator:checked { border: 5px solid @accent; background: @surface; }
QRadioButton::indicator:hover, QCheckBox::indicator:hover { border-color: @accent; }
QCheckBox::indicator { width: 14px; height: 14px; border-radius: 4px;
                       border: 2px solid @border_strong; background: @surface; }
QCheckBox::indicator:checked { background: @accent; border-color: @accent; }
QRadioButton:disabled, QCheckBox:disabled { color: @faint; }

/* SpinBox / ComboBox */
QDoubleSpinBox, QSpinBox, QComboBox { background: @surface; border: 1px solid @border_strong;
                                      border-radius: 7px; padding: 5px 8px; color: @text; }
QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus { border-color: @accent; }
QDoubleSpinBox:disabled, QSpinBox:disabled, QComboBox:disabled { color: @faint; background: @surface2; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView { background: @surface; color: @text; border: 1px solid @border_strong;
                              selection-background-color: @accent_soft; selection-color: @accent; outline: none; }
QDoubleSpinBox::up-button, QSpinBox::up-button,
QDoubleSpinBox::down-button, QSpinBox::down-button { width: 16px; border: none; background: transparent; }

/* Lista file */
QListWidget { background: @surface; border: 1px solid @border_strong; border-radius: 8px;
              color: @text; font-size: 9pt; padding: 3px; outline: none; }
QListWidget::item { padding: 5px 8px; border-radius: 5px; }
QListWidget::item:selected { background: @accent_soft; color: @accent; }
QListWidget::item:hover:!selected { background: @surface2; }
QListWidget[dragActive="true"] { background: @accent_soft; border: 2px dashed @accent; padding: 2px; }

/* Slider */
QSlider::groove:horizontal { background: @border_strong; height: 4px; border-radius: 2px; }
QSlider::handle:horizontal { background: @accent; width: 16px; height: 16px;
                             margin: -7px 0; border-radius: 8px; border: 2px solid @surface; }
QSlider::handle:horizontal:hover { background: @accent_hover; }
QSlider::sub-page:horizontal { background: @accent; border-radius: 2px; }
QSlider::sub-page:horizontal:disabled { background: @disabled; }
QSlider::handle:horizontal:disabled { background: @disabled; }

/* Scrollbar */
QScrollBar:vertical { background: transparent; width: 8px; margin: 2px; }
QScrollBar::handle:vertical { background: @border_strong; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: @faint; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; background: none; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal { background: transparent; height: 8px; margin: 2px; }
QScrollBar::handle:horizontal { background: @border_strong; border-radius: 4px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: @faint; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; background: none; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

/* Separatori */
QFrame#sep { background: @border; max-height: 1px; border: none; }

/* Etichette */
QLabel { background: transparent; }
QLabel#lbl_info { color: @muted; font-size: 9pt; }
QLabel#lbl_info:disabled { color: @faint; }
QLabel#lbl_hint { color: @faint; font-size: 8pt; }
QLabel#lbl_title { color: @accent; font-size: 16pt; font-weight: 700; letter-spacing: 2px; }
QLabel#lbl_subtitle { color: @faint; }
QLabel#lbl_accent { color: @accent; font-weight: 600; }
QLabel#lbl_section { color: @accent; font-weight: 600; }
QLabel#lbl_count { color: @muted; font-size: 9pt; }
QLabel#lbl_key { color: @faint; }
QLabel#lbl_copy { color: @muted; font-size: 9pt; }
"""

def build_stylesheet(theme):
    import re
    pal = THEMES[theme]
    return re.sub(r"@(\w+)", lambda m: pal[m.group(1)], STYLE_TEMPLATE)

# ── LOADERS ──────────────────────────────────────────────────

def _filtra(pos, colori, log):
    v = np.isfinite(pos).all(axis=1)
    n = len(pos) - int(v.sum())
    if n: log(f"  Rimossi {n:,} punti non validi")
    return pos[v], (colori[v] if colori is not None else None)

def _norm_col(raw):
    r = np.asarray(raw, dtype=np.float32)
    if r.max() <= 1.0: r = r * 255.0
    return np.clip(r, 0, 255).astype(np.uint8)

def leggi_nuvola(percorso, mantieni_colori, log):
    ext = Path(percorso).suffix.lower()
    log(f"Lettura {ext.upper()}...")
    if ext == ".e57":
        import e57 as _e
        d = _e.read_points(percorso)
        pos = np.asarray(d.points, dtype=np.float64)
        col = None
        if mantieni_colori:
            try:
                r = np.asarray(d.color, dtype=np.float32)
                if r.ndim==2 and r.shape[1]==3 and len(r)==len(pos):
                    col = _norm_col(r); log("  Colori RGB inclusi.")
            except: pass
    elif ext in (".las",".laz"):
        import laspy
        las = laspy.read(percorso)
        pos = np.column_stack([np.asarray(las.x,dtype=np.float64),
                               np.asarray(las.y,dtype=np.float64),
                               np.asarray(las.z,dtype=np.float64)])
        col = None
        if mantieni_colori and hasattr(las,"red"):
            col = _norm_col(np.column_stack([
                np.asarray(las.red,dtype=np.float32)/256,
                np.asarray(las.green,dtype=np.float32)/256,
                np.asarray(las.blue,dtype=np.float32)/256]))
            log("  Colori RGB inclusi.")
    elif ext == ".ply":
        from plyfile import PlyData
        p = PlyData.read(percorso); el = p["vertex"]
        pos = np.column_stack([np.asarray(el["x"],dtype=np.float64),
                               np.asarray(el["y"],dtype=np.float64),
                               np.asarray(el["z"],dtype=np.float64)])
        col = None
        if mantieni_colori:
            props = {pr.name for pr in el.properties}
            if {"red","green","blue"}.issubset(props):
                col = np.column_stack([np.asarray(el["red"],dtype=np.uint8),
                                       np.asarray(el["green"],dtype=np.uint8),
                                       np.asarray(el["blue"],dtype=np.uint8)])
                log("  Colori RGB inclusi.")
    elif ext in (".pts",".ptx"):
        rows = []
        with open(percorso,"r",errors="replace") as f:
            for line in f:
                p2 = line.strip().split()
                if len(p2)>=3 and not p2[0].isdigit():
                    try: rows.append([float(x) for x in p2[:7]])
                    except: pass
        arr = np.array(rows, dtype=np.float64)
        pos = arr[:,:3]
        col = _norm_col(arr[:,4:7].astype(np.float32)) if mantieni_colori and arr.shape[1]>=7 else None
        if col is not None: log("  Colori RGB inclusi.")
    elif ext in (".xyz",".txt",".csv"):
        import csv
        rows = []
        sep = "," if ext==".csv" else None
        with open(percorso,"r",errors="replace") as f:
            for line in f:
                p2 = line.strip().split(sep) if sep else line.strip().split()
                if len(p2)>=3:
                    try: rows.append([float(x) for x in p2[:6]])
                    except: pass
        arr = np.array(rows, dtype=np.float64)
        pos = arr[:,:3]
        col = _norm_col(arr[:,3:6].astype(np.float32)) if mantieni_colori and arr.shape[1]>=6 else None
        if col is not None: log("  Colori RGB inclusi.")
    else:
        raise ValueError(f"Formato non supportato: {ext}")
    if pos is None or len(pos)==0: raise ValueError("Nessun punto trovato.")
    return _filtra(pos, col, log)

def scrivi_nuvola(pos, colori, percorso, log):
    ext = Path(percorso).suffix.lower()
    Path(percorso).parent.mkdir(parents=True, exist_ok=True)
    log(f"Scrittura {ext.upper()}...")
    ha = colori is not None and len(colori)==len(pos)
    if ext in (".laz",".las"):
        import laspy
        h = laspy.LasHeader(point_format=7 if ha else 6, version="1.4")
        h.offsets = pos.mean(axis=0); h.scales = np.array([0.001,0.001,0.001])
        las = laspy.LasData(header=h)
        las.x=pos[:,0]; las.y=pos[:,1]; las.z=pos[:,2]
        if ha:
            las.red=colori[:,0].astype(np.uint16)*256
            las.green=colori[:,1].astype(np.uint16)*256
            las.blue=colori[:,2].astype(np.uint16)*256
        las.write(percorso)
    elif ext == ".ply":
        from plyfile import PlyData, PlyElement
        if ha:
            arr = np.zeros(len(pos),dtype=[("x","f4"),("y","f4"),("z","f4"),("red","u1"),("green","u1"),("blue","u1")])
            arr["red"]=colori[:,0]; arr["green"]=colori[:,1]; arr["blue"]=colori[:,2]
        else:
            arr = np.zeros(len(pos),dtype=[("x","f4"),("y","f4"),("z","f4")])
        arr["x"]=pos[:,0].astype(np.float32); arr["y"]=pos[:,1].astype(np.float32); arr["z"]=pos[:,2].astype(np.float32)
        PlyData([PlyElement.describe(arr,"vertex")],text=False).write(percorso)
    elif ext == ".pts":
        # PTS Leica: header conteggio + X Y Z [intensity R G B], scrittura vettoriale numpy
        with open(percorso,"w") as f:
            f.write(f"{len(pos)}\n")
        if ha:
            data = np.column_stack([pos, np.zeros(len(pos)), colori.astype(np.float64)])
            with open(percorso,"ab") as f:
                np.savetxt(f, data, fmt="%.6f %.6f %.6f %d %d %d %d")
        else:
            with open(percorso,"ab") as f:
                np.savetxt(f, pos, fmt="%.6f %.6f %.6f")
    elif ext == ".xyz":
        # XYZ: X Y Z [R G B], scrittura vettoriale numpy (molto piu' veloce dei cicli)
        if ha:
            data = np.column_stack([pos, colori.astype(np.float64)])
            np.savetxt(percorso, data, fmt="%.6f %.6f %.6f %d %d %d")
        else:
            np.savetxt(percorso, pos, fmt="%.6f %.6f %.6f")
    size = Path(percorso).stat().st_size/1024/1024
    log(f"Salvato: {percorso}  ({size:.1f} MB, {len(pos):,} punti)")

def decima_casuale(pos, col, perc, log):
    n = max(1, int(len(pos)*perc/100))
    log(f"  Casuale: {len(pos):,} -> {n:,} punti ({perc:.1f}%)")
    idx = np.random.choice(len(pos),n,replace=False); idx.sort()
    return pos[idx], (col[idx] if col is not None else None)

def decima_voxel(pos, col, mm, log, pct_fn):
    dm = mm/1000.0
    log(f"  Voxel {mm:.0f}mm...")
    minp = pos.min(axis=0)
    vox = ((pos-minp)/dm).astype(np.int32)
    CHUNK=1_000_000; cella={}
    for s in range(0,len(pos),CHUNK):
        e = min(s+CHUNK,len(pos))
        for j in range(s,e):
            k=(int(vox[j,0]),int(vox[j,1]),int(vox[j,2]))
            if k not in cella: cella[k]=j
        pct_fn(int(60+15*e/len(pos)))
    idx = np.array(list(cella.values()),dtype=np.int64); idx.sort()
    return pos[idx], (col[idx] if col is not None else None)

# ── THREADS ──────────────────────────────────────────────────

class NuvolaThread(QThread):
    progress=pyqtSignal(str); percent=pyqtSignal(int)
    done=pyqtSignal(str,int,int); error=pyqtSignal(str)
    def __init__(self,p): super().__init__(); self.p=p
    def run(self):
        p=self.p; ok=0; tot=len(p["files"])
        self.progress.emit("="*50)
        self.progress.emit(f"  Krill v3.2  |  {tot} file da elaborare")
        self.progress.emit("="*50)
        for i,inp in enumerate(p["files"]):
            self.progress.emit(f"\n[{i+1}/{tot}] {Path(inp).name}")
            try:
                pos,col = leggi_nuvola(inp, p["mantieni_colori"], self.progress.emit)
                self.progress.emit(f"  Punti: {len(pos):,}")
                self.percent.emit(int(100*i/tot)+5)
                if p["decimazione"]=="casuale":
                    pos,col = decima_casuale(pos,col,p["dec_val"],self.progress.emit)
                elif p["decimazione"]=="intelligente":
                    pos,col = decima_voxel(pos,col,p["dec_val"],self.progress.emit,self.percent.emit)
                ext = NUVOLA_OUTPUT_EXT[p["fmt"]]
                out_dir = p["out_dir"] or str(Path(inp).parent)
                out = safe_output_path(inp, out_dir, ext)
                scrivi_nuvola(pos,col,out,self.progress.emit)
                ok+=1
            except Exception as e:
                self.progress.emit(f"  ERRORE: {e}")
            self.percent.emit(int(100*(i+1)/tot))
        self.done.emit(f"{ok}/{tot} file convertiti con successo.",ok,tot)

class MeshThread(QThread):
    progress=pyqtSignal(str); percent=pyqtSignal(int)
    done=pyqtSignal(str,int,int); error=pyqtSignal(str)
    def __init__(self,p): super().__init__(); self.p=p
    def run(self):
        import trimesh
        p=self.p; ok=0; tot=len(p["files"])
        self.progress.emit("="*50)
        self.progress.emit(f"  Krill v3.2  |  {tot} mesh da elaborare")
        self.progress.emit("="*50)
        for i,inp in enumerate(p["files"]):
            self.progress.emit(f"\n[{i+1}/{tot}] {Path(inp).name}")
            try:
                mesh = trimesh.load(inp, force="mesh")
                if isinstance(mesh, trimesh.Scene):
                    mesh = trimesh.util.concatenate(
                        [g for g in mesh.geometry.values() if isinstance(g,trimesh.Trimesh)])
                if not isinstance(mesh, trimesh.Trimesh):
                    raise ValueError("Impossibile caricare la mesh.")
                nf = len(mesh.faces)
                self.progress.emit(f"  Facce: {nf:,}  Vertici: {len(mesh.vertices):,}")
                self.percent.emit(int(100*i/tot)+20)
                if p["decimazione"] and p["dec_perc"]<100:
                    reduction = max(0.01, min(0.99, 1.0-p["dec_perc"]/100.0))
                    target = max(4, int(nf*p["dec_perc"]/100))
                    self.progress.emit(f"  Decimazione: {nf:,} -> ~{target:,} facce ({p['dec_perc']:.0f}%)")
                    mesh = mesh.simplify_quadric_decimation(percent=reduction)
                    self.progress.emit(f"  Risultato: {len(mesh.faces):,} facce")
                ext = MESH_OUTPUT_EXT[p["fmt"]]
                out_dir = p["out_dir"] or str(Path(inp).parent)
                out = safe_output_path(inp, out_dir, ext)
                Path(out).parent.mkdir(parents=True,exist_ok=True)
                mesh.export(out)
                size = Path(out).stat().st_size/1024/1024
                self.progress.emit(f"  Salvato: {out}  ({size:.1f} MB)")
                ok+=1
            except Exception as e:
                self.progress.emit(f"  ERRORE: {e}\n{traceback.format_exc()[:300]}")
            self.percent.emit(int(100*(i+1)/tot))
        self.done.emit(f"{ok}/{tot} file convertiti con successo.",ok,tot)

# ── HELPERS UI ───────────────────────────────────────────────

def _sep(lay):
    f=QFrame(); f.setObjectName("sep"); f.setFixedHeight(1); lay.addWidget(f)

def _hint(text):
    l=QLabel(text); l.setObjectName("lbl_hint"); return l

class DropList(QListWidget):
    """Lista file con segnaposto quando e' vuota e stato di drag evidenziato."""
    PLACEHOLDER = "Trascina qui i file\noppure usa  + Aggiungi"
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(90)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.setAcceptDrops(False)
        self.setTextElideMode(Qt.ElideMiddle)
        self.setProperty("dragActive", False)
    def set_drag(self, on):
        self.setProperty("dragActive", on)
        self.style().unpolish(self); self.style().polish(self)
    def paths(self):
        return [self.item(i).data(Qt.UserRole) for i in range(self.count())]
    def add_path(self, p):
        if p in self.paths(): return
        it = QListWidgetItem(Path(p).name)
        it.setData(Qt.UserRole, p); it.setToolTip(p)
        self.addItem(it)
    def paintEvent(self, e):
        super().paintEvent(e)
        if self.count(): return
        pt = QPainter(self.viewport())
        pt.setPen(QColor(THEMES[self.window().property("theme") or "light"]["faint"]))
        pt.drawText(self.viewport().rect(), Qt.AlignCenter, self.PLACEHOLDER)

def _slider_box(preset, default_idx, spin, lbl, left_txt, right_txt):
    """Slider a preset con etichetta valore, estremi e nomi dei preset."""
    sl = QSlider(Qt.Horizontal)
    sl.setRange(0,len(preset)-1); sl.setValue(default_idx)
    sl.setTickPosition(QSlider.TicksBelow); sl.setTickInterval(1)
    def _sl(v):
        val,txt = preset[v]
        spin.blockSignals(True); spin.setValue(val); spin.blockSignals(False)
        lbl.setText(txt)
    def _sp(v):
        dists=[abs(v-p[0]) for p in preset]
        sl.blockSignals(True); sl.setValue(dists.index(min(dists))); sl.blockSignals(False)
        lbl.setText(f"Personalizzata ({int(v)})")
    sl.valueChanged.connect(_sl)
    spin.valueChanged.connect(_sp)

    lbl.setObjectName("lbl_accent")
    ends = QHBoxLayout(); ends.addWidget(_hint(left_txt)); ends.addStretch(); ends.addWidget(_hint(right_txt))
    names = QHBoxLayout()
    for _,e in preset:
        l=_hint(e.split("(")[0].strip()); l.setAlignment(Qt.AlignCenter); names.addWidget(l)
    box = QGroupBox(); box.setObjectName("slider_box")
    bl = QVBoxLayout(box); bl.setContentsMargins(10,8,10,8); bl.setSpacing(4)
    bl.addWidget(lbl); bl.addWidget(sl); bl.addLayout(ends); bl.addLayout(names)
    return sl, box

# ── TAB BASE (lista file + destinazione) ─────────────────────

class TabBase(QWidget):
    EXTS = set(); INPUT_FILTER = ""; OUT_FORMATS = []; DEFAULT_FMT = None; DIALOG_TITLE = ""

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        sa = QScrollArea(); sa.setWidgetResizable(True); sa.setFrameShape(QFrame.NoFrame)
        inner = QWidget(); inner.setObjectName("tab_inner"); sa.setWidget(inner); outer.addWidget(sa)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(14,14,14,14); lay.setSpacing(10)
        self._build_files(lay)
        self._build_output(lay)
        self._build_options(lay)
        lay.addStretch()

    def _build_files(self, lay):
        grp = QGroupBox("File sorgenti")
        gl = QVBoxLayout(grp); gl.setSpacing(8)
        self.lst = DropList(); gl.addWidget(self.lst)
        br = QHBoxLayout()
        for txt,fn in [("+  Aggiungi",self._aggiungi),("−  Rimuovi",self._rimuovi),("Svuota",self.lst.clear)]:
            b=QPushButton(txt); b.clicked.connect(fn); br.addWidget(b)
        br.addStretch()
        self.lbl_count = QLabel(); self.lbl_count.setObjectName("lbl_count"); br.addWidget(self.lbl_count)
        gl.addLayout(br); lay.addWidget(grp)
        m = self.lst.model()
        for sig in (m.rowsInserted, m.rowsRemoved, m.modelReset): sig.connect(self._update_count)
        self._update_count()

    def _build_output(self, lay):
        grp = QGroupBox("Destinazione e formato")
        gl = QVBoxLayout(grp); gl.setSpacing(6)
        row = QHBoxLayout()
        self.txt_out = QLineEdit()
        self.txt_out.setPlaceholderText("Stessa cartella del file sorgente (default)")
        self.cmb_fmt = QComboBox(); self.cmb_fmt.addItems(self.OUT_FORMATS); self.cmb_fmt.setFixedWidth(80)
        if self.DEFAULT_FMT: self.cmb_fmt.setCurrentText(self.DEFAULT_FMT)
        self.cmb_fmt.setToolTip("Formato di output")
        b = QPushButton("Sfoglia…"); b.clicked.connect(self._scegli_dir)
        row.addWidget(self.txt_out, 1); row.addWidget(self.cmb_fmt); row.addWidget(b)
        gl.addLayout(row)
        lh = QLabel("Se la cartella coincide con quella sorgente, il file viene salvato con suffisso _krill.")
        lh.setObjectName("lbl_info"); lh.setWordWrap(True); gl.addWidget(lh)
        lay.addWidget(grp)

    def _build_options(self, lay):
        raise NotImplementedError

    def _update_count(self, *_):
        n = self.lst.count()
        self.lbl_count.setText("Nessun file" if n==0 else f"{n} file")

    # Drag & drop
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls(): self.lst.set_drag(True); e.acceptProposedAction()
    def dragMoveEvent(self,e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
    def dragLeaveEvent(self,e):
        self.lst.set_drag(False)
    def dropEvent(self,e):
        self.lst.set_drag(False)
        for url in e.mimeData().urls():
            p=url.toLocalFile()
            if Path(p).suffix.lower().lstrip(".") in self.EXTS: self.lst.add_path(p)
        e.acceptProposedAction()

    def _aggiungi(self):
        paths,_=QFileDialog.getOpenFileNames(self,self.DIALOG_TITLE,"",self.INPUT_FILTER)
        for p in paths: self.lst.add_path(p)
    def _rimuovi(self):
        for it in self.lst.selectedItems(): self.lst.takeItem(self.lst.row(it))
    def _scegli_dir(self):
        d=QFileDialog.getExistingDirectory(self,"Cartella destinazione",self.txt_out.text() or "")
        if d: self.txt_out.setText(d)

    def _common_options(self):
        return dict(files=self.lst.paths(), fmt=self.cmb_fmt.currentText(),
                    out_dir=self.txt_out.text().strip() or None)
    def valida(self):
        if self.lst.count()==0: return "Aggiungi almeno un file sorgente."
        return None

# ── TAB NUVOLE ───────────────────────────────────────────────

class TabNuvole(TabBase):
    EXTS = {"e57","las","laz","ply","pts","ptx","xyz","txt","csv"}
    INPUT_FILTER = NUVOLA_INPUT_FILTER; OUT_FORMATS = NUVOLA_OUTPUT_FORMATS
    DEFAULT_FMT = "LAZ"; DIALOG_TITLE = "Seleziona nuvole"

    def _build_options(self, lay):
        grp = QGroupBox("Opzioni"); ol = QVBoxLayout(grp); ol.setSpacing(8)
        self.chk_col = QCheckBox("Mantieni colori RGB"); self.chk_col.setChecked(True); ol.addWidget(self.chk_col)
        _sep(ol)
        lbl_d = QLabel("Decimazione"); lbl_d.setObjectName("lbl_section"); ol.addWidget(lbl_d)
        self.bg = QButtonGroup(self)
        self.rb_no  = QRadioButton("Nessuna")
        self.rb_cas = QRadioButton("Casuale  —  riduci a una percentuale del totale")
        self.rb_int = QRadioButton("Intelligente  —  preserva il dettaglio geometrico")
        self.rb_no.setChecked(True)
        for rb in (self.rb_no,self.rb_cas,self.rb_int): self.bg.addButton(rb); ol.addWidget(rb)

        # Casuale
        self.pan_cas = QWidget()
        pc = QFormLayout(self.pan_cas); pc.setSpacing(6); pc.setContentsMargins(0,4,0,0)
        self.spin_p = QDoubleSpinBox(); self.spin_p.setRange(0.1,99.9); self.spin_p.setValue(20); self.spin_p.setDecimals(1); self.spin_p.setSuffix("  %"); self.spin_p.setSingleStep(5)
        pc.addRow("Percentuale da mantenere:", self.spin_p)
        ol.addWidget(self.pan_cas)

        # Intelligente
        self.pan_int = QWidget()
        pi = QVBoxLayout(self.pan_int); pi.setSpacing(6); pi.setContentsMargins(0,4,0,0)
        lbl_ni = QLabel("Divide la nuvola in celle cubiche. Zone dense (spigoli) vengono preservate meglio delle superfici piane.")
        lbl_ni.setObjectName("lbl_info"); lbl_ni.setWordWrap(True); pi.addWidget(lbl_ni)
        form = QFormLayout(); form.setSpacing(6)
        self.spin_d = QDoubleSpinBox(); self.spin_d.setRange(1,500); self.spin_d.setValue(20); self.spin_d.setDecimals(0); self.spin_d.setSuffix("  mm"); self.spin_d.setSingleStep(5)
        form.addRow("Dimensione cella:", self.spin_d); pi.addLayout(form)
        preset = [(5,"Massima (5mm)"),(10,"Alta (10mm)"),(20,"Bilanciata (20mm)"),(50,"Leggera (50mm)"),(100,"Minima (100mm)")]
        self.sl_n, box = _slider_box(preset,2,self.spin_d,QLabel("Bilanciata (20mm)"),"◄ Più punti","Meno punti ►")
        pi.addWidget(box); ol.addWidget(self.pan_int)

        def _tog():
            self.pan_cas.setVisible(self.rb_cas.isChecked())
            self.pan_int.setVisible(self.rb_int.isChecked())
        for rb in (self.rb_no,self.rb_cas,self.rb_int): rb.toggled.connect(_tog)
        _tog(); lay.addWidget(grp)

    def get_options(self):
        if self.rb_cas.isChecked(): dec,val="casuale",self.spin_p.value()
        elif self.rb_int.isChecked(): dec,val="intelligente",self.spin_d.value()
        else: dec,val="nessuna",0
        return dict(self._common_options(), mantieni_colori=self.chk_col.isChecked(),
                    decimazione=dec, dec_val=val)

# ── TAB MESH ─────────────────────────────────────────────────

class TabMesh(TabBase):
    EXTS = {"stl","obj","ply","glb","gltf","dae","off"}
    INPUT_FILTER = MESH_INPUT_FILTER; OUT_FORMATS = MESH_OUTPUT_FORMATS
    DEFAULT_FMT = None; DIALOG_TITLE = "Seleziona mesh"

    def _build_options(self, lay):
        grp = QGroupBox("Opzioni"); ol = QVBoxLayout(grp); ol.setSpacing(8)
        self.chk_dec = QCheckBox("Abilita decimazione mesh"); ol.addWidget(self.chk_dec)
        self.lbl_nd = QLabel("Quadric Edge Collapse: riduce le facce preservando la forma. Le zone con più dettaglio (spigoli, curvature) mantengono più triangoli rispetto alle superfici piane.")
        self.lbl_nd.setObjectName("lbl_info"); self.lbl_nd.setWordWrap(True); ol.addWidget(self.lbl_nd)
        _sep(ol)
        form = QFormLayout(); form.setSpacing(6)
        self.spin_p = QDoubleSpinBox(); self.spin_p.setRange(1,99); self.spin_p.setValue(50); self.spin_p.setDecimals(0); self.spin_p.setSuffix("  %"); self.spin_p.setSingleStep(5)
        form.addRow("Facce da mantenere:", self.spin_p); ol.addLayout(form)
        preset = [(10,"Pesante (10%)"),(25,"Alta (25%)"),(50,"Bilanciata (50%)"),(75,"Leggera (75%)"),(90,"Minima (90%)")]
        self.sl_m, self.box_sl = _slider_box(preset,2,self.spin_p,QLabel("Bilanciata (50%)"),"◄ Decimazione massima","Decimazione minima ►")
        ol.addWidget(self.box_sl)
        def _tog(on):
            for w in (self.spin_p,self.sl_m,self.box_sl,self.lbl_nd): w.setEnabled(on)
        self.chk_dec.toggled.connect(_tog); _tog(False)
        lay.addWidget(grp)

    def get_options(self):
        return dict(self._common_options(), decimazione=self.chk_dec.isChecked(),
                    dec_perc=self.spin_p.value())

# ── ABOUT DIALOG ─────────────────────────────────────────────

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Informazioni")
        self.setFixedWidth(480)
        ico = Path(__file__).parent / "Krill.ico"
        if ico.exists(): self.setWindowIcon(QIcon(str(ico)))
        lay = QVBoxLayout(self); lay.setContentsMargins(24,20,24,16); lay.setSpacing(10)

        top = QHBoxLayout()
        if ico.exists():
            lbl_ico = QLabel()
            px = QPixmap(str(ico)).scaled(40,40,Qt.KeepAspectRatio,Qt.SmoothTransformation)
            lbl_ico.setPixmap(px); top.addWidget(lbl_ico); top.addSpacing(10)
        col = QVBoxLayout(); col.setSpacing(0)
        lt = QLabel("KRILL"); lt.setObjectName("lbl_title"); col.addWidget(lt)
        lv = QLabel("3D Converter  v3.2"); lv.setObjectName("lbl_hint"); col.addWidget(lv)
        top.addLayout(col); top.addStretch(); lay.addLayout(top)
        _sep(lay)

        copy = QLabel(
            "Il presente software, la sua architettura, logica e design "
            "sono opera originale di Luca Ferrari e sono protetti dalle "
            "leggi sul diritto d'autore.\n\n"
            "L'uso del software è libero e gratuito. La modifica, "
            "redistribuzione o reverse engineering, anche parziali, sono "
            "vietate senza esplicito consenso scritto dell'autore.")
        copy.setWordWrap(True); copy.setObjectName("lbl_copy")
        lay.addWidget(copy)
        _sep(lay)

        form = QFormLayout(); form.setSpacing(5); form.setContentsMargins(0,4,0,4)
        def _r(k,v,link=False):
            lk=QLabel(k); lk.setObjectName("lbl_key")
            if link:
                lval=QLabel(f"<a href='mailto:{v}' style='text-decoration:none;'>{v}</a>")
                lval.setOpenExternalLinks(True)
            else: lval=QLabel(v)
            form.addRow(lk,lval)
        _r("Autore","Luca Ferrari")
        _r("Versione","3.2")
        _r("Contatto","lukeferra90@gmail.com",link=True)
        _r("Copyright", chr(169)+" 2026 Luca Ferrari "+chr(8212)+" Tutti i diritti riservati")
        lay.addLayout(form)

        br=QHBoxLayout(); br.addStretch()
        ok=QPushButton("OK"); ok.setFixedWidth(80); ok.setDefault(True); ok.clicked.connect(self.accept)
        br.addWidget(ok); lay.addLayout(br)

# ── MAIN WINDOW ──────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Krill  —  3D Converter  v3.2")
        self.setMinimumSize(700,760); self.resize(740,960)
        self._settings = QSettings("Krill","Krill")
        self._thread=None
        self.setStyleSheet(build_stylesheet(self._initial_theme()))
        self._build_ui()
        self._apply_theme(self._initial_theme())
        ico=Path(__file__).parent/"Krill.ico"
        if ico.exists(): self.setWindowIcon(QIcon(str(ico)))

    def _initial_theme(self):
        t = self._settings.value("theme", "")
        if t in THEMES: return t
        # primo avvio: segue il tema di sistema
        return "dark" if QApplication.palette().color(QPalette.Window).lightness() < 128 else "light"

    def _apply_theme(self, theme):
        self.setProperty("theme", theme)
        self.setStyleSheet(build_stylesheet(theme))
        self.btn_theme.setText("☀" if theme=="dark" else "☾")
        self.btn_theme.setToolTip("Passa al tema chiaro" if theme=="dark" else "Passa al tema scuro")
        self.tab_n.lst.viewport().update(); self.tab_m.lst.viewport().update()

    def _toggle_theme(self):
        t = "light" if self.property("theme")=="dark" else "dark"
        self._apply_theme(t); self._settings.setValue("theme", t)

    def _build_ui(self):
        root=QWidget(); root.setObjectName("root"); self.setCentralWidget(root)
        lay=QVBoxLayout(root); lay.setContentsMargins(20,14,20,16); lay.setSpacing(10)

        hdr=QHBoxLayout(); hdr.setSpacing(10)
        ico=Path(__file__).parent/"Krill.ico"
        if ico.exists():
            li=QLabel(); li.setPixmap(QPixmap(str(ico)).scaled(30,30,Qt.KeepAspectRatio,Qt.SmoothTransformation)); hdr.addWidget(li)
        t=QLabel("KRILL"); t.setObjectName("lbl_title"); hdr.addWidget(t)
        s=QLabel("3D Converter  ·  v3.2"); s.setObjectName("lbl_subtitle"); hdr.addWidget(s, 0, Qt.AlignBottom)
        hdr.addStretch()
        self.btn_theme=QPushButton(); self.btn_theme.setObjectName("btn_icon"); self.btn_theme.setFixedSize(28,28)
        self.btn_theme.clicked.connect(self._toggle_theme); hdr.addWidget(self.btn_theme)
        btn_i=QPushButton("ⓘ"); btn_i.setFixedSize(28,28); btn_i.setToolTip("Informazioni")
        btn_i.setObjectName("btn_icon"); btn_i.clicked.connect(lambda: AboutDialog(self).exec_())
        hdr.addWidget(btn_i); lay.addLayout(hdr)

        self.tabs=QTabWidget()
        self.tabs.tabBar().setExpanding(False)
        f=self.tabs.tabBar().font(); f.setBold(True); self.tabs.tabBar().setFont(f)
        self.tab_n=TabNuvole(); self.tab_m=TabMesh()
        self.tabs.addTab(self.tab_n,"☁   Nuvole di punti")
        self.tabs.addTab(self.tab_m,"▲   Mesh 3D")
        lay.addWidget(self.tabs, 5)

        br=QHBoxLayout(); br.addStretch()
        self.btn_conv=QPushButton("▶  Converti"); self.btn_conv.setObjectName("btn_converti")
        self.btn_conv.setFixedHeight(44); self.btn_conv.setCursor(Qt.PointingHandCursor)
        self.btn_conv.clicked.connect(self._avvia)
        br.addWidget(self.btn_conv); br.addStretch(); lay.addLayout(br)

        self.pbar=QProgressBar(); self.pbar.setValue(0); self.pbar.setTextVisible(False); lay.addWidget(self.pbar)

        grp_log=QGroupBox("Log"); ll=QVBoxLayout(grp_log)
        self.log=QTextEdit(); self.log.setReadOnly(True); self.log.setMinimumHeight(70)
        ll.addWidget(self.log); lay.addWidget(grp_log, 1)

    def _append(self,msg):
        self.log.append(msg)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def _set_busy(self, busy):
        self.btn_conv.setEnabled(not busy)
        self.btn_conv.setText("Conversione in corso…" if busy else "▶  Converti")
        self.tabs.setEnabled(not busy)

    def _avvia(self):
        idx=self.tabs.currentIndex()
        tab = self.tab_n if idx==0 else self.tab_m
        err=tab.valida()
        if err: QMessageBox.warning(self,"Attenzione",err); return
        opts=tab.get_options()
        self.log.clear(); self.pbar.setValue(0); self._set_busy(True)
        self._thread = NuvolaThread(opts) if idx==0 else MeshThread(opts)
        self._thread.progress.connect(self._append)
        self._thread.percent.connect(self.pbar.setValue)
        self._thread.done.connect(self._on_done)
        self._thread.error.connect(self._on_error)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _on_done(self,msg,ok,tot):
        self._append(f"\n✔  {msg}")
        self._set_busy(False)
        if ok==tot: QMessageBox.information(self,"Completato",msg)
        else: QMessageBox.warning(self,"Completato con errori",msg+"\nControlla il log per i dettagli.")

    def _on_error(self,msg):
        self._append(f"\n✘  ERRORE:\n{msg}")
        self._set_busy(False)
        QMessageBox.critical(self,"Errore",msg[:800])

if __name__=="__main__":
    app=QApplication(sys.argv); app.setStyle("Fusion")
    win=MainWindow(); win.show(); sys.exit(app.exec_())
