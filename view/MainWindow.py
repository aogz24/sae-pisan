from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QMenu,
    QAbstractItemView, QApplication, QSplitter, QScrollArea, QSizePolicy, QToolBar, QInputDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QSize 
from PyQt6.QtGui import QAction, QKeySequence, QIcon
import polars as pl
from model.TableModel import TableModel
import os
from service.table.GoToRow import *
from service.table.GoToColumn import *
from view.components.MenuContext import show_context_menu
from view.components.ModelingSaeDialog import ModelingSaeDialog
from PyQt6.QtWidgets import QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SAE Pisan: Small Area Estimation Programming for Statistical Analysis v0.1.0")

        # Data awal untuk Sheet 1 dan Sheet 2
        self.cek = "cek"
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

        # Inisialisasi UI
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        # Membuat splitter utama untuk membagi halaman menjadi dua bagian (kiri dan kanan)
        self.splitter_main = QSplitter(Qt.Orientation.Horizontal, self)

        # Bagian kiri: QTabWidget untuk dua sheet
        self.tab_widget = QTabWidget(self.splitter_main)  # Ditambahkan ke splitter utama
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.South)
        
        self.show_modeling_sae_dialog = ModelingSaeDialog(self)
        self.show_modeling_sae_dialog.set_model(self.model1)

        # Tab pertama (Sheet 1)
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

        # Tab kedua (Sheet 2)
        self.tab2 = QWidget()
        self.table_view2 = QTableView(self.tab2)
        self.table_view2.setModel(self.model2)
        self.table_view2.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tab2_layout = QVBoxLayout(self.tab2)
        tab2_layout.addWidget(self.table_view2)

        # Menambahkan tab ke QTabWidget
        self.tab_widget.addTab(self.tab1, "Data Editor")
        self.tab_widget.addTab(self.tab2, "Output Data")

        # Bagian kanan: QTabWidget untuk output
        self.output_tab_widget = QTabWidget(self.splitter_main)  # Ditambahkan ke splitter utama
        self.output_tab_widget.setTabPosition(QTabWidget.TabPosition.South)

        # Tab untuk output
        self.output_tab = QWidget()
        self.scroll_area = QScrollArea(self.output_tab)
        self.scroll_area.setWidgetResizable(True)
        self.output_container = QWidget()
        self.output_layout = QVBoxLayout(self.output_container)
        self.output_container.setLayout(self.output_layout)
        self.scroll_area.setWidget(self.output_container)
        output_tab_layout = QVBoxLayout(self.output_tab)
        output_tab_layout.addWidget(self.scroll_area)

        # Set fixed size for widgets added to output layout
        self.output_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.output_layout.setSpacing(10)
        

        # Menambahkan tab ke QTabWidget
        self.output_tab_widget.addTab(self.output_tab, "Output")

        # Membuat layout utama
        layout = QVBoxLayout()
        layout.addWidget(self.splitter_main)

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
        self.save_data_output_action = QAction("Save Data Output", self)
        self.save_data_output_action.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_S))
        self.save_action.setStatusTip("Ctrl+S")

        self.file_menu.addAction(self.load_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_data_output_action)

        # Menu "Exploration"
        self.menu_exploration = self.menu_bar.addMenu("Exploration")

        self.action_summary_data = QAction("Summary Data", self)
        self.action_normality_test = QAction("Normality Test", self)
        self.action_scatterplot = QAction("Scatterplot", self)
        self.action_correlation_matrix = QAction("Correlation Matrix", self)
        self.action_box_plot = QAction("Box Plot", self)
        self.action_line_plot = QAction("Line Plot", self)
        self.action_histogram = QAction("Histogram", self)
        self.action_multicollinearity = QAction("Multicollinearity", self)
        self.action_variable_selection = QAction("Variable Selection", self)
        self.menu_exploration.addAction(self.action_summary_data)
        self.menu_exploration.addAction(self.action_normality_test)
        self.menu_exploration.addAction(self.action_scatterplot)
        self.menu_exploration.addAction(self.action_correlation_matrix)
        self.menu_exploration.addAction(self.action_box_plot)
        self.menu_exploration.addAction(self.action_line_plot)
        self.menu_exploration.addAction(self.action_histogram)
        self.menu_exploration.addAction(self.action_multicollinearity)
        self.menu_exploration.addAction(self.action_variable_selection)

        # Menu "Model"
        menu_model = self.menu_bar.addMenu("Model")

        # Submenu "Area Level"
        menu_area_level = QMenu("Area Level", self)
        action_eblup_area = QAction("EBLUP", self)
        action_eblup_area.triggered.connect(self.show_modeling_sae_dialog.show)
        action_hb_beta = QAction("HB Beta", self)
        action_hb_beta.triggered.connect(lambda: print("Area Level -> HB Beta selected"))
        menu_area_level.addAction(action_eblup_area)
        menu_area_level.addAction(action_hb_beta)

        # Submenu "Unit Level"
        menu_unit_level = QMenu("Unit Level", self)
        action_eblup_unit = QAction("EBLUP", self)
        action_eblup_unit.triggered.connect(lambda: print("Unit Level -> EBLUP selected"))
        action_hb_normal = QAction("HB Normal", self)
        action_hb_normal.triggered.connect(lambda: print("Unit Level -> HB Normal selected"))
        menu_unit_level.addAction(action_eblup_unit)
        menu_unit_level.addAction(action_hb_normal)

        # Submenu "Pseudo"
        menu_pseudo = QMenu("Pseudo", self)
        action_eblup_pseudo = QAction("EBLUP", self)
        action_eblup_pseudo.triggered.connect(lambda: print("Pseudo -> EBLUP selected"))
        menu_pseudo.addAction(action_eblup_pseudo)

        # Submenu "Projection"
        menu_projection = QMenu("Projection", self)
        action_linear_regression = QAction("Linear Regression", self)
        action_linear_regression.triggered.connect(lambda: print("Projection -> Linear Regression selected"))
        action_logistic_regression = QAction("Logistic Regression", self)
        action_logistic_regression.triggered.connect(lambda: print("Projection -> Logistic Regression selected"))
        action_svm = QAction("SVM", self)
        action_svm.triggered.connect(lambda: print("Projection -> SVM selected"))
        action_gboost = QAction("GBoost", self)
        action_gboost.triggered.connect(lambda: print("Projection -> GBoost selected"))
        menu_projection.addAction(action_linear_regression)
        menu_projection.addAction(action_logistic_regression)
        menu_projection.addAction(action_svm)
        menu_projection.addAction(action_gboost)

        # Menambahkan submenu ke menu "Model"
        menu_model.addMenu(menu_area_level)
        menu_model.addMenu(menu_unit_level)
        menu_model.addMenu(menu_pseudo)
        menu_model.addMenu(menu_projection)

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
        self.toolBar.addAction(self.actionSetting)


        # Menetapkan ukuran default
        self.resize(800, 600)

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
            self.show_modeling_sae_dialog.set_model(model)
        elif sheet_number == 2:
            self.table_view2.setModel(model)
            self.model2 = model

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
        menu.exec(header.mapToGlobal(pos))

    def rename_column(self, column_index):
        """Rename the column at the given index."""
        new_name, ok = QInputDialog.getText(self, "Rename Column", "New column name:")
        if ok and new_name:
            self.model1.rename_column(column_index, new_name)
            self.update_table(1, self.model1)