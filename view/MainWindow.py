from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QMenu, QFrame,
    QAbstractItemView, QApplication, QSplitter, QScrollArea, QSizePolicy, QToolBar, QInputDialog, QTextEdit, QFontDialog 
)
from PyQt6.QtCore import Qt, QSize 
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QPixmap
import polars as pl
from model.TableModel import TableModel
import os
from service.table.GoToRow import *
from service.table.GoToColumn import *
from view.components.MenuContext import show_context_menu
from view.components.ModelingSaeEblupAreaDialog import ModelingSaeDialog
from view.components.ModellingSaeHBDialog import ModelingSaeHBDialog
from view.components.ModelingSaeEblupUnitDialog import ModelingSaeUnitDialog
from view.components.ModellingSaeHbNormal import ModelingSaeHBNormalDialog
from view.components.ModelingSaeEblupPseudoDialog import ModelingSaePseudoDialog
from view.components.SummaryDataDialog import SummaryDataDialog
from view.components.NormalityTestDialog import NormalityTestDialog
from view.components.ScatterPlotDialog import ScatterPlotDialog
from view.components.BoxPlotDialog import BoxPlotDialog
from view.components.LinePlotDialog import LinePlotDialog
from view.components.CorrelationMatrikDialog import CorrelationMatrixDialog
from view.components.MulticollinearityDialog import MulticollinearityDialog
from view.components.ComputeVariableDialog import ComputeVariableDialog
from view.components.ProjectionDialog import ProjectionDialog
from service.table.DeleteColumn import confirm_delete_selected_columns
from service.table.AddColumn import show_add_column_before_dialog, show_add_column_after_dialog
from view.components.ProjectionDialog import ProjectionDialog
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
        self.spreadsheet.customContextMenuRequested.connect(lambda pos: show_context_menu(self, pos))
        self.spreadsheet.setModel(self.model1)
        self.spreadsheet.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.spreadsheet.horizontalHeader().customContextMenuRequested.connect(self.show_header_context_menu)
        self.spreadsheet.horizontalHeader().sectionDoubleClicked.connect(self.rename_column)
        self.spreadsheet.verticalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.spreadsheet.verticalHeader().customContextMenuRequested.connect(lambda pos: show_context_menu(self, pos))

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
        self.scroll_area.verticalScrollBar().rangeChanged.connect(lambda: self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum()))
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
        self.show_summary_data_dialog = SummaryDataDialog(self)
        self.action_summary_data.triggered.connect(self.open_summary_data_dialog)

        self.action_normality_test = QAction("Normality Test", self)
        self.show_normality_test_dialog = NormalityTestDialog(self)
        self.action_normality_test.triggered.connect(self.open_normality_test_dialog)

        self.action_correlation = QAction("Correlation", self)  # Mengubah nama menjadi Correlation
        self.show_correlation_matrix_dialog = CorrelationMatrixDialog(self)
        self.action_correlation.triggered.connect(self.open_correlation_matrix_dialog)

        self.action_multicollinearity = QAction("Multicollinearity", self)  # Menambahkan Multicollinearity
        self.show_multicollinearity_dialog = MulticollinearityDialog(self)
        self.action_multicollinearity.triggered.connect(self.open_multicollinearity_dialog)

        self.menu_exploration.addAction(self.action_summary_data)
        self.menu_exploration.addAction(self.action_normality_test)
        self.menu_exploration.addAction(self.action_correlation)
        self.menu_exploration.addAction(self.action_multicollinearity)  # Menambahkan Multicollinearity ke menu Exploration

        # Menu "Graph"
        self.menu_graph = self.menu_bar.addMenu("Graph")

        self.action_scatter_plot = QAction("Scatterplot", self)
        self.action_scatter_plot.triggered.connect(self.open_scatter_plot_dialog)

        self.action_correlation_matrix = QAction("Correlation Matrix", self)
        self.action_correlation_matrix.triggered.connect(self.open_correlation_matrix_dialog)

        self.action_box_plot = QAction("Box Plot", self)
        self.action_box_plot.triggered.connect(self.open_box_plot_dialog)

        self.action_line_plot = QAction("Line Plot", self)
        self.action_line_plot.triggered.connect(self.open_line_plot_dialog)

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
        action_eblup_area.triggered.connect(self.show_modeling_sae_dialog_lazy)
        action_hb_beta = QAction("HB Beta", self)
        action_hb_beta.triggered.connect(self.show_modeling_saeHB_dialog_lazy)
        menu_area_level.addAction(action_eblup_area)
        menu_area_level.addAction(action_hb_beta)

        # Submenu "Unit Level"
        menu_unit_level = QMenu("Unit Level", self)
        action_eblup_unit = QAction("EBLUP", self)
        action_eblup_unit.triggered.connect(self.show_modeling_sae_unit_dialog_lazy)
        action_hb_normal = QAction("HB Normal", self)
        action_hb_normal.triggered.connect(self.show_modeling_saeHB_normal_dialog_lazy)
        menu_unit_level.addAction(action_eblup_unit)
        menu_unit_level.addAction(action_hb_normal)

        # Submenu "Pseudo"
        menu_pseudo = QMenu("Pseudo", self)
        action_eblup_pseudo = QAction("EBLUP", self)
        action_eblup_pseudo.triggered.connect(self.show_modellig_sae_pseudo_dialog_lazy)
        menu_pseudo.addAction(action_eblup_pseudo)

        # Submenu "Projection"
        menu_projection = QMenu("Projection", self)
        action_projection = QAction("Projection", self)
        action_projection.triggered.connect(self.show_projection_variabel_dialog_lazy)
        menu_projection.addAction(action_projection)


        # Menambahkan submenu ke menu "Model"
        menu_model.addMenu(menu_area_level)
        menu_model.addMenu(menu_unit_level)
        menu_model.addMenu(menu_pseudo)
        menu_model.addMenu(menu_projection)

         # Menu 'Compute'
        menu_compute = self.menu_bar.addMenu("Compute")
        compute_new_var = QAction("Compute New Variable", self)
        compute_new_var.triggered.connect(self.show_compute_variable_dialog_lazy)
        menu_compute.addAction(compute_new_var)
        
        # Menu "About"
        menu_about = self.menu_bar.addMenu("About")
        action_about_info = QAction("About This App", self)
        action_about_info.triggered.connect(lambda: print("About -> About This App selected"))
        menu_about.addAction(action_about_info)
        

        # Tool Bar
        self.toolBar = QToolBar(self)
        self.toolBar.setIconSize(QSize(45, 35))
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)  # Perbaikan dilakukan di sini

        # Actions for Toolbar
        self.actionLoad_file = QAction(self)  # Menggunakan self untuk referensi instance
        icon_load = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'open.svg'))
        self.actionLoad_file.setIcon(icon_load)
        self.actionLoad_file.setText("Load File")
        self.toolBar.addAction(self.actionLoad_file)

        self.actionSave_Data = QAction(self)  # Menggunakan self untuk referensi instance
        icon_save = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'save.svg'))
        self.actionSave_Data.setIcon(icon_save)
        self.actionSave_Data.setText("Save Data")
        self.toolBar.addAction(self.actionSave_Data)

        self.actionUndo = QAction(self)
        icon_undo = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'undo.svg'))
        self.actionUndo.setIcon(icon_undo)
        self.actionUndo.setText("Undo")
        self.actionUndo.triggered.connect(self.undo_action)
        self.toolBar.addAction(self.actionUndo)

        self.actionRedo = QAction(self)
        icon_redo = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'redo.svg'))
        self.actionRedo.setIcon(icon_redo)
        self.actionRedo.setText("Redo")
        self.actionRedo.triggered.connect(self.redo_action)
        self.toolBar.addAction(self.actionRedo)
        
        self.actionCompute = QAction(self)
        icon_compute = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'compute.svg'))
        self.actionCompute.setIcon(icon_compute)
        self.actionCompute.setText("Compute New Variable")
        self.actionCompute.triggered.connect(self.show_compute_variable_dialog_lazy)
        self.toolBar.addAction(self.actionCompute)
        
        # Shortcuts for "Go to Start/End Row/Column"
        self.go_to_start_row_action = QAction(self)
        self.go_to_start_row_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Up))
        self.go_to_start_row_action.triggered.connect(lambda : go_to_start_row(self))
        self.addAction(self.go_to_start_row_action)

        self.go_to_end_row_action = QAction(self)
        self.go_to_end_row_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Down))
        self.go_to_end_row_action.triggered.connect(lambda : go_to_end_row(self))
        self.addAction(self.go_to_end_row_action)

        self.go_to_start_column_action = QAction(self)
        self.go_to_start_column_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Left))
        self.go_to_start_column_action.triggered.connect(lambda : go_to_start_column(self))
        self.addAction(self.go_to_start_column_action)

        self.go_to_end_column_action = QAction(self)
        self.go_to_end_column_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Right))
        self.go_to_end_column_action.triggered.connect(lambda : go_to_end_column(self))
        self.addAction(self.go_to_end_column_action)

        # Add spacer to push following items to the right
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolBar.addWidget(spacer)

        # Add "Setting" button to the right
        self.actionSetting = QAction(self)
        icon_setting = QIcon(os.path.join(os.path.dirname(__file__), '..', 'assets', 'setting.svg'))
        self.actionSetting.setIcon(icon_setting)
        self.actionSetting.setText("Setting")
        self.actionSetting.triggered.connect(self.change_font_size)
        self.toolBar.addAction(self.actionSetting)

        # Menu "Settings"
        menu_settings = self.menu_bar.addMenu("Settings")
        action_change_font_size = QAction("Change Font Size", self)
        action_change_font_size.triggered.connect(self.change_font_size)
        menu_settings.addAction(action_change_font_size)


        # Menetapkan ukuran default
        self.resize(800, 600)

    
    def change_font_size(self):
        current_font = self.font()
        font, ok = QFontDialog.getFont(current_font, self, "Select Font Size")
        if ok:
            self.set_font_size(font.pointSize())

    def set_font_size(self, size):
        stylesheet = self.load_stylesheet_with_font_size(size)
        self.setStyleSheet(stylesheet)

    def load_stylesheet_with_font_size(self, size):
        """
        Memuat stylesheet dan mengganti ukuran font global.
        """
        stylesheet_path = os.path.join(self.path, 'assets', 'style', 'style.qss')
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as file:
                stylesheet = file.read()
                stylesheet = stylesheet.replace("font-size: 14px;", f"font-size: {size}px;")
                return stylesheet
        else:
            print(f"Stylesheet tidak ditemukan di {stylesheet_path}")
            return ""
    
    def open_summary_data_dialog(self):
        self.show_summary_data_dialog.set_model(self.model1, self.model2)
        self.show_summary_data_dialog.show()
        
    def open_normality_test_dialog(self):
        self.show_normality_test_dialog.set_model( self.model1, self.model2)
        self.show_normality_test_dialog.show()

    def open_scatter_plot_dialog(self):
        self.show_scatter_plot_dialog.set_model(self.model1, self.model2)
        self.show_scatter_plot_dialog.show()

    def open_line_plot_dialog(self):
        self.show_line_plot_dialog.set_model(self.model1, self.model2)
        self.show_line_plot_dialog.show()
    
    def open_box_plot_dialog(self):
        self.show_box_plot_dialog.set_model(self.model1, self.model2)
        self.show_box_plot_dialog.show()

    def open_correlation_matrix_dialog(self):
        self.show_correlation_matrix_dialog.set_model(self.model1, self.model2)
        self.show_correlation_matrix_dialog.show()
    
    def open_multicollinearity_dialog(self):
        self.show_multicollinearity_dialog.set_model(self.model1, self.model2)
        self.show_multicollinearity_dialog.show()

    def show_modeling_sae_dialog_lazy(self):
        if self.show_modeling_sae_dialog is None:
            self.show_modeling_sae_dialog = ModelingSaeDialog(self)
        self.show_modeling_sae_dialog.set_model(self.model1)
        self.show_modeling_sae_dialog.show()

    def show_modeling_saeHB_dialog_lazy(self):
        if self.show_modeling_saeHB_dialog is None:
            self.show_modeling_saeHB_dialog = ModelingSaeHBDialog(self)
        self.show_modeling_saeHB_dialog.set_model(self.model1)
        self.show_modeling_saeHB_dialog.show()

    def show_modeling_sae_unit_dialog_lazy(self):
        if self.show_modeling_sae_unit_dialog is None:
            self.show_modeling_sae_unit_dialog = ModelingSaeUnitDialog(self)
        self.show_modeling_sae_unit_dialog.set_model(self.model1)
        self.show_modeling_sae_unit_dialog.show()

    def show_modeling_saeHB_normal_dialog_lazy(self):
        if self.show_modeling_saeHB_normal_dialog is None:
            self.show_modeling_saeHB_normal_dialog = ModelingSaeHBNormalDialog(self)
        self.show_modeling_saeHB_normal_dialog.set_model(self.model1)
        self.show_modeling_saeHB_normal_dialog.show()

    def show_modellig_sae_pseudo_dialog_lazy(self):
        if self.show_modellig_sae_pseudo_dialog is None:
            self.show_modellig_sae_pseudo_dialog = ModelingSaePseudoDialog(self)
        self.show_modellig_sae_pseudo_dialog.set_model(self.model1)
        self.show_modellig_sae_pseudo_dialog.show()

    def show_compute_variable_dialog_lazy(self):
        if self.show_compute_variable_dialog is None:
            self.show_compute_variable_dialog = ComputeVariableDialog(self)
        self.show_compute_variable_dialog.set_model(self.model1)
        self.show_compute_variable_dialog.show()

    def show_projection_variabel_dialog_lazy(self):
        if self.show_projection_variabel_dialog is None:
            self.show_projection_variabel_dialog = ProjectionDialog(self)
        self.show_projection_variabel_dialog.set_model(self.model1)
        if self.show_projection_variabel_dialog.show_prerequisites():
            self.show_projection_variabel_dialog.show()

    def add_row(self, sheet_number):
        """Sinkronisasi data ketika baris baru ditambahkan di SpreadsheetWidget."""
        if sheet_number == 1:
            # Tambahkan baris baru di DataFrame data1
            new_row = pl.DataFrame({col: [""] for col in self.data1.columns})
            self.data1 = pl.concat([self.data1, new_row])
        elif sheet_number == 2:
            pass  # Tidak digunakan untuk Sheet 2
    
    def add_column(self, sheet_number):
        """Sinkronisasi data ketika kolom baru ditambahkan di SpreadsheetWidget."""
        if sheet_number == 1:
            # Tambahkan kolom baru di DataFrame data1
            new_column_name = f"Column {self.data1.shape[1] + 1}"
            new_column = pl.DataFrame({new_column_name: [""] * self.data1.shape[0]})
            self.data1 = pl.concat([self.data1, new_column], how="horizontal")
        elif sheet_number == 2:
            pass  # Tidak digunakan untuk Sheet 2
    
    def update_table(self, sheet_number, model):
        """Memperbarui tabel pada sheet tertentu dengan model baru"""
        if sheet_number == 1:
            self.spreadsheet.setModel(model)
            self.model1 = model
            self.spreadsheet.resizeColumnsToContents()
            if self.show_modeling_sae_dialog:
                self.show_modeling_sae_dialog.set_model(model)
            if self.show_modeling_saeHB_dialog:
                self.show_modeling_saeHB_dialog.set_model(model)
            if self.show_modeling_sae_unit_dialog:
                self.show_modeling_sae_unit_dialog.set_model(model)
            if self.show_modeling_saeHB_normal_dialog:
                self.show_modeling_saeHB_normal_dialog.set_model(model)
            if self.show_modellig_sae_pseudo_dialog:
                self.show_modellig_sae_pseudo_dialog.set_model(model)
            if self.show_compute_variable_dialog:
                self.show_compute_variable_dialog.set_model(model)
            if self.show_projection_variabel_dialog:
                self.show_projection_variabel_dialog.set_model(model)
        elif sheet_number == 2:
            self.table_view2.setModel(model)
            self.model2 = model
            self.table_view2.resizeColumnsToContents()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for copy, paste, undo, and redo."""
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selection()
        elif event.matches(QKeySequence.StandardKey.Paste):
            self.paste_selection()
        elif event.matches(QKeySequence.StandardKey.Undo):
            self.undo_action()
        elif event.matches(QKeySequence.StandardKey.Redo):
            self.redo_action()
        else:
            super().keyPressEvent(event)

    def copy_selection(self):
        """Copy selected cells to clipboard."""
        selection = self.spreadsheet.selectionModel().selectedIndexes()
        if selection:
            data = '\n'.join(['\t'.join([self.model1.data(index, Qt.ItemDataRole.DisplayRole) for index in row]) for row in self.group_by_row(selection)])
            clipboard = QApplication.clipboard()
            clipboard.setText(data)

    def paste_selection(self):
        """Paste clipboard content to selected cells."""
        clipboard = QApplication.clipboard()
        data = clipboard.text().split('\n')
        selection = self.spreadsheet.selectionModel().selectedIndexes()
        if selection:
            start_row = selection[0].row()
            start_col = selection[0].column()
            for i, row in enumerate(data):
                for j, value in enumerate(row.split('\t')):
                    index = self.model1.index(start_row + i, start_col + j)
                    self.model1.setData(index, value, Qt.ItemDataRole.EditRole)

    def undo_action(self):
        """Undo the last action."""
        self.model1.undo()

    def redo_action(self):
        """Redo the last undone action."""
        self.model1.redo()

    def group_by_row(self, selection):
        """Group selected indexes by row."""
        rows = {}
        for index in selection:
            if index.row() not in rows:
                rows[index.row()] = []
            rows[index.row()].append(index)
        return [rows[row] for row in sorted(rows)]
    
    def show_output(self, title, content):
        """Display output in the Output tab"""
        label = QLabel(content)
        self.output_layout.addWidget(label)
        self.output_tab_widget.setCurrentIndex(0)

    def show_header_context_menu(self, pos):
        """Show context menu for header."""
        header = self.spreadsheet.horizontalHeader()
        logical_index = header.logicalIndexAt(pos)
        menu = QMenu(self)
        rename_action = QAction("Rename Column", self)
        rename_action.triggered.connect(lambda: self.rename_column(logical_index))
        menu.addAction(rename_action)
        
        edit_type_action = QAction("Edit Data Type", self)
        edit_type_action.triggered.connect(lambda: self.edit_data_type(logical_index))
        menu.addAction(edit_type_action)
        
        selection = self.spreadsheet.selectionModel().selectedIndexes()
        has_selection = bool(selection)
        
        delete_column_action = QAction("Delete Column", self)
        delete_column_action.triggered.connect(lambda : confirm_delete_selected_columns(self))
        delete_column_action.setEnabled(has_selection)
        menu.addAction(delete_column_action)
        
        add_column_before_action = QAction("Add Column Before", self)
        add_column_before_action.triggered.connect(lambda: show_add_column_before_dialog(self))
        add_column_before_action.setEnabled(has_selection)
        menu.addAction(add_column_before_action)
        
        add_column_after_action = QAction("Add Column After", self)
        add_column_after_action.triggered.connect(lambda: show_add_column_after_dialog(self))
        add_column_after_action.setEnabled(has_selection)
        menu.addAction(add_column_after_action)
        
        menu.exec(header.mapToGlobal(pos))

    def rename_column(self, column_index):
        """Rename the column at the given index."""
        current_name = self.model1.headerData(column_index, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
        new_name, ok = QInputDialog.getText(self, "Rename Column", "New column name:", text=current_name)
        if ok and new_name:
            self.model1.rename_column(column_index, new_name)
            self.update_table(1, self.model1)

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
    
    def set_path(self, path):
        self.path=path
    
    def add_output(self, script_text, result_text=None, plot_paths=None):
        """Fungsi untuk menambahkan output baru ke layout dalam bentuk card"""
        # Membuat frame sebagai card
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        # Layout vertikal untuk card
        card_layout = QVBoxLayout(card_frame)
        card_layout.setSpacing(8)

        # Bagian Script R
        label_script = QLabel("<b>Script R:</b>")
        label_script.setStyleSheet("color: #333; margin-bottom: 5px;")
        script_box = QTextEdit()
        script_box.setPlainText(script_text)
        script_box.setReadOnly(True)
        script_box.setStyleSheet("""
            QTextEdit {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-family: Consolas, Courier New, monospace;
            }
        """)
        script_box.setFixedHeight(script_box.fontMetrics().lineSpacing() * (script_text.count('\n') + 3))

        # Tambahkan elemen teks ke layout card
        card_layout.addWidget(label_script)
        card_layout.addWidget(script_box)

        # Bagian Output (jika ada)
        if result_text:
            label_output = QLabel("<b>Output:</b>")
            label_output.setStyleSheet("color: #333; margin-top: 10px; margin-bottom: 5px;")
            result_box = QTextEdit()
            result_box.setPlainText(result_text)
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
            result_box.setFixedHeight(result_box.fontMetrics().lineSpacing() * (result_text.count('\n') + 3))

            card_layout.addWidget(label_output)
            card_layout.addWidget(result_box)

        # Bagian Plot (jika ada)
        if plot_paths:
            label_plot = QLabel("<b>Plot:</b>")
            label_plot.setStyleSheet("color: #333; margin-top: 10px; margin-bottom: 5px;")
            card_layout.addWidget(label_plot)

            # Tambahkan semua plot ke dalam layout
            for plot_path in plot_paths:
                if os.path.exists(plot_path):
                    pixmap = QPixmap(plot_path)
                    label = QLabel()
                    label.setPixmap(pixmap)
                    label.setFixedSize(700, 500)  # Ukuran tetap untuk gambar
                    label.setScaledContents(True)
                    label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
                    card_layout.addWidget(label)

        # Tambahkan card ke layout utama
        self.output_layout.addWidget(card_frame)
        self.output_layout.addStretch()

        # Hapus file sementara setelah ditampilkan
        if plot_paths:
            for plot_path in plot_paths:
                if os.path.exists(plot_path):
                    os.remove(plot_path)