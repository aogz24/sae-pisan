from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QTableView, QDialogButtonBox, QPushButton, QFileDialog
import polars as pl
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class CSVOptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSV Options")

        self.file_path = None
        self.separator = ","
        self.header = True

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # File picker
        self.file_label = QLabel("No file selected")
        layout.addWidget(self.file_label)
        self.file_button = QPushButton("Select File")
        self.file_button.clicked.connect(self.select_file)
        layout.addWidget(self.file_button)

        # Separator input
        layout.addWidget(QLabel("Separator (e.g., , or ;)"))
        self.separator_input = QLineEdit(",")
        self.separator_input.textChanged.connect(self.update_preview)
        layout.addWidget(self.separator_input)

        # Header checkbox
        self.header_checkbox = QCheckBox("First row as header")
        self.header_checkbox.setChecked(True)  # Default header True
        self.header_checkbox.toggled.connect(self.update_preview)
        layout.addWidget(self.header_checkbox)

        # Preview Table
        self.preview_label = QLabel("Preview")
        layout.addWidget(self.preview_label)
        self.preview_table = QTableView()
        layout.addWidget(self.preview_table)

        # OK/Cancel buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def select_file(self):
        """File picker untuk memilih file CSV."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(f"Selected: {file_path}")
            self.update_preview()

    def update_preview(self):
        """Perbarui preview tabel berdasarkan input."""
        if not self.file_path:
            self.preview_table.setModel(None)
            return

        sep = self.separator_input.text()
        hdr = True if self.header_checkbox.isChecked() else False
        try:
            preview_data = pl.read_csv(self.file_path, separator=sep, has_header=hdr).head(10)
            model = QStandardItemModel()
            
            if not self.header_checkbox.isChecked():
                preview_data.columns = [f"Column {i+1}" for i in range(preview_data.shape[1])]
            
            model.setHorizontalHeaderLabels(preview_data.columns)

            for row in preview_data.to_numpy():
                items = [QStandardItem(str(cell)) for cell in row]
                model.appendRow(items)

            self.preview_table.setModel(model)
        except Exception as e:
            print(f"Error: {e}")
            self.preview_table.setModel(None)

    def get_csv_options(self):
        """Mengembalikan opsi CSV jika dialog diterima."""
        if self.exec() == QDialog.DialogCode.Accepted and self.file_path:
            return self.file_path, self.separator_input.text(), self.header_checkbox.isChecked()
        return None, None, None

from PyQt6 import QtCore
from PyQt6 import QtCore, QtGui, QtWidgets
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, batch_size=100):
        super().__init__()
        self._data = data
        self.batch_size = batch_size
        self.loaded_rows = min(batch_size, self._data.shape[0])
    
    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        # Return the number of rows that should be displayed. 
        # Here, we use self.loaded_rows to support batch loading.
        return self.loaded_rows

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        # Return the number of columns based on your data's columns.
        return len(self._data.columns)
    
    import polars as pl

    def data(self, index: QtCore.QModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == QtCore.Qt.ItemDataRole.DisplayRole or role == QtCore.Qt.ItemDataRole.EditRole:
            column_name = self._data.columns[index.column()]  # Get column name
            value = self._data[column_name][index.row()]  # Get value using Polars indexing
            return str(value)  # Convert to string for Qt compatibility

        return None

    
    def set_data(self, new_data):
        if isinstance(new_data, pl.DataFrame):
            self.beginResetModel()
            self._data = new_data
            self.loaded_rows = min(self.batch_size, self._data.shape[0])
            self.endResetModel()
        else:
            raise ValueError("Data must be a Polars DataFrame")
    def get_column_type(self, column_index):
        if isinstance(column_index, int) and 0 <= column_index < len(self._data.columns):
            column_name = self._data.columns[column_index]
            return self._data[column_name].dtype
        return None
    def get_data(self):
        return self._data
    
    def set_column_type(self, column_index, new_type):
        if isinstance(column_index, int) and 0 <= column_index < len(self._data.columns):
            column_name = self._data.columns[column_index]
            old_dtype = self._data[column_name].dtype
            old_data = self._data[column_name].to_list()

            if new_type == "String":
                new_dtype = pl.Utf8
            elif new_type == "Integer":
                if self._data[column_name].dtype == pl.Utf8:
                    try:
                        warning_dialog = QtWidgets.QMessageBox()
                        warning_dialog.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                        warning_dialog.setText(f"The current data type of column {column_name} is String. Converting to Integer will result in loss of non-numeric data.")
                        warning_dialog.setInformativeText("Do you want to proceed with the conversion?")
                        warning_dialog.setWindowTitle("Data Type Conversion Warning")
                        warning_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
                        warning_dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
                        ret = warning_dialog.exec()

                        if ret == QtWidgets.QMessageBox.StandardButton.Yes:
                            self._data = self._data.with_columns([
                                pl.when(pl.col(column_name).str.contains(r'\d'))
                                .then(pl.col(column_name).str.extract(r'(\d+)').cast(pl.Int64))
                                .otherwise(pl.lit(None).cast(pl.Int64))
                            ])
                        else:
                            return
                    except Exception:
                        raise ValueError(f"Cannot convert column {column_name} to Integer")
                new_dtype = pl.Int64
            elif new_type == "Float":
                if self._data[column_name].dtype == pl.Utf8:
                    try:
                        warning_dialog = QtWidgets.QMessageBox()
                        warning_dialog.setIcon(QtWidgets.QMessageBox.Icon.Warning)
                        warning_dialog.setText(f"The current data type of column {column_name} is String. Converting to Float will result in loss of non-numeric data.")
                        warning_dialog.setInformativeText("Do you want to proceed with the conversion?")
                        warning_dialog.setWindowTitle("Data Type Conversion Warning")
                        warning_dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
                        warning_dialog.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
                        ret = warning_dialog.exec()

                        if ret == QtWidgets.QMessageBox.StandardButton.Yes:
                            self._data = self._data.with_columns([
                                pl.when(pl.col(column_name).str.contains(r'^\d+(\.\d+)?$') | pl.col(column_name).str.contains(r'^\d+(,\d+)?$'))
                                .then(pl.col(column_name).str.replace(",", ".").cast(pl.Float64, strict=False))
                                .otherwise(pl.lit(None).cast(pl.Float64))
                            ])
                        else:
                            return
                    except Exception:
                        raise ValueError(f"Cannot convert column {column_name} to Float")
                new_dtype = pl.Float64
            else:
                raise ValueError("Unsupported data type")

            self.beginResetModel()
            self._data = self._data.with_columns([pl.col(column_name).cast(new_dtype)])
            self.endResetModel()

from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QMenu, QFrame, QSpacerItem,
    QAbstractItemView, QApplication, QSplitter, QScrollArea, QSizePolicy, QToolBar, QInputDialog, QTextEdit, QFontDialog 
)

from PyQt6.QtCore import Qt, QSize 
from PyQt6.QtGui import QAction, QKeySequence
import polars as pl
import os
from PyQt6.QtWidgets import QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SAE Pisan: Small Area Estimation Programming for Statistical Analysis v0.1.1")
        columns = [f"Column {i+1}" for i in range(100)]
        self.data1 = pl.DataFrame({col: [""] * 100 for col in columns})
        self.data2 = pl.DataFrame({
            "Estimated Value": [""] * 100,
            "Standar Error": [""] * 100,
            "CV": [""] * 100
        })

        # Model untuk Sheet 2
        self.model1 = TableModel(self.data1)
        self.model2 = TableModel(self.data2)
        self.path = os.path.join(os.path.dirname(__file__), '..')

        # Inisialisasi UI
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        # Membuat splitter utama untuk membagi halaman menjadi dua bagian (kiri dan kanan)
        self.splitter_main = QSplitter(Qt.Orientation.Horizontal, self)

        # Bagian kiri: QTabWidget untuk dua sheet
        self.tab_widget = QTabWidget(self.splitter_main)  # Ditambahkan ke splitter utama
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.South)
        
        self.show_modeling_sae_dialog = None
        self.show_modeling_saeHB_dialog = None
        self.show_modeling_sae_unit_dialog = None
        self.show_modeling_saeHB_normal_dialog = None
        self.show_modellig_sae_pseudo_dialog = None
        self.show_compute_variable_dialog = None
        self.show_projection_variabel_dialog = None
        

        # Tab pertama (Data Editor)
        self.tab1 = QWidget()
        self.spreadsheet = QTableView(self.tab1)
        self.spreadsheet.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.spreadsheet.setModel(self.model1)

        tab1_layout = QVBoxLayout(self.tab1)
        tab1_layout.addWidget(self.spreadsheet)
        self.spreadsheet.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Tab kedua (Data Output)
        self.tab2 = QWidget()
        self.table_view2 = QTableView(self.tab2)
        self.table_view2.setModel(self.model2)
        self.table_view2.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        tab2_layout = QVBoxLayout(self.tab2)
        tab2_layout.addWidget(self.table_view2)

        # Tab ketiga (Output)
        self.tab3 = QWidget()
        self.scroll_area = QScrollArea(self.tab3)
        
        # Tab output
        self.output_tab = QWidget()
        self.scroll_area = QScrollArea(self.output_tab)
        self.scroll_area.setWidgetResizable(True)
        self.output_container = QWidget()
        self.output_layout = QVBoxLayout(self.output_container)
        self.output_container.setLayout(self.output_layout)
        self.scroll_area.setWidget(self.output_container)
        
        # Atur layout output
        self.output_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.output_layout.setSpacing(0)

        tab3_layout = QVBoxLayout(self.tab3)
        tab3_layout.addWidget(self.scroll_area)

        # Menambahkan tab ke QTabWidget
        self.tab_widget.addTab(self.tab1, "Data Editor")
        self.tab_widget.addTab(self.tab2, "Data Output")
        self.tab_widget.addTab(self.tab3, "Output")  # Tab baru untuk output

        # Membuat layout utama
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        

        # Widget utama dan layout
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Membuat menu bar
        self.menu_bar = self.menuBar()

        # Membuat menu File -> Load dan Save
        self.file_menu = self.menu_bar.addMenu("File")

        self.load_action = QAction("Load File", self)
        self.load_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_O))
        self.load_action.setStatusTip("Ctrl+O")
        
        self.save_action = QAction("Save Data", self)
        self.save_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_S))
        self.save_action.setStatusTip("Ctrl+S")
        
        self.save_data_output_action = QAction("Save Data Output", self)
        self.save_data_output_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_S))
        self.save_action.setStatusTip("Ctrl+Shift+S")
        
        self.save_output_pdf = QAction("Save Output to PDF", self)
        self.save_output_pdf.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_P))
        self.save_output_pdf.setStatusTip("Ctrl+P")

        self.file_menu.addAction(self.load_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_data_output_action)
        self.file_menu.addAction(self.save_output_pdf)

        # Menu "Exploration"
        self.menu_exploration = self.menu_bar.addMenu("Exploration")

        self.action_summary_data = QAction("Summary Data", self)

        self.action_normality_test = QAction("Normality Test", self)

        self.action_correlation = QAction("Correlation", self) 

        self.action_multicollinearity = QAction("Multicollinearity", self)

        self.action_variable_selection = QAction("Variable Selection", self)

        self.menu_exploration.addAction(self.action_summary_data)
        self.menu_exploration.addAction(self.action_normality_test)
        self.menu_exploration.addAction(self.action_correlation)
        self.menu_exploration.addAction(self.action_multicollinearity)
        self.menu_exploration.addAction(self.action_variable_selection)

        # Menu "Graph"
        self.menu_graph = self.menu_bar.addMenu("Graph")

        self.action_scatter_plot = QAction("Scatter Plot", self)

        self.action_correlation_matrix = QAction("Correlation Matrix", self)

        self.action_box_plot = QAction("Box Plot", self)

        self.action_line_plot = QAction("Line Plot", self)

        self.action_histogram = QAction("Histogram", self)

        # Menambahkan plot-plot ke menu Graph
        self.menu_graph.addAction(self.action_scatter_plot)
        self.menu_graph.addAction(self.action_box_plot)
        self.menu_graph.addAction(self.action_line_plot)
        self.menu_graph.addAction(self.action_histogram)



        # Menu "Model"
        menu_model = self.menu_bar.addMenu("Model")

        # Submenu "Area Level"
        menu_area_level = QMenu("Area Level", self)
        action_eblup_area = QAction("EBLUP", self)
        action_hb_beta = QAction("HB Beta", self)
        menu_area_level.addAction(action_eblup_area)
        menu_area_level.addAction(action_hb_beta)

        # Submenu "Unit Level"
        menu_unit_level = QMenu("Unit Level", self)
        action_eblup_unit = QAction("EBLUP", self)
        action_hb_normal = QAction("HB Normal", self)
        menu_unit_level.addAction(action_eblup_unit)
        menu_unit_level.addAction(action_hb_normal)

        # Submenu "Pseudo"
        menu_pseudo = QMenu("Pseudo", self)
        action_eblup_pseudo = QAction("EBLUP", self)
        menu_pseudo.addAction(action_eblup_pseudo)

        # Submenu "Projection"
        menu_projection = QMenu("Projection", self)
        action_projection = QAction("Projection", self)
        menu_projection.addAction(action_projection)


        # Menambahkan submenu ke menu "Model"
        menu_model.addMenu(menu_area_level)
        menu_model.addMenu(menu_unit_level)
        menu_model.addMenu(menu_pseudo)
        menu_model.addMenu(menu_projection)



         # Menu 'Compute'
        menu_compute = self.menu_bar.addMenu("Compute")
        compute_new_var = QAction("Compute New Variable", self)
        menu_compute.addAction(compute_new_var)
        
        # Menu "About"
        menu_about = self.menu_bar.addMenu("About")
        action_about_info = QAction("About This App", self)
        menu_about.addAction(action_about_info)
        

        # Tool Bar
        self.toolBar = QToolBar(self)
        self.toolBar.setIconSize(QSize(45, 35))
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)  # Perbaikan dilakukan di sini
        # Actions for Toolbar
        self.actionLoad_file = QAction(self)
        self.actionLoad_file.setText("Load File")
        self.toolBar.addAction(self.actionLoad_file)
    
    def edit_data_type(self, column_index):
        """Edit the data type of the column at the given index."""
        current_type = self.model1.get_column_type(column_index)
        if current_type==pl.Utf8:
            current_type = "String"
        elif current_type==pl.Int64:
            current_type = "Integer"
        elif current_type==pl.Float64:
            current_type = "Float"
        type_list = ["String", "Integer", "Float"]
        current_index = type_list.index(current_type)
        new_type, ok = QInputDialog.getItem(self, "Edit Data Type", "Select new data type:", type_list, current=current_index)
        if ok and new_type:
            self.model1.set_column_type(column_index, new_type)
            self.update_table(1, self.model1)
    def update_table(self, sheet_number, model):
        """Memperbarui tabel pada sheet tertentu dengan model baru"""
        if sheet_number == 1:
            self.spreadsheet.setModel(model)
            self.model1 = model
        elif sheet_number == 2:
            self.table_view2.setModel(model)
            self.model2 = model
            self.table_view2.resizeColumnsToContents()

from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog, QLabel, QFrame
import polars as pl
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtGui import QPainter, QPdfWriter
from PyQt6.QtCore import QRectF

class FileController:
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view

    def load_file(self):
        """Muat file CSV atau Excel ke model pertama."""
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self.view, "Open File", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )

        if not file_path:  # Jika file tidak dipilih
            return

        try:
            if selected_filter == "CSV Files (*.csv)":
                dialog = CSVOptionsDialog(self.view)
                dialog.file_path = file_path
                dialog.file_label.setText(f"Selected: {file_path}")
                dialog.update_preview()
                file_path, separator, header = dialog.get_csv_options()

                if not file_path:  # Jika file tidak dipilih
                    return

                # Baca data dari CSV dengan atau tanpa header
                if header:
                    data = pl.read_csv(file_path, separator=separator, has_header=True, null_values=["NA", "NULL", "na", "null"])
                else:
                    data = pl.read_csv(file_path, separator=separator, has_header=False, null_values=["NA", "NULL", "na", "null"])
                    data.columns = [f"Column {i+1}" for i in range(data.shape[1])]
            elif selected_filter == "Excel Files (*.xlsx)":
                import pandas as pd
                sheet_names = pd.ExcelFile(file_path).sheet_names
                sheet_name, ok = QInputDialog.getItem(self.view, "Select Sheet", "Sheet:", sheet_names, 0, False)
                if not ok:
                    return
                data = pl.read_excel(file_path, sheet_name=sheet_name)

            self.model1.set_data(data)
            self.view.update_table(1, self.model1)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load file: {str(e)}")

    def save_data(self):
        """Simpan data dari model pertama (Sheet 1)."""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.view, "Save File", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if file_path:

            try:
                if selected_filter == "CSV Files (*.csv)":
                    self.save_as_csv(file_path, self.model1)
                elif selected_filter == "Excel Files (*.xlsx)":
                    self.save_as_excel(file_path, self.model1)
                elif selected_filter == "JSON Files (*.json)":
                    self.save_as_json(file_path, self.model1)
                elif selected_filter == "Text Files (*.txt)":
                    self.save_as_txt(file_path, self.model1)

                QMessageBox.information(self.view, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Failed to save file: {str(e)}")

    def save_data_output(self):
        """Simpan data dari model kedua (Sheet 2)."""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.view, "Save Output Data", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if file_path:

            try:
                if selected_filter == "CSV Files (*.csv)":
                    self.save_as_csv(file_path, self.model2)
                elif selected_filter == "Excel Files (*.xlsx)":
                    self.save_as_excel(file_path, self.model2)
                elif selected_filter == "JSON Files (*.json)":
                    self.save_as_json(file_path, self.model2)
                elif selected_filter == "Text Files (*.txt)":
                    self.save_as_txt(file_path, self.model2)

                QMessageBox.information(self.view, "Success", "Output file saved successfully!")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Failed to save file: {str(e)}")

    def save_as_csv(self, file_path, model):
        """Simpan data sebagai CSV."""
        data = model.get_data()
        data.write_csv(file_path)

    def save_as_excel(self, file_path, model):
        """Simpan data sebagai Excel."""
        data = model.get_data()
        data.write_excel(file_path)

    def save_as_json(self, file_path, model):
        """Simpan data sebagai JSON."""
        data = model.get_data()
        data.write_json(file_path, orient="records", lines=True)

    def save_as_txt(self, file_path, model):
        """Simpan data sebagai file teks."""
        data = model.get_data()
        data.write_csv(file_path, separator="\t")
    
    def export_output_to_pdf(self):
        """Export the content of all widgets in the output layout to a PDF file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.view, "Save PDF", "", "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        pdf_writer = QPdfWriter(file_path)
        painter = QPainter(pdf_writer)

        # Convert cm to points (1 cm = 28.3465 points)
        top_margin = 4 * 28.3465
        side_margin = 3 * 28.3465

        y_offset = top_margin
        page_height = pdf_writer.height()
        page_width = pdf_writer.width()

        def draw_text_multiline(text, y_offset):
            """Helper function to split text and draw it across multiple pages if needed."""
            font_metrics = painter.fontMetrics()
            line_height = font_metrics.lineSpacing()
            lines = text.splitlines()
            for line in lines:
                if y_offset + line_height > page_height - top_margin:
                    pdf_writer.newPage()
                    y_offset = top_margin
                painter.drawText(QRectF(side_margin, y_offset, page_width - 2 * side_margin, line_height),
                                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, line)
                y_offset += line_height
            return y_offset

        for i in range(self.view.output_layout.count()):
            widget = self.view.output_layout.itemAt(i).widget()
            if isinstance(widget, QFrame):
                for j in range(widget.layout().count()):
                    sub_widget = widget.layout().itemAt(j).widget()
                    if isinstance(sub_widget, QLabel) and "<b>Script R:</b>" in sub_widget.text():
                        script_box = widget.layout().itemAt(j + 1).widget()
                        text = script_box.toPlainText()
                        y_offset = draw_text_multiline(text, y_offset)
                    elif isinstance(sub_widget, QLabel) and "<b>Output:</b>" in sub_widget.text():
                        result_box = widget.layout().itemAt(j + 1).widget()
                        text = result_box.toPlainText()
                        y_offset = draw_text_multiline(text, y_offset)
                    elif isinstance(sub_widget, QLabel) and "<b>Plot:</b>" in sub_widget.text():
                        for k in range(j + 1, widget.layout().count()):
                            plot_label = widget.layout().itemAt(k).widget()
                            if isinstance(plot_label, QLabel):
                                image = plot_label.pixmap().toImage()
                                image_height = image.height() * (page_width - 2 * side_margin) / image.width()
                                if y_offset + image_height > page_height - top_margin:
                                    pdf_writer.newPage()
                                    y_offset = top_margin
                                rect = QRectF(side_margin, y_offset, page_width - 2 * side_margin, image_height)
                                painter.drawImage(rect, image)
                                y_offset += image_height

            # Check if y_offset exceeds page height for next widget
            if y_offset > page_height - top_margin:
                pdf_writer.newPage()
                y_offset = top_margin

        painter.end()

        QMessageBox.information(self.view, "Success", "PDF exported successfully!")
        
