# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Krill.py'],
    pathex=[],
    binaries=[],
    datas=[('Krill.ico', '.')],
    hiddenimports=[
        'numpy', 'numpy.core', 'numpy.core.multiarray',
        'numpy.core._multiarray_umath', 'numpy.core.numeric',
        'numpy.core.fromnumeric', 'numpy.core._dtype_ctypes',
        'numpy._core', 'numpy._core.multiarray',
        'numpy._core._multiarray_umath', 'numpy._core.numeric',
        'laspy', 'laspy.lasappender', 'laspy.laswriter',
        'laspy.lasreader', 'lazrs',
        'e57',
        'plyfile',
        'trimesh', 'trimesh.exchange', 'trimesh.exchange.load',
        'trimesh.exchange.export', 'trimesh.exchange.stl',
        'trimesh.exchange.obj', 'trimesh.exchange.ply',
        'trimesh.exchange.gltf', 'trimesh.exchange.dae',
        'trimesh.exchange.off', 'trimesh.util',
        'trimesh.visual', 'trimesh.visual.color',
        'trimesh.simplify',
        'fast_simplification',
        'scipy', 'scipy.spatial', 'scipy.sparse',
        'scipy.sparse.csgraph', 'networkx',
        'PyQt5', 'PyQt5.QtWidgets', 'PyQt5.QtCore',
        'PyQt5.QtGui', 'PyQt5.sip',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['open3d','pye57','matplotlib','tkinter',
              'PyQt5.QtWebEngineWidgets','PyQt5.QtMultimedia'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
    name='Krill',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Krill.ico',
)
