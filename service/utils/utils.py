from PyQt6.QtWidgets import QLabel, QTextEdit, QFrame, QVBoxLayout, QMenu, QApplication, QSpacerItem, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QSizePolicy
import os
from PyQt6.QtGui import QPixmap, QAction,  QClipboard

def delete_output_card(parent, card_frame):
    """Delete the selected output card"""
    parent.output_layout.removeWidget(card_frame)
    card_frame.deleteLater()

    # Optional: remove from parent.data list
    if hasattr(parent, "data") and isinstance(parent.data, list):
        index = parent.output_layout.indexOf(card_frame)
        if 0 <= index < len(parent.data):
            del parent.data[index]

def delete_all_outputs(parent):
    """Removes all output cards from the output layout"""
    while parent.output_layout.count() > 0:
        item = parent.output_layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
    parent.data = []  # Clear stored data

def show_context_menu(parent, pos, card_frame):
    """Display right-click menu on each output card"""
    menu = QMenu(parent)

    copy_image_action = menu.addAction("Copy Output Image")
    delete_action = menu.addAction("Delete Output")
    delete_all_action = menu.addAction("Delete All Outputs")

    action = menu.exec(card_frame.mapToGlobal(pos))

    if action == copy_image_action:
        parent.copy_output_image(card_frame)
    elif action == delete_action:
        delete_output_card(parent, card_frame)
    elif action == delete_all_action:
        delete_all_outputs(parent)


def copy_output_image(parent, image_label):
    """Menyalin gambar dari QLabel ke clipboard dengan simpan file sementara (tanpa loop)."""
    pixmap = image_label.pixmap()
    
    if pixmap and not pixmap.isNull():
        temp_folder = os.path.join(parent.path, 'temp')
        temp_path = os.path.join(temp_folder, 'temp_image.png')

        os.makedirs(temp_folder, exist_ok=True)

        if pixmap.save(temp_path):
            print(f"Gambar disimpan di: {temp_path}")
            
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(QPixmap(temp_path))

            if os.path.exists(temp_path):  
                os.remove(temp_path)
        else:
            print("Gagal menyimpan gambar sementara.")
    else:
        print("Tidak ada gambar untuk disalin.")


def show_image_context_menu(parent, pos, image_label, image_path):
    """Display right-click menu on image labels."""
    menu = QMenu(parent)

    copy_image_action = menu.addAction("Copy Image")
    save_as_action = menu.addAction("Save Image As...")

    action = menu.exec(image_label.mapToGlobal(pos))

    if action == copy_image_action:
        copy_output_image(parent, image_label)
    elif action == save_as_action:
        file_dialog = QFileDialog()
        save_path, _ = file_dialog.getSaveFileName(parent, "Save Image", os.path.basename(image_path), "Images (*.png *.jpg *.bmp)")
        if save_path:
            image_label.pixmap().save(save_path)



def check_script(r_script):
    """
    Checks if the provided R script string is not empty.
    Parameters:
    r_script (str): The R script string to check.
    Returns:
    bool: True if the R script string is not empty, False otherwise.
    """
    
    if r_script == "":
        QMessageBox.warning(None, "Warning", "R sript cannot empty")
        return False
    return True
        
        
def add_copy_context_menu_to_table(table_view):
    """
    Adds a context menu to the QTableView for copying data (including headers and content).
    Args:
        table_view (QTableView): The table view to which the context menu will be added.
    """
    def copy_table_data():
        """
        Copies the table data (headers and content) to the clipboard.
        """
        model = table_view.model()
        if model is None:
            return

        # Get headers
        headers = [model.headerData(i, Qt.Orientation.Horizontal) for i in range(model.columnCount())]
        data = '\t'.join(headers) + '\n'

        # Get table content
        for row in range(model.rowCount()):
            row_data = [model.index(row, col).data() for col in range(model.columnCount())]
            data += '\t'.join(map(str, row_data)) + '\n'

        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(data)

    # Add context menu
    table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    table_view.customContextMenuRequested.connect(lambda pos: show_table_context_menu(pos, table_view, copy_table_data))
    
    header = table_view.horizontalHeader()
    header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    header.customContextMenuRequested.connect(lambda pos: show_table_context_menu(pos, table_view, copy_table_data))


def show_table_context_menu(pos, table_view, copy_action):
    """
    Displays the context menu for the QTableView.
    Args:
        pos (QPoint): The position where the context menu is requested.
        table_view (QTableView): The table view for which the context menu is displayed.
        copy_action (function): The function to execute when "Copy" is selected.
    """
    menu = QMenu(table_view)
    copy_action_item = QAction("Copy", table_view)
    copy_action_item.triggered.connect(copy_action)
    menu.addAction(copy_action_item)
    menu.exec(table_view.mapToGlobal(pos))

