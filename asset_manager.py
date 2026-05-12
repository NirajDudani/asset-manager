import nuke
import os
from os.path import join
import csv


def show_asset_manager():
    try:
        from PySide2 import QtWidgets, QtCore
    except ImportError:
        from PySide6 import QtWidgets, QtCore

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
            return node["file"].value().split(".")[-1]

        def get_color_space(self, node):
            if node.knob("colorspace"):
                return node["colorspace"].value()
            return "Unknown"

        def get_frame_range(self, node):
            return str(node["first"].value()) + "-" + str(node["last"].value())

        def save_clicked_cell_value(self, row, column):
            item = self.asset_table.item(row, column)
            self.clicked_value = item.text() if item else None

        def add_asset_to_table(self, node):
            row = self.asset_table.rowCount()
            self.asset_table.insertRow(row)

            def create_item(text):
                item = QtWidgets.QTableWidgetItem(text)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                return item

            file_path = node["file"].value()
            status = "Location Error" if node.error() else "Up-to-date"
            name = os.path.splitext(os.path.basename(file_path))[0]
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
                    QtWidgets.QMessageBox.warning(self, "Node Not Found", "Could not find node: {}".format(node_name))

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

                    # FIX: guard item(row, 4) for None before calling .text()
                    status_item = self.asset_table.item(row, 4)
                    if status_item and status_item.text() in ["Missing File", "Location Error"]:
                        new_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select New Asset Path", "", file_filter)
                        if not new_file_path:
                            continue
                        selected_item = os.path.basename(new_file_path)
                        dir_loc = os.path.dirname(new_file_path)

                        valid_video_formats = [".mov", ".mp4", ".avi", ".mpg", ".mpeg", ".wmv", ".mkv", ".flv", ".webm"]
                        valid_image_formats = [".exr", ".dpx", ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".tga"]
                        file_ext = os.path.splitext(selected_item)[1].lower()

                        if file_ext in valid_video_formats:
                            node["file"].setValue(new_file_path)
                            self.asset_table.setItem(row, 3, QtWidgets.QTableWidgetItem(new_file_path))
                            self.asset_table.setItem(row, 4, QtWidgets.QTableWidgetItem("Relinked"))
                            break
                        elif file_ext in valid_image_formats:
                            # FIX: filter to only image files before min/max to avoid ValueError on mixed dirs
                            image_files = sorted([
                                f for f in os.listdir(dir_loc)
                                if os.path.splitext(f)[1].lower() in valid_image_formats
                            ])
                            if not image_files:
                                QtWidgets.QMessageBox.warning(self, "Error", "No image files found in the selected directory.")
                                continue
                            first_frame = image_files[0].split("_")[-1].split(".")[0]
                            last_frame  = image_files[-1].split("_")[-1].split(".")[0]

                            # FIX: guard rsplit for filenames without underscore
                            if "_" not in selected_item:
                                QtWidgets.QMessageBox.warning(self, "Error", "Selected file does not follow the expected naming convention (name_####.ext).")
                                continue
                            name_part, frame_part_ext = selected_item.rsplit("_", 1)
                            if "." not in frame_part_ext:
                                QtWidgets.QMessageBox.warning(self, "Error", "Could not parse frame number and extension from filename.")
                                continue
                            frame_part, ext = frame_part_ext.split(".", 1)
                            updated_path = join(dir_loc, "{}_####.{}".format(name_part, ext))
                            node["file"].setValue(updated_path.replace("\\", "/"))
                            node["first"].setValue(int(first_frame))
                            node["last"].setValue(int(last_frame))
                            self.asset_table.setItem(row, 3, QtWidgets.QTableWidgetItem(new_file_path))
                            self.asset_table.setItem(row, 4, QtWidgets.QTableWidgetItem("Relinked"))
                            break
                        else:
                            QtWidgets.QMessageBox.warning(self, "Invalid File Type", "Please select a supported 2D or 3D file type.")

            if not missing_assets:
                QtWidgets.QMessageBox.information(self, "Notice", "All files are linked and up-to-date.")

        def version_report(self):
            if not hasattr(self, "clicked_value") or not self.clicked_value:
                QtWidgets.QMessageBox.warning(self, "Error", "No asset selected.")
                return

            # FIX: guard nuke.toNode() for None
            selected_node = nuke.toNode(self.clicked_value)
            if not selected_node:
                QtWidgets.QMessageBox.warning(self, "Error", "Could not find node: {}".format(self.clicked_value))
                return

            file_path = selected_node["file"].getValue()
            current_dir = os.path.dirname(file_path)
            main_dir = os.path.dirname(current_dir)

            if not os.path.isdir(main_dir):
                QtWidgets.QMessageBox.warning(self, "Error", "Asset directory does not exist:\n{}".format(main_dir))
                return

            # FIX: skip folders whose names (after stripping leading 'v') are not numeric
            folder_versions = []
            for folder in os.listdir(main_dir):
                stripped = folder.lstrip("v")
                if stripped.isdigit():
                    folder_versions.append(stripped)
            available_versions = sorted(folder_versions, key=int)

            if not available_versions:
                QtWidgets.QMessageBox.information(self, "No Versions", "No versioned folders found in:\n{}".format(main_dir))
                return

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
                                image_files = sorted([
                                    f for f in latest_items
                                    if os.path.splitext(f)[1].lower() in valid_image_formats
                                ])
                                if image_files:
                                    first_frame = image_files[0].split("_")[-1].split(".")[0]
                                    last_frame  = image_files[-1].split("_")[-1].split(".")[0]
                                    if "_" in item:
                                        name_part, frame_part_ext = item.rsplit("_", 1)
                                        if "." in frame_part_ext:
                                            frame_part, ext = frame_part_ext.split(".", 1)
                                            updated_path = join(selected_version_path, "{}_####.{}".format(name_part, ext))
                                            new_node["file"].setValue(updated_path.replace("\\", "/"))
                                            new_node["first"].setValue(int(first_frame))
                                            new_node["last"].setValue(int(last_frame))
                            break
                else:
                    QtWidgets.QMessageBox.information(self, "Up-to-date", "The asset is already at the selected version.")

        def generate_report(self):
            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Report", "", "CSV Files (*.csv)")
            if not save_path:
                return
            with open(save_path, "w", newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Node", "Asset", "Type", "Path", "Status", "Colorspace", "Range"])
                for row in range(self.asset_table.rowCount()):
                    row_data = [self.asset_table.item(row, col).text() if self.asset_table.item(row, col) else "N/A"
                                for col in range(self.asset_table.columnCount())]
                    writer.writerow(row_data)
            QtWidgets.QMessageBox.information(self, "Report Generated", "Report saved at:\n{}".format(save_path))

    manager = AssetManager()
    manager.exec_()


nuke.menu('Nuke').addCommand('NDToolKit/Asset Manager', show_asset_manager)
