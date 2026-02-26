# Asset-Manager-Nuke  

A Nuke Python GUI tool that scans, manages, relinks, and versions Read node assets, helping artists quickly troubleshoot and organize shot files inside production scripts.

---

## Features  

### Scan Script  
- Scans all Read nodes in the current Nuke script  
- Displays:
  - Node name  
  - Asset name  
  - File type  
  - File path  
  - Status (Up-to-date / Missing / Location Error)  
  - Colorspace  
  - Frame range  

### Navigate to Node  
- Click a node in the table to automatically select and zoom to it in the Node Graph  

### Relink Missing Assets  
- Detects missing or broken file paths  
- Supports image sequences, videos, and 3D formats  
- Automatically:
  - Detects first and last frame  
  - Converts sequences to #### format  
  - Updates frame range  

### Available Versions  
- Detects version folders (v001, v002, etc.)  
- Lets you select from available versions  
- Creates a new Read node with updated path and frame range  

### Generate Report  
- Exports asset data to a CSV file  
- Useful for production tracking and handoffs  

---

## Usage  

1. Open your Nuke script  
2. Launch **Asset Manager** from:  
   `Nuke → Tools → Asset Manager`  
3. Click **Scan Script**  
4. Review asset status  
5. Relink missing files or check available versions as needed  
6. Generate a CSV report if required  

---

## Installation

1. Download the script file  
2. Place it inside your `.nuke` directory  
3. Add the following to your `menu.py`:

```python
import asset_manager

---

### Contribution

Feel free to open issues or submit pull requests with ideas or improvements.