from PyQt6.QtWidgets import QTableView, QAbstractItemView, QVBoxLayout, QHeaderView
from PyQt6.QtGui import QStandardItemModel, QStandardItem

import polars as pl
from datetime import datetime
import json
import uuid
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QHBoxLayout, QWidget, QSizePolicy

def display_script_and_output(parent, r_script, results, plot_paths=None, timestamps=None):
    """
    Adds a new output card to the layout displaying the provided R script and its result.
    Parameters:
    parent (object): The parent widget containing the layout to which the card will be added.
    r_script (str): The R script to be displayed in the card.
    results (dict or str): The output result of the R script to be displayed in the card. If empty or None, only the script will be displayed.
    plot_paths (list): List of paths to plot images to be displayed.
    Returns:
    None
    """
    # Membuat frame sebagai card
    card_frame = QFrame()
    card_frame.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    card_frame.customContextMenuRequested.connect(lambda pos: show_context_menu(parent, pos, card_frame))
    card_frame.setStyleSheet("""
        QFrame {
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
        }
        QFrame:hover {
            background-color: #f0f0f0;
            border: 1px solid #c35112;
        }
    """)

    card_frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

    # Layout vertikal untuk card
    card_layout = QVBoxLayout(card_frame)
    card_layout.setSpacing(8)

    # Bagian Script
    out = {}
    out["r_script"] = r_script  # Simpan r_script ke dalam data parent untuk referensi
    result = {}

    # Bersihkan baris kosong hanya di bagian akhir script
    lines = r_script.splitlines()
    while lines and lines[-1].strip() == "":
        lines.pop()
    cleaned_script = "\n".join(lines)

    # Widget untuk menampilkan script
    script_box = QTextEdit()
    script_box.setPlainText(cleaned_script)
    script_box.setReadOnly(True)
    script_box.hide()
    script_box.setStyleSheet(f"""
        QTextEdit {{
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 5px;
            font-family: "Courier New", Courier, monospace;
            font-size: {parent.font_size}px;
        }}
    """)

    # Hitung tinggi berdasarkan jumlah baris, batasi hingga max_height
    num_lines = cleaned_script.count('\n') + 1
    line_height = script_box.fontMetrics().lineSpacing()
    calculated_height = line_height * num_lines + 10  # Tambah margin kecil
    max_height = 400
    script_box.setFixedHeight(min(calculated_height, max_height))

    # Tampilkan scroll hanya jika tinggi lebih dari batas
    script_box.setVerticalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAlwaysOn if calculated_height > max_height
        else Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )

    # Label dengan tombol show/hide di dalamnya (pakai layout horizontal)
    label_widget = QWidget()
    label_widget.setStyleSheet("QWidget { color: #333; margin-top: 10px; margin-bottom: 5px;}")
    label_layout = QHBoxLayout(label_widget)
    label_layout.setContentsMargins(0, 0, 0, 0)
    label_layout.setSpacing(5)
    
    label_script = QLabel("<b>R Script:</b>")
    label_script.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    label_layout.addWidget(label_script, 0, Qt.AlignmentFlag.AlignLeft)


    toggle_btn = QPushButton("▶")
    toggle_btn.setStyleSheet("font-size: 14px; border: none; background: transparent;")
    toggle_btn.setCheckable(True)
    toggle_btn.setChecked(False)
    toggle_btn.setMaximumWidth(22)
    toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)

    def toggle_script():
        if toggle_btn.isChecked():
            script_box.show()
            toggle_btn.setText("▼")
        else:
            script_box.hide()
            toggle_btn.setText("▶")

    toggle_btn.toggled.connect(toggle_script)
    label_layout.addWidget(toggle_btn, 0, Qt.AlignmentFlag.AlignRight)
    label_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    # Tambahkan ke layout
    card_layout.addWidget(label_widget)
    card_layout.addWidget(script_box)

    # Bagian Output (jika ada)
    if isinstance(results, dict):
        label_output = QLabel("<b>Output:</b>")
        label_output.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label_output.setStyleSheet("color: #333; margin-top: 10px; margin-bottom: 5px;")
        card_layout.addWidget(label_output)
        
        if "Model" in results:
            model_value = results["Model"]
            model_label = QLabel(f"<b>Summary of {model_value}</b>")
            model_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            model_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            model_label.setStyleSheet("font-size: 20px; background-color: #ccc; margin-top: 5px;")
            card_layout.addWidget(model_label)
            result["Model"] = results["Model"]

        if "Pre-Modeling" in results:
            title_value = results["Pre-Modeling"]
            title_label = QLabel(f"<b>Pre-Modeling : {title_value}</b>")
            title_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("font-size: 18px; background-color: #ccc; margin-top: 5px;")
            card_layout.addWidget(title_label)
            result["Pre-Modeling"] = results["Pre-Modeling"]
        
        if "Graph" in results:
            graph_value = results["Graph"]
            graph_label = QLabel(f"<b>Graph : {graph_value}</b>")
            graph_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            graph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            graph_label.setStyleSheet("font-size: 18px; background-color: #ccc; margin-top: 5px;")
            card_layout.addWidget(graph_label)
            result["Graph"] = results["Graph"]

        # Add timestamp for generation
        timestamp = datetime.now().strftime("%H:%M:%S %d-%m-%Y") if timestamps is None else timestamps
        out["timestamp"] = timestamp
        timestamp_label = QLabel(f"<i>Generated at: {timestamp}</i>")
        timestamp_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        timestamp_label.setStyleSheet("font-size: 12px; color: #666; margin-top: 10px;")
        card_layout.addWidget(timestamp_label)

        for key, value in results.items():
            # Skip displaying if the key is "Model"
            if key in ["Model", "Pre-Modeling", "Graph", "Plot"]:
                continue

            # Tambahkan header untuk setiap key
            key_label = QLabel(f"<b>{key}:</b>")
            key_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            key_label.setStyleSheet("color: #333; margin-top: 5px;")
            card_layout.addWidget(key_label)

            if isinstance(value, pl.DataFrame):
                table_view = QTableView()
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels(value.columns)

                for row in value.iter_rows(named=True):
                    items = [QStandardItem(str(row[col])) for col in value.columns]
                    model.appendRow(items)
                
                result[key] = value.to_dict(as_series=False)
                
                table_view.setModel(model)
                table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                table_view.horizontalHeader().setFixedHeight(50)

                # Hitung tinggi tabel berdasarkan jumlah baris (maksimal 5 baris)
                row_height = table_view.verticalHeader().defaultSectionSize()
                header_height = table_view.horizontalHeader().height()
                max_visible_rows = 5
                visible_rows = min(model.rowCount(), max_visible_rows)
                total_height = row_height * visible_rows + header_height + 20  # Tambahkan margin
                table_view.setFixedHeight(total_height)

                # Enable scroll jika baris lebih dari 5
                if model.rowCount() > max_visible_rows:
                    table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                else:
                    table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

                table_view.setStyleSheet("""
                    QTableView {
                        background-color: #fff;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                        padding: 5px;
                        font-family: Consolas, Courier New, monospace;
                    }
                """)
                add_copy_context_menu_to_table(table_view)
                card_layout.addWidget(table_view)
                
            else:
                # Tampilkan nilai biasa sebagai teks
                value_label = QLabel(str(value))
                value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                value_label.setStyleSheet("color: #333; margin-left: 10px;")
                card_layout.addWidget(value_label)
                result[key] = value
        out["result"] = result  # Simpan hasil ke dalam data parent untuk referensi

    elif results:
        label_output = QLabel("<b>Output:</b>")
        label_output.setStyleSheet("color: #333; margin-top: 10px; margin-bottom: 5px;")
        result_box = QTextEdit()
        result_box.setPlainText(results)
        result_box.setReadOnly(True)
        result_box.setStyleSheet("""
            QTextEdit {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-family: Consolas, Courier New, monospace;
            }
        """)
        
        card_layout.addWidget(label_output)
        card_layout.addWidget(result_box)

    if plot_paths is not None:
        label_plot = QLabel("<b>Plot:</b>")
        label_plot.setStyleSheet("color: #333; margin-top: 10px; margin-bottom: 5px;")
        card_layout.addWidget(label_plot)

        for plot_path in plot_paths:
            if os.path.exists(plot_path):
                pixmap = QPixmap(plot_path)
                label = QLabel()
                label.setPixmap(pixmap)
                label.setFixedSize(800, 600)
                label.setScaledContents(True)
                label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")

                # Enable right-click menu on image
                label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                label.customContextMenuRequested.connect(
                    lambda pos, l=label, p=plot_path: show_image_context_menu(parent, pos, l, p)
                )

                card_layout.addWidget(label)

                # Simpan image ke path baru
                dest_folder = os.path.join(parent.path, 'file-data', 'temp')
                os.makedirs(dest_folder, exist_ok=True)
                unique_id = uuid.uuid4().hex
                filename, ext = os.path.splitext(os.path.basename(plot_path))
                dest_path = os.path.join(dest_folder, f"{filename}_{unique_id}{ext}")
                pixmap.save(dest_path)
                if "Plot" not in result:
                    result["Plot"] = []
                result["Plot"].append(dest_path)
                os.remove(plot_path)
                
    # Tambahkan card ke layout utama
    parent.output_layout.addWidget(card_frame)
    # parent.output_layout.addStretch()
    parent.tab_widget.setCurrentWidget(parent.tab3)
    if not hasattr(parent, "data") or not isinstance(parent.data, list):
        parent.data = []
    parent.data.append(out)
    parent.autosave_data()
    