import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
import polars as pl
import sys

class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.main_window = MainWindow()
        self.file_controller = FileController(self.main_window.model1, self.main_window.model2, self.main_window)

    def test_load_file(self):
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=('test.csv', 'CSV Files (*.csv)')):
            with patch('load_file.CSVOptionsDialog.get_csv_options', return_value=('test.csv', ',', True)):
                with patch('polars.read_csv', return_value=pl.DataFrame({'Column1': [1, 2], 'Column2': [3, 4]})):
                    self.file_controller.load_file()
                    self.assertEqual(self.main_window.model1._data.shape, (2, 2))

    def test_save_data(self):
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=('test.csv', 'CSV Files (*.csv)')):
            with patch('polars.DataFrame.write_csv') as mock_write_csv:
                self.file_controller.save_data()
                mock_write_csv.assert_called_once()

    def test_save_data_output(self):
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=('test_output.csv', 'CSV Files (*.csv)')):
            with patch('polars.DataFrame.write_csv') as mock_write_csv:
                self.file_controller.save_data_output()
                mock_write_csv.assert_called_once()

    def test_export_output_to_pdf(self):
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=('output.pdf', 'PDF Files (*.pdf)')):
            with patch('PyQt6.QtGui.QPdfWriter') as MockPdfWriter:
                mock_pdf_writer_instance = MockPdfWriter.return_value
                self.file_controller.export_output_to_pdf()
                # MockPdfWriter.assert_called_once()
    
    def test_edit_data_type(self):
        self.main_window.model1.set_data(pl.DataFrame({'Column1': [1, 2], 'Column2': [3, 4]}))
        with patch('PyQt6.QtWidgets.QInputDialog.getItem', return_value=('String', True)):
            self.main_window.edit_data_type(0)
            self.assertEqual(self.main_window.model1.get_column_type(0), pl.Utf8)

if __name__ == '__main__':
    unittest.main()
