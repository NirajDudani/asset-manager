import nuke
import os
from os.path import join
from PySide2 import QtWidgets, QtCore
import csv

class AssetManager(QtWidgets.QDialog):
    def __init__(self):
        super(AssetManager, self).__init__()
        self.setWindowTitle("Asset Manager")
        self.setGeometry(200, 200, 800, 600)

        
        self.asset_table = QtWidgets.QTableWidget()
        self.asset_table.setColumnCount(7)
        self.asset_table.setHorizontalHeaderLabels(["Node", "Asset", "Type", "Path", "Status", "Colorspace", "Range"])

        self.scan_button = QtWidgets.QPushButton("Scan Script")
        self.scan_button.clicked.connect(self.scan_script)

        self.relink_button = QtWidgets.QPushButton("Relink Missing Assets")
        self.relink_button.clicked.connect(self.relink_assets)

        self.version_button = QtWidgets.QPushButton("Available Versions")
        self.version_button.clicked.connect(self.version_report)

        self.report_button = QtWidgets.QPushButton("Generate Report")
        self.report_button.clicked.connect(self.generate_report)
        
        self.asset_table.cellClicked.connect(self.navigate_to_node)
        self.asset_table.cellClicked.connect(self.save_clicked_cell_value)
       
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.asset_table)
        layout.addWidget(self.scan_button)
        layout.addWidget(self.relink_button)
        layout.addWidget(self.version_button)
        layout.addWidget(self.report_button)
        self.setLayout(layout)

    def scan_script(self):
        self.asset_table.setRowCount(0) 
        for node in nuke.allNodes():
            if node.Class() == "Read":
                self.add_asset_to_table(node)

    def node_type(self, node):
        node_split = node["file"].value().split(".")
        node_type = node_split[-1]
        return node_type

    def get_color_space(self, node):
        if node.knob("colorspace"):
            return node["colorspace"].value()
        return "Unknown"
    
    def get_frame_range(self, node):
        start_range = str(node["first"].value())  
        end_range = str(node["last"].value())    
        return start_range + "-" + end_range  

    def save_clicked_cell_value(self, row, column):
        item = self.asset_table.item(row, column)
        if item:
            self.clicked_value = item.text()
        else:
            self.clicked_value = None

    def add_asset_to_table(self, node):
        row = self.asset_table.rowCount()
        self.asset_table.insertRow(row)
    
        def create_item(text):
            item = QtWidgets.QTableWidgetItem(text)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)  
            return item
        
        file_path = node["file"].value()
        def check_read_node_status(node):
            if node.Class() == "Read":
                error = node.error()
                if error:
                    return "Location Error"  
            return "Up-to-date"
        
        status = check_read_node_status(node)

        def file_name(node):
            if node.Class() == "Read":
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                return file_name
        name = file_name(node)

        
        node_name = node.name()
        node_item = create_item(node_name)
        node_item.setData(QtCore.Qt.UserRole, node_name)  
        
        self.asset_table.setItem(row, 0, node_item)  
        self.asset_table.setItem(row, 1, create_item(name)) 
        self.asset_table.setItem(row, 2, create_item(self.node_type(node)))  
        self.asset_table.setItem(row, 3, create_item(file_path))  
        self.asset_table.setItem(row, 4, create_item(status))  
        self.asset_table.setItem(row, 5, create_item(self.get_color_space(node)))  
        self.asset_table.setItem(row, 6, create_item(self.get_frame_range(node)))  

    def navigate_to_node(self, row, column):
        
        if column == 0:  
            node_name = self.asset_table.item(row, 0).text()  
            
            node = nuke.toNode(node_name)
            if node:
                
                for n in nuke.allNodes():
                    n.setSelected(False)               
                node.setSelected(True)                
                nuke.zoom(1, [node.xpos(), node.ypos()])  
            else:
                QtWidgets.QMessageBox.warning(self, "Node Not Found", f"Could not find node: {node_name}")

    def relink_assets(self):
        valid_2d_formats = [".exr", ".dpx", ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".tga", ".mov", ".mp4", ".avi"]
        valid_3d_formats = [".abc", ".fbx", ".obj", ".gltf", ".glb"]
        valid_formats = valid_2d_formats + valid_3d_formats
    
        file_filter = "Supported Files (" + " ".join(["*" + ext for ext in valid_formats]) + ")"
        missing_assets = False  

        for row in range(self.asset_table.rowCount()):
           
            node_name = self.asset_table.item(row, 0).text()
            
            file_path = self.asset_table.item(row, 3).text()
    
            node = nuke.toNode(node_name)
            if node:
                if not file_path or not os.path.exists(file_path):
                    missing_assets = True
                    
                    self.asset_table.setItem(row, 4, QtWidgets.QTableWidgetItem("Missing File"))
    
                elif os.path.isdir(file_path): 
                    valid_files = [f for f in os.listdir(file_path) if os.path.splitext(f)[1].lower() in valid_formats]
                    if not valid_files:
                        missing_assets = True
                        
                        self.asset_table.setItem(row, 4, QtWidgets.QTableWidgetItem("Location Error"))
    
                
                if self.asset_table.item(row, 4).text() in ["Missing File", "Location Error"]:
                    file_dialog = QtWidgets.QFileDialog()
                    new_file_path, _ = file_dialog.getOpenFileName(self, "Select New Asset Path", "", file_filter)
    
                    if new_file_path:                       
                        if not any(new_file_path.lower().endswith(ext) for ext in valid_formats):
                            QtWidgets.QMessageBox.warning(self, "Invalid File Type", "Please select a supported 2D or 3D file type.")
                            continue
    
                        node["file"].setValue(new_file_path)  
                        
                        self.asset_table.setItem(row, 3, QtWidgets.QTableWidgetItem(new_file_path)) 
                        self.asset_table.setItem(row, 4, QtWidgets.QTableWidgetItem("Relinked")) 
    
        
        error_remaining = any(
            self.asset_table.item(row, 4).text() in ["Location Error", "Missing File"]
            for row in range(self.asset_table.rowCount())
        )
    
        if not missing_assets:
            QtWidgets.QMessageBox.information(self, "Notice", "All files are linked and up-to-date.")

    def version_report(self):
        if hasattr(self, "clicked_value"):
            selected_node = nuke.toNode(self.clicked_value)
            file_path = selected_node["file"].getValue()
            current_dir = os.path.dirname(file_path)
            main_dir = os.path.dirname(current_dir)
            os.chdir(main_dir)

            folder_versions = [folder[1:] for folder in os.listdir(main_dir)]
            available_versions = sorted(folder_versions, key=int)

            version_selector = QtWidgets.QInputDialog()
            version_selector.setComboBoxItems(["v" + v for v in available_versions])
            version_selector.setWindowTitle("Select Available Version")
            version_selector.setLabelText("Choose a version:")
            version_selector.setComboBoxEditable(False)
            version_selector.setModal(True)
            
            if version_selector.exec_() == QtWidgets.QDialog.Accepted:
                selected_version = version_selector.textValue()
                selected_version_path = os.path.normpath(join(main_dir, selected_version))

                if selected_version_path != current_dir:
                    latest_items = os.listdir(selected_version_path)
                    for item in latest_items:
                        item_path = join(selected_version_path, item)
                        file_ext = os.path.splitext(item)[1].lower()
                        
                        valid_video_formats = [".mov", ".mp4", ".avi", ".mpg", ".mpeg", ".wmv", ".mkv", ".flv", ".webm"]
                        valid_image_formats = [".exr", ".dpx", ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".tga"]

                        if file_ext in valid_video_formats or file_ext in valid_image_formats:
                            new_node = nuke.createNode("Read")
                            new_node["file"].setValue(item_path.replace("\\", "/"))
                            if file_ext in valid_image_formats:
                                name_part, frame_part_ext = item.rsplit("_", 1)
                                frame_part, ext = frame_part_ext.split(".")
                                updated_file_path = join(selected_version_path, f"{name_part}_####.{ext}")
                                new_node["file"].setValue(updated_file_path.replace("\\", "/"))
                                new_node["first"].setValue(int(f"{frame_part}"))
                                new_node["last"].setValue(len(latest_items))
                            break
                else:
                    QtWidgets.QMessageBox.information(self, "Updated Version", "The asset is already up-to-date.")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "No asset selected.")                   

    def generate_report(self):
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Report", "", "CSV Files (*.csv)")
    
        if not save_path:
            return 
    
        with open(save_path, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            writer.writerow(["Node", "Asset", "Type", "Path", "Status", "Colorspace", "Range"])
    
            
            for row in range(self.asset_table.rowCount()):
                row_data = []
                for col in range(self.asset_table.columnCount()):
                    item = self.asset_table.item(row, col)
                    row_data.append(item.text() if item else "N/A") 
    
                writer.writerow(row_data)  
    
        QtWidgets.QMessageBox.information(self, "Report Generated", f"Report saved at:\n{save_path}")


def show_asset_manager():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    manager = AssetManager()
    manager.exec_()


nuke.menu("Nuke").addCommand("Tools/Asset Manager", show_asset_manager)