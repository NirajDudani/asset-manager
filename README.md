# Asset Manager for Nuke

A Python GUI tool for [Foundry Nuke](https://www.foundry.com/products/nuke) that gives compositors a centralized dashboard to scan, inspect, relink, version, and report on every Read node in a script — so broken paths and outdated assets get caught before they reach the render farm.

![Python](https://img.shields.io/badge/Python-2.7%20%7C%203.x-blue)
![Nuke](https://img.shields.io/badge/Nuke-11%2B-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

---

## What It Does

Open any Nuke script, hit **Scan Script**, and Asset Manager builds a live table of every Read node showing its name, file type, path, link status, colorspace, and frame range. From that table you can jump to any node in the graph, relink broken paths, swap to a different version, or export everything to CSV for production tracking.

---

## Installation

### Step 1 — Download

Clone the repo or download the ZIP:

```bash
git clone https://github.com/YOUR_USERNAME/asset-manager.git
```

Or click **Code → Download ZIP** on the GitHub page and extract it.

### Step 2 — Copy the Script

Copy `asset-manager.py` into your `.nuke` directory. The `.nuke` folder lives in your home directory by default:

| OS | Default Path |
|----|-------------|
| Windows | `C:\Users\<you>\.nuke\` |
| macOS | `/Users/<you>/.nuke/` |
| Linux | `/home/<you>/.nuke/` |

> **Tip:** If you don't see a `.nuke` folder, open Nuke once and it will create one automatically. On Windows and macOS, hidden folders may not show by default — enable "Show hidden files" in your file browser.

### Step 3 — Register the Script

Open (or create) the file `menu.py` inside your `.nuke` directory and add this single line:

```python
import asset_manager
```

> **Note:** The import name uses an underscore (`asset_manager`), so make sure the file on disk is named `asset_manager.py` (rename it from `asset-manager.py` if needed). Python cannot import filenames that contain hyphens.

### Step 4 — Restart Nuke

Close and reopen Nuke. You should now see a new menu entry at **Nuke → Tools → Asset Manager**.

---

## How to Use It

### 1. Scan Script

Open a Nuke script that contains Read nodes, then launch the tool from **Nuke → Tools → Asset Manager** and click **Scan Script**. The table populates with every Read node and shows one of these statuses:

| Status | Meaning |
|--------|---------|
| Up-to-date | File path is valid and accessible |
| Location Error | Path exists but the file can't be read |
| Missing File | File not found on disk |

### 2. Navigate to Node

Click any row in the **Node** column (first column) and the Node Graph will zoom to that node and select it. This is useful for quickly finding problem nodes in large scripts.

### 3. Relink Missing Assets

Click **Relink Missing Assets** to fix broken paths. The tool walks through every node flagged as missing or errored and opens a file browser so you can point it to the correct file. It handles:

- **Image sequences** — automatically detects the first and last frame from the folder, converts the path to `####` notation, and updates the frame range on the Read node.
- **Video files** — links directly to the selected `.mov`, `.mp4`, `.avi`, etc.
- **3D formats** — supports `.abc`, `.fbx`, `.obj`, `.gltf`, `.glb`.

If all assets are already linked, you'll see a confirmation dialog instead.

### 4. Available Versions

Select a Read node in the table (click any cell in its row), then click **Available Versions**. The tool looks for sibling version folders (`v001`, `v002`, `v003`, …) next to the current version and presents a dropdown. Choosing a different version creates a new Read node with the updated path and frame range.

**Required folder structure:**

```
/project/assets/
└── characterA/
    ├── v001/
    │   ├── characterA_diffuse_v0001_0001.exr
    │   └── characterA_diffuse_v0001_0031.exr
    ├── v002/
    │   ├── characterA_diffuse_v0002_0001.exr
    │   └── characterA_diffuse_v0002_0031.exr
    └── v003/
        ├── characterA_diffuse_v0003_0001.exr
        └── characterA_diffuse_v0003_0031.exr
```

### 5. Generate Report

Click **Generate Report** to export the current table to a `.csv` file. You'll be prompted to choose a save location. The CSV includes all seven columns (Node, Asset, Type, Path, Status, Colorspace, Range) and can be opened in Excel, Google Sheets, or any spreadsheet app for production tracking and handoffs.

---

## Supported File Formats

| Category | Extensions |
|----------|-----------|
| Image sequences | `.exr` `.dpx` `.tif` `.tiff` `.png` `.jpg` `.jpeg` `.tga` |
| Video | `.mov` `.mp4` `.avi` `.mpg` `.mpeg` `.wmv` `.mkv` `.flv` `.webm` |
| 3D geometry | `.abc` `.fbx` `.obj` `.gltf` `.glb` |

---

## Requirements

- **Nuke 11+** (any version with PySide2 bundled — this includes most modern releases)
- No external Python packages required; everything used (`os`, `csv`, `PySide2`) ships with Nuke's embedded Python.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Menu entry doesn't appear | Make sure the file is named `asset_manager.py` (underscore, not hyphen) and lives directly inside `.nuke/`. Check Nuke's Script Editor for import errors. |
| `ModuleNotFoundError: No module named 'asset_manager'` | The filename probably still has a hyphen. Rename it to `asset_manager.py`. |
| "No asset selected" when clicking Available Versions | Click a cell in the **Node** column first to select the asset, then click the button. |
| Relink doesn't detect frame range | The tool expects filenames ending in `_####.ext` (e.g., `shot_0001.exr`). If your naming convention is different, the auto-detection may not parse correctly. |

---

## Contributing

Contributions are welcome — feel free to open issues or submit pull requests. If you're adding a feature, please test it against a Nuke script with a mix of linked, missing, and sequence-based Read nodes.

---

## License

MIT — use it however you like.
