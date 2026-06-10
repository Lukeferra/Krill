"""
Krill.py  v3.1
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
    QListWidget, QListWidgetItem, QAbstractItemView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap

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

STYLESHEET = """
* { font-family: "Segoe UI", sans-serif; font-size: 10pt; }
QMainWindow, QWidget { background: #f5f6f8; color: #2e3338; }

/* Tabs */
QTabWidget::pane { border: 1px solid #e2e5ea; border-radius: 8px; background: #ffffff; top: -1px; }
QTabBar::tab { background: transparent; color: #8a9099; padding: 9px 32px; border: none;
               border-bottom: 2px solid transparent; margin-right: 8px; font-weight: 600; }
QTabBar::tab:selected { color: #388e3c; border-bottom: 2px solid #388e3c; }
QTabBar::tab:hover:!selected { color: #5a616b; }

/* GroupBox */
QGroupBox { border: 1px solid #e2e5ea; border-radius: 8px; margin-top: 14px;
            padding: 14px 12px 12px 12px; font-weight: 600; color: #5a616b; background: #ffffff; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #6b7280; }

/* Pulsanti standard */
QPushButton { background: #ffffff; border: 1px solid #d4d8df; border-radius: 6px;
              padding: 7px 16px; color: #3a4047; }
QPushButton:hover { background: #f0f7f0; border-color: #388e3c; color: #388e3c; }
QPushButton:pressed { background: #e3efe3; }

/* Pulsante principale */
QPushButton#btn_converti { background: #388e3c; color: #ffffff; font-weight: 600;
                            font-size: 11pt; padding: 9px 28px; border: none; border-radius: 7px; }
QPushButton#btn_converti:hover { background: #2f7a33; }
QPushButton#btn_converti:pressed { background: #286b2b; }
QPushButton#btn_converti:disabled { background: #cfd3d9; color: #ffffff; }

/* Pulsante info */
QPushButton#btn_info { background: transparent; border: 1px solid #d4d8df; border-radius: 12px;
                        color: #a0a6ae; font-size: 13px; padding: 0; }
QPushButton#btn_info:hover { border-color: #388e3c; color: #388e3c; }

/* Input */
QLineEdit { background: #ffffff; border: 1px solid #d4d8df; border-radius: 6px;
            padding: 6px 10px; color: #2e3338; }
QLineEdit:focus { border-color: #388e3c; }

/* Log */
QTextEdit { background: #fbfbfc; border: 1px solid #e2e5ea; border-radius: 6px;
            color: #4a5058; font-family: "Consolas", monospace; font-size: 9pt; padding: 4px; }

/* ProgressBar */
QProgressBar { background: #eceef1; border: none; border-radius: 6px; height: 8px; text-align: center;
               color: transparent; }
QProgressBar::chunk { background: #388e3c; border-radius: 6px; }

/* Radio */
QRadioButton { color: #3a4047; spacing: 8px; padding: 2px 0; }
QRadioButton::indicator { width: 16px; height: 16px; border-radius: 9px;
                          border: 2px solid #c4c9d0; background: #ffffff; }
QRadioButton::indicator:checked { border: 5px solid #388e3c; background: #ffffff; }
QRadioButton::indicator:hover { border-color: #388e3c; }

/* Checkbox */
QCheckBox { color: #3a4047; spacing: 8px; padding: 2px 0; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px;
                       border: 2px solid #c4c9d0; background: #ffffff; }
QCheckBox::indicator:checked { background: #388e3c; border-color: #388e3c;
                               image: url(none); }
QCheckBox::indicator:hover { border-color: #388e3c; }

/* SpinBox / ComboBox */
QDoubleSpinBox, QSpinBox, QComboBox { background: #ffffff; border: 1px solid #d4d8df;
                                       border-radius: 6px; padding: 5px 8px; color: #2e3338; }
QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus { border-color: #388e3c; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView { background: #ffffff; color: #2e3338; border: 1px solid #d4d8df;
                              selection-background-color: #e3efe3; selection-color: #388e3c; outline: none; }
QDoubleSpinBox::up-button, QSpinBox::up-button,
QDoubleSpinBox::down-button, QSpinBox::down-button { width: 16px; border: none; background: transparent; }

/* Lista file */
QListWidget { background: #ffffff; border: 1px solid #d4d8df; border-radius: 6px;
              color: #3a4047; font-size: 9pt; padding: 2px; outline: none; }
QListWidget::item { padding: 4px 6px; border-radius: 4px; }
QListWidget::item:selected { background: #e3efe3; color: #388e3c; }
QListWidget::item:hover { background: #f0f7f0; }
QListWidget#drag_active { background: #f0f7f0; border: 2px dashed #388e3c; border-radius: 6px;
                          color: #3a4047; font-size: 9pt; padding: 1px; outline: none; }

/* Slider */
QSlider::groove:horizontal { background: #e2e5ea; height: 4px; border-radius: 2px; }
QSlider::handle:horizontal { background: #388e3c; width: 16px; height: 16px;
                             margin: -7px 0; border-radius: 8px; border: 2px solid #ffffff; }
QSlider::handle:horizontal:hover { background: #2f7a33; }
QSlider::sub-page:horizontal { background: #388e3c; border-radius: 2px; }

/* Scrollbar discreta */
QScrollBar:vertical { background: transparent; width: 8px; margin: 2px; }
QScrollBar::handle:vertical { background: #c4c9d0; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #a0a6ae; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; background: none; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
QScrollBar:horizontal { background: transparent; height: 8px; margin: 2px; }
QScrollBar::handle:horizontal { background: #c4c9d0; border-radius: 4px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: #a0a6ae; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; background: none; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

/* Etichette */
QLabel { color: #3a4047; }
QLabel#lbl_path { color: #9aa0a8; font-style: italic; }
QLabel#lbl_info { color: #6b7280; font-size: 9pt; }
QLabel#lbl_warn { color: #c77d3a; font-size: 9pt; }
QLabel#lbl_title { color: #388e3c; }
QLabel#lbl_subtitle { color: #9aa0a8; }
QLabel#lbl_accent { color: #388e3c; font-weight: 600; }
"""

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
        self.progress.emit(f"  Krill v3.1  |  {tot} file da elaborare")
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
        self.progress.emit(f"  Krill v3.1  |  {tot} mesh da elaborare")
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
    f=QFrame(); f.setFrameShape(QFrame.HLine); f.setStyleSheet("color:#e2e5ea;"); lay.addWidget(f)

def _make_list():
    lst = QListWidget()
    lst.setMinimumHeight(70)
    lst.setSelectionMode(QAbstractItemView.ExtendedSelection)
    lst.setDragDropMode(QAbstractItemView.NoDragDrop)
    lst.setAcceptDrops(False)
    return lst

def _make_slider(preset, default_idx, spin, lbl):
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
    return sl

# ── TAB NUVOLE ───────────────────────────────────────────────

class TabNuvole(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12,12,12,12); lay.setSpacing(10)

        # File list
        grp_in = QGroupBox("File sorgenti  (trascina qui i file o usa Aggiungi)")
        gl = QVBoxLayout(grp_in)
        self.lst = _make_list(); gl.addWidget(self.lst)
        br = QHBoxLayout()
        for txt,fn in [("+ Aggiungi",self._aggiungi),("- Rimuovi",self._rimuovi),("Svuota",self.lst.clear)]:
            b=QPushButton(txt); b.clicked.connect(fn); br.addWidget(b)
        gl.addLayout(br); lay.addWidget(grp_in)

        # Output dir
        grp_out = QGroupBox("Cartella di destinazione")
        ol = QHBoxLayout(grp_out)
        self.txt_out = QLineEdit()
        self.txt_out.setPlaceholderText("Stessa cartella del file sorgente (default)...")
        self.txt_out.setObjectName("lbl_path")
        self.cmb_fmt = QComboBox(); self.cmb_fmt.addItems(NUVOLA_OUTPUT_FORMATS); self.cmb_fmt.setFixedWidth(70)
        self.cmb_fmt.setCurrentText("LAZ")
        b_out = QPushButton("Sfoglia..."); b_out.clicked.connect(self._scegli_dir)
        ol.addWidget(self.txt_out); ol.addWidget(self.cmb_fmt); ol.addWidget(b_out)
        lay.addWidget(grp_out)

        lh = QLabel("Se la cartella coincide con quella sorgente, il file viene salvato con suffisso _krill.")
        lh.setObjectName("lbl_info"); lh.setWordWrap(True); lay.addWidget(lh)

        # Opzioni
        grp_opt = QGroupBox("Opzioni"); ol2 = QVBoxLayout(grp_opt); ol2.setSpacing(8)
        self.chk_col = QCheckBox("Mantieni colori RGB"); self.chk_col.setChecked(True); ol2.addWidget(self.chk_col)
        _sep(ol2)
        lbl_d = QLabel("Decimazione:"); lbl_d.setStyleSheet("font-weight:600;color:#388e3c;"); ol2.addWidget(lbl_d)
        self.bg = QButtonGroup(self)
        self.rb_no  = QRadioButton("Nessuna")
        self.rb_cas = QRadioButton("Casuale  \u2014  riduci a una percentuale del totale")
        self.rb_int = QRadioButton("Intelligente  \u2014  preserva il dettaglio geometrico")
        self.rb_no.setChecked(True)
        for rb in (self.rb_no,self.rb_cas,self.rb_int): self.bg.addButton(rb); ol2.addWidget(rb)
        self.lbl_ni = QLabel("Divide la nuvola in celle cubiche. Zone dense (spigoli) vengono preservate meglio delle superfici piane.")
        self.lbl_ni.setObjectName("lbl_info"); self.lbl_ni.setWordWrap(True); self.lbl_ni.setVisible(False); ol2.addWidget(self.lbl_ni)
        self.rb_int.toggled.connect(lambda on: self.lbl_ni.setVisible(on))
        _sep(ol2)

        # Pannello CASUALE
        self.pan_cas = QWidget()
        pc = QFormLayout(self.pan_cas); pc.setSpacing(6); pc.setContentsMargins(0,0,0,0)
        self.spin_p = QDoubleSpinBox(); self.spin_p.setRange(0.1,99.9); self.spin_p.setValue(20); self.spin_p.setDecimals(1); self.spin_p.setSuffix("  %"); self.spin_p.setSingleStep(5)
        pc.addRow("Percentuale da mantenere:", self.spin_p)
        ol2.addWidget(self.pan_cas)

        # Pannello INTELLIGENTE
        self.pan_int = QWidget()
        pi = QVBoxLayout(self.pan_int); pi.setSpacing(6); pi.setContentsMargins(0,0,0,0)
        form_i = QFormLayout(); form_i.setSpacing(6)
        self.spin_d = QDoubleSpinBox(); self.spin_d.setRange(1,500); self.spin_d.setValue(20); self.spin_d.setDecimals(0); self.spin_d.setSuffix("  mm"); self.spin_d.setSingleStep(5)
        form_i.addRow("Dimensione cella:", self.spin_d)
        pi.addLayout(form_i)
        preset_n = [(5,"Massima (5mm)"),(10,"Alta (10mm)"),(20,"Bilanciata (20mm)"),(50,"Leggera (50mm)"),(100,"Minima (100mm)")]
        self.lbl_q = QLabel("Bilanciata (20mm)"); self.lbl_q.setStyleSheet("color:#388e3c;font-weight:600;")
        self.sl_n = _make_slider(preset_n,2,self.spin_d,self.lbl_q)
        lbr = QHBoxLayout(); ll=QLabel("\u25c4 Pi\u00f9 punti"); lr=QLabel("Meno punti \u25ba")
        for l in (ll,lr): l.setStyleSheet("color:#9aa0a8;font-size:8pt;")
        lbr.addWidget(ll); lbr.addStretch(); lbr.addWidget(lr)
        prow = QHBoxLayout()
        for _,e in preset_n:
            n=e.split("(")[0].strip(); l=QLabel(n); l.setStyleSheet("color:#9aa0a8;font-size:8pt;"); l.setAlignment(Qt.AlignCenter); prow.addWidget(l)
        grp_sl = QGroupBox(); grp_sl.setStyleSheet("QGroupBox{border:1px solid #e2e5ea;border-radius:6px;padding:8px;margin-top:4px;background:#fbfbfc;}")
        gsl = QVBoxLayout(grp_sl); gsl.setContentsMargins(8,6,8,6)
        gsl.addWidget(self.lbl_q); gsl.addWidget(self.sl_n); gsl.addLayout(lbr); gsl.addLayout(prow)
        pi.addWidget(grp_sl)
        ol2.addWidget(self.pan_int)

        def _tog():
            self.pan_cas.setVisible(self.rb_cas.isChecked())
            self.pan_int.setVisible(self.rb_int.isChecked())
        for rb in (self.rb_no,self.rb_cas,self.rb_int): rb.toggled.connect(_tog)
        _tog(); lay.addWidget(grp_opt)
        lay.setStretchFactor(grp_opt, 1)

    def _set_drag(self, active):
        self.lst.setObjectName("drag_active" if active else "")
        self.lst.style().unpolish(self.lst); self.lst.style().polish(self.lst)
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls(): self._set_drag(True); e.acceptProposedAction()
    def dragMoveEvent(self,e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
    def dragLeaveEvent(self,e):
        self._set_drag(False)
    def dropEvent(self,e):
        self._set_drag(False)
        exts={"e57","las","laz","ply","pts","ptx","xyz","txt","csv"}
        for url in e.mimeData().urls():
            p=url.toLocalFile()
            if Path(p).suffix.lower().lstrip(".") in exts: self._add(p)
        e.acceptProposedAction()

    def _add(self,p):
        ex=[self.lst.item(i).text() for i in range(self.lst.count())]
        if p not in ex: self.lst.addItem(p)
    def _aggiungi(self):
        paths,_=QFileDialog.getOpenFileNames(self,"Seleziona nuvole","",NUVOLA_INPUT_FILTER)
        for p in paths: self._add(p)
    def _rimuovi(self):
        for it in self.lst.selectedItems(): self.lst.takeItem(self.lst.row(it))
    def _scegli_dir(self):
        d=QFileDialog.getExistingDirectory(self,"Cartella destinazione",self.txt_out.text() or "")
        if d: self.txt_out.setText(d)

    def get_options(self):
        if self.rb_cas.isChecked(): dec,val="casuale",self.spin_p.value()
        elif self.rb_int.isChecked(): dec,val="intelligente",self.spin_d.value()
        else: dec,val="nessuna",0
        return dict(files=[self.lst.item(i).text() for i in range(self.lst.count())],
                    fmt=self.cmb_fmt.currentText(),
                    out_dir=self.txt_out.text().strip() or None,
                    mantieni_colori=self.chk_col.isChecked(),
                    decimazione=dec, dec_val=val)
    def valida(self):
        if self.lst.count()==0: return "Aggiungi almeno un file sorgente."
        return None

# ── TAB MESH ─────────────────────────────────────────────────

class TabMesh(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self); lay.setContentsMargins(12,12,12,12); lay.setSpacing(10)

        # File list
        grp_in = QGroupBox("File sorgenti  (trascina qui i file o usa Aggiungi)")
        gl = QVBoxLayout(grp_in)
        self.lst = _make_list(); gl.addWidget(self.lst)
        br = QHBoxLayout()
        for txt,fn in [("+ Aggiungi",self._aggiungi),("- Rimuovi",self._rimuovi),("Svuota",self.lst.clear)]:
            b=QPushButton(txt); b.clicked.connect(fn); br.addWidget(b)
        gl.addLayout(br); lay.addWidget(grp_in)

        # Output dir
        grp_out = QGroupBox("Cartella di destinazione")
        ol = QHBoxLayout(grp_out)
        self.txt_out = QLineEdit(); self.txt_out.setPlaceholderText("Stessa cartella del file sorgente (default)..."); self.txt_out.setObjectName("lbl_path")
        self.cmb_fmt = QComboBox(); self.cmb_fmt.addItems(MESH_OUTPUT_FORMATS); self.cmb_fmt.setFixedWidth(70)
        b_out = QPushButton("Sfoglia..."); b_out.clicked.connect(self._scegli_dir)
        ol.addWidget(self.txt_out); ol.addWidget(self.cmb_fmt); ol.addWidget(b_out)
        lay.addWidget(grp_out)
        lh = QLabel("Se la cartella coincide con quella sorgente, il file viene salvato con suffisso _krill.")
        lh.setObjectName("lbl_info"); lh.setWordWrap(True); lay.addWidget(lh)

        # Opzioni
        grp_opt = QGroupBox("Opzioni"); ol2 = QVBoxLayout(grp_opt); ol2.setSpacing(8)
        self.chk_dec = QCheckBox("Abilita decimazione mesh"); self.chk_dec.setChecked(False); ol2.addWidget(self.chk_dec)
        self.lbl_nd = QLabel("Quadric Edge Collapse: riduce le facce preservando la forma. Le zone con piu' dettaglio (spigoli, curvature) mantengono piu' triangoli rispetto alle superfici piane.")
        self.lbl_nd.setObjectName("lbl_info"); self.lbl_nd.setWordWrap(True); ol2.addWidget(self.lbl_nd)
        _sep(ol2)
        form = QFormLayout(); form.setSpacing(6)
        self.spin_p = QDoubleSpinBox(); self.spin_p.setRange(1,99); self.spin_p.setValue(50); self.spin_p.setDecimals(0); self.spin_p.setSuffix("  %"); self.spin_p.setSingleStep(5)
        form.addRow("Facce da mantenere:", self.spin_p); ol2.addLayout(form)
        preset_m = [(10,"Pesante (10%)"),(25,"Alta (25%)"),(50,"Bilanciata (50%)"),(75,"Leggera (75%)"),(90,"Minima (90%)")]
        self.lbl_q = QLabel("Bilanciata (50%)"); self.lbl_q.setStyleSheet("color:#388e3c;font-weight:600;")
        self.sl_m = _make_slider(preset_m,2,self.spin_p,self.lbl_q)
        lbr = QHBoxLayout(); ll=QLabel("\u25c4 Decimazione massima"); lr=QLabel("Decimazione minima \u25ba")
        for l in (ll,lr): l.setStyleSheet("color:#9aa0a8;font-size:8pt;")
        lbr.addWidget(ll); lbr.addStretch(); lbr.addWidget(lr)
        prow = QHBoxLayout()
        for _,e in preset_m:
            n=e.split("(")[0].strip(); l=QLabel(n); l.setStyleSheet("color:#9aa0a8;font-size:8pt;"); l.setAlignment(Qt.AlignCenter); prow.addWidget(l)
        self.grp_sl = QGroupBox(); self.grp_sl.setStyleSheet("QGroupBox{border:1px solid #e2e5ea;border-radius:6px;padding:8px;margin-top:0;background:#fbfbfc;}")
        gsl = QVBoxLayout(self.grp_sl); gsl.setContentsMargins(8,6,8,6)
        gsl.addWidget(self.lbl_q); gsl.addWidget(self.sl_m); gsl.addLayout(lbr); gsl.addLayout(prow)
        ol2.addWidget(self.grp_sl)
        def _tog(on):
            self.spin_p.setEnabled(on); self.sl_m.setEnabled(on)
            self.grp_sl.setEnabled(on)
            self.lbl_nd.setStyleSheet("color:#6b7280;font-size:9pt;" if on else "color:#c4c9d0;font-size:9pt;")
        self.chk_dec.toggled.connect(_tog); _tog(False); lay.addWidget(grp_opt)
        lay.setStretchFactor(grp_opt, 1)

    def _set_drag(self, active):
        self.lst.setObjectName("drag_active" if active else "")
        self.lst.style().unpolish(self.lst); self.lst.style().polish(self.lst)
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls(): self._set_drag(True); e.acceptProposedAction()
    def dragMoveEvent(self,e):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
    def dragLeaveEvent(self,e):
        self._set_drag(False)
    def dropEvent(self,e):
        self._set_drag(False)
        exts={"stl","obj","ply","glb","gltf","dae","off"}
        for url in e.mimeData().urls():
            p=url.toLocalFile()
            if Path(p).suffix.lower().lstrip(".") in exts: self._add(p)
        e.acceptProposedAction()

    def _add(self,p):
        ex=[self.lst.item(i).text() for i in range(self.lst.count())]
        if p not in ex: self.lst.addItem(p)
    def _aggiungi(self):
        paths,_=QFileDialog.getOpenFileNames(self,"Seleziona mesh","",MESH_INPUT_FILTER)
        for p in paths: self._add(p)
    def _rimuovi(self):
        for it in self.lst.selectedItems(): self.lst.takeItem(self.lst.row(it))
    def _scegli_dir(self):
        d=QFileDialog.getExistingDirectory(self,"Cartella destinazione",self.txt_out.text() or "")
        if d: self.txt_out.setText(d)

    def get_options(self):
        return dict(files=[self.lst.item(i).text() for i in range(self.lst.count())],
                    fmt=self.cmb_fmt.currentText(),
                    out_dir=self.txt_out.text().strip() or None,
                    decimazione=self.chk_dec.isChecked(),
                    dec_perc=self.spin_p.value())
    def valida(self):
        if self.lst.count()==0: return "Aggiungi almeno un file sorgente."
        return None

# ── ABOUT DIALOG ─────────────────────────────────────────────

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Informazioni")
        self.setFixedWidth(480)
        self.setStyleSheet(
            "QDialog{background:#f5f6f8;}"
            "QLabel{color:#3a4047;font-family:'Segoe UI';font-size:9pt;background:transparent;}"
            "QPushButton{background:#ffffff;border:1px solid #d4d8df;"
            "border-radius:6px;padding:6px 20px;color:#3a4047;}"
            "QPushButton:hover{background:#f0f7f0;border-color:#388e3c;color:#388e3c;}")
        ico = Path(__file__).parent / "Krill.ico"
        if ico.exists(): self.setWindowIcon(QIcon(str(ico)))
        lay = QVBoxLayout(self); lay.setContentsMargins(24,20,24,16); lay.setSpacing(8)

        # Header con icona
        top = QHBoxLayout()
        if ico.exists():
            lbl_ico = QLabel()
            px = QPixmap(str(ico)).scaled(36,36,Qt.KeepAspectRatio,Qt.SmoothTransformation)
            lbl_ico.setPixmap(px); top.addWidget(lbl_ico); top.addSpacing(10)
        col = QVBoxLayout()
        lt = QLabel("K R I L L"); lt.setFont(QFont("Segoe UI",13,QFont.Bold)); lt.setStyleSheet("color:#388e3c;"); col.addWidget(lt)
        lv = QLabel("3D Converter  v3.1"); lv.setStyleSheet("color:#9aa0a8;font-size:8pt;"); col.addWidget(lv)
        top.addLayout(col); top.addStretch(); lay.addLayout(top)

        s1=QFrame(); s1.setFrameShape(QFrame.HLine); s1.setStyleSheet("color:#e2e5ea;"); lay.addWidget(s1)

        # Testo copyright come QLabel (no sfondo, wrap pulito)
        copy = QLabel(
            "Il presente software, la sua architettura, logica e design "
            "sono opera originale di Luca Ferrari e sono protetti dalle "
            "leggi sul diritto d'autore.\n\n"
            "L'uso del software \u00e8 libero e gratuito. La modifica, "
            "redistribuzione o reverse engineering, anche parziali, sono "
            "vietate senza esplicito consenso scritto dell'autore.")
        copy.setWordWrap(True)
        copy.setStyleSheet("color:#5a616b;font-size:9pt;line-height:1.5;")
        lay.addWidget(copy)

        s2=QFrame(); s2.setFrameShape(QFrame.HLine); s2.setStyleSheet("color:#e2e5ea;"); lay.addWidget(s2)

        form = QFormLayout(); form.setSpacing(5); form.setContentsMargins(0,6,0,6)
        def _r(k,v,link=False):
            lk=QLabel(k); lk.setStyleSheet("color:#9aa0a8;")
            if link:
                lval=QLabel("<a href='mailto:{0}' style='color:#388e3c;text-decoration:none;'>{0}</a>".format(v))
                lval.setOpenExternalLinks(True)
            else: lval=QLabel(v)
            form.addRow(lk,lval)
        _r("Autore","Luca Ferrari")
        _r("Versione","3.1")
        _r("Contatto","lukeferra90@gmail.com",link=True)
        _r("Copyright", chr(169)+" 2026 Luca Ferrari "+chr(8212)+" Tutti i diritti riservati")
        lay.addLayout(form)

        br=QHBoxLayout(); br.addStretch()
        ok=QPushButton("OK"); ok.setFixedWidth(80); ok.clicked.connect(self.accept)
        br.addWidget(ok); lay.addLayout(br)

# ── MAIN WINDOW ──────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Krill  \u2014  3D Converter  v3.1")
        self.setMinimumSize(700,920); self.resize(720,960)
        self.setStyleSheet(STYLESHEET)
        self._thread=None
        self._build_ui()
        ico=Path(__file__).parent/"Krill.ico"
        if ico.exists(): self.setWindowIcon(QIcon(str(ico)))

    def _build_ui(self):
        root=QWidget(); self.setCentralWidget(root)
        lay=QVBoxLayout(root); lay.setContentsMargins(18,12,18,14); lay.setSpacing(8)

        # Header compatto su una riga
        hdr=QHBoxLayout(); hdr.setSpacing(8)
        t=QLabel("KRILL"); t.setFont(QFont("Segoe UI",16,QFont.Bold))
        t.setObjectName("lbl_title")
        hdr.addWidget(t)
        s=QLabel("3D Converter"); s.setFont(QFont("Segoe UI",10))
        s.setObjectName("lbl_subtitle"); s.setStyleSheet("padding-top:6px;")
        hdr.addWidget(s)
        hdr.addStretch()
        ver=QLabel("v3.1"); ver.setObjectName("lbl_subtitle"); ver.setStyleSheet("padding-top:7px;font-size:9pt;")
        hdr.addWidget(ver)
        btn_i=QPushButton("\u24d8"); btn_i.setFixedSize(24,24); btn_i.setToolTip("Informazioni")
        btn_i.setObjectName("btn_info")
        btn_i.clicked.connect(lambda: AboutDialog(self).exec_())
        hdr.addWidget(btn_i); lay.addLayout(hdr)

        # Tabs
        self.tabs=QTabWidget()
        self.tabs.setMinimumHeight(560)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.tabBar().setDocumentMode(False)
        self.tab_n=TabNuvole(); self.tab_m=TabMesh()
        self.tabs.addTab(self.tab_n,"\u2601   Nuvole di punti")
        self.tabs.addTab(self.tab_m,"\u25b2   Mesh 3D")
        lay.addWidget(self.tabs)
        lay.setStretchFactor(self.tabs, 3)

        # Converti
        br=QHBoxLayout(); br.addStretch()
        self.btn_conv=QPushButton("\u25b6  Converti"); self.btn_conv.setObjectName("btn_converti")
        self.btn_conv.setFixedHeight(42); self.btn_conv.clicked.connect(self._avvia)
        br.addWidget(self.btn_conv); br.addStretch(); lay.addLayout(br)

        self.pbar=QProgressBar(); self.pbar.setValue(0); lay.addWidget(self.pbar)

        grp_log=QGroupBox("Log"); ll=QVBoxLayout(grp_log)
        self.log=QTextEdit(); self.log.setReadOnly(True); self.log.setMinimumHeight(80)
        self.log.setStyleSheet("QTextEdit{font-size:8pt;}")
        ll.addWidget(self.log); lay.addWidget(grp_log)
        lay.setStretchFactor(grp_log, 1)

    def _append(self,msg):
        self.log.append(msg)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def _avvia(self):
        idx=self.tabs.currentIndex()
        tab = self.tab_n if idx==0 else self.tab_m
        err=tab.valida()
        if err: QMessageBox.warning(self,"Attenzione",err); return
        opts=tab.get_options()
        self.log.clear(); self.pbar.setValue(0); self.btn_conv.setEnabled(False)
        self._thread = NuvolaThread(opts) if idx==0 else MeshThread(opts)
        self._thread.progress.connect(self._append)
        self._thread.percent.connect(self.pbar.setValue)
        self._thread.done.connect(self._on_done)
        self._thread.error.connect(self._on_error)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _on_done(self,msg,ok,tot):
        self._append(f"\n\u2714  {msg}")
        self.btn_conv.setEnabled(True)
        if ok==tot: QMessageBox.information(self,"Completato",msg)
        else: QMessageBox.warning(self,"Completato con errori",msg+"\nControlla il log per i dettagli.")

    def _on_error(self,msg):
        self._append(f"\n\u2718  ERRORE:\n{msg}")
        self.btn_conv.setEnabled(True)
        QMessageBox.critical(self,"Errore",msg[:800])

if __name__=="__main__":
    app=QApplication(sys.argv); app.setStyle("Fusion")
    win=MainWindow(); win.show(); sys.exit(app.exec_())
