# 🦐 Krill — 3D Converter

A lightweight universal converter for **point clouds** and **3D meshes**.

Built for surveyors, architects, designers, and anyone working with
3D scan data who needs to convert between formats, reduce file size,
or simplify geometry without losing important detail.

![Krill UI](docs/screenshot.png)

## ✨ Features

### Point Clouds
- **Input formats**: E57, LAS, LAZ, PLY, PTS, PTX, XYZ, TXT, CSV
- **Output formats**: LAZ, LAS, PLY, PTS, XYZ
- **Decimation**:
  - *Random* — keep a percentage of the original points
  - *Smart* — voxel-based downsampling that preserves geometric
    detail (edges, corners) while simplifying flat surfaces

### 3D Meshes
- **Input formats**: STL, OBJ, PLY, GLB, GLTF, DAE, OFF
- **Output formats**: STL, OBJ, PLY, GLB, GLTF, DAE
- **Decimation**: Quadric Edge Collapse — preserves curved/detailed
  zones while reducing triangles on flat surfaces

### General
- Drag & drop multiple files
- Batch conversion
- RGB color preservation
- Standalone executable (no Python installation required)
- Output files never overwrite originals (automatic `_krill` suffix)

## 📥 Download

Get the latest Windows build from the
[Releases](https://github.com/lukeferra/krill/releases) page.

Just download `Krill.exe` and run it — no installation needed.

## 🛠️ Built with

Python, PyQt5, NumPy, laspy, e57, trimesh, plyfile, fast-simplification

## 📄 License

The software is **free to use** for personal and professional purposes.
Modification, redistribution, and reverse engineering — even partial —
require written consent from the author.

© 2026 Luca Ferrari — All rights reserved.

## 💬 Contact

For bug reports, feature requests, or custom development inquiries:
**lukeferra90@gmail.com**
