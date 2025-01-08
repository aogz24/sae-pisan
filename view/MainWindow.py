from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QMenuBar, QMenu,
    QAbstractItemView, QMessageBox, QApplication, QSplitter, QScrollArea, QSizePolicy, QToolBar,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QAction, QKeySequence, QIcon
import polars as pl
from model.TableModel import TableModel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SAE Pisan: Small Area Estimation Programming for Statistical Analysis v0.1")

        # Data awal untuk Sheet 1 dan Sheet 2
        columns = [f"Column {i+1}" for i in range(30)]
        self.data1 = pl.DataFrame({col: [""] * 10 for col in columns})
        self.data2 = pl.DataFrame({
            "Estimated Value": [""] * 10,
            "Standar Error": [""] * 10,
            "CV": [""] * 10
        })

        # Model untuk Sheet 2
        self.model1 = TableModel(self.data1)
        self.model2 = TableModel(self.data2)

        # Inisialisasi UI
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        # Membuat QTabWidget untuk menampilkan dua sheet secara vertikal
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.South)  # Set tabs di bawah

        # Membuat widget untuk tab pertama (Sheet 1) dengan SpreadsheetWidget
        self.tab1 = QWidget()
        self.spreadsheet = QTableView(self.tab1)
        self.spreadsheet.setModel(self.model1)
        tab1_layout = QVBoxLayout(self.tab1)
        tab1_layout.addWidget(self.spreadsheet)

        # Membuat widget untuk tab kedua (Sheet 2) dengan QSplitter horizontal
        self.tab2 = QWidget()
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self.tab2)

        # Menambahkan tabel ke splitter
        self.table_view2 = QTableView(self.splitter)
        self.table_view2.setModel(self.model2)
        self.table_view2.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Menambahkan widget untuk grafik ke splitter dengan QScrollArea
        self.scroll_area = QScrollArea(self.splitter)
        self.scroll_area.setWidgetResizable(True)
        self.graph_container = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_container)
        self.graph_container.setLayout(self.graph_layout)
        self.scroll_area.setWidget(self.graph_container)

        # Layout untuk tab kedua
        tab2_layout = QVBoxLayout(self.tab2)
        tab2_layout.addWidget(self.splitter)

        # Menambahkan tab ke tab widget
        self.tab_widget.addTab(self.tab1, "Data Editor")
        self.tab_widget.addTab(self.tab2, "Output Data")

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

        self.load_action = QAction("Load CSV", self)
        self.save_action = QAction("Save Data", self)
        self.save_data_output_action = QAction("Save Data Output", self)

        self.file_menu.addAction(self.load_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_data_output_action)

        # Menu "Exploration"
        menu_exploration = self.menu_bar.addMenu("Exploration")

        action_summary_data = QAction("Summary Data", self)
        action_summary_data.triggered.connect(lambda: print("Exploration -> Summary Data selected"))
        action_normality_test = QAction("Normality Test", self)
        action_normality_test.triggered.connect(lambda: print("Exploration -> Normality Test selected"))
        action_scatterplot = QAction("Scatterplot", self)
        action_scatterplot.triggered.connect(lambda: print("Exploration -> Scatterplot Test selected"))
        action_correlation_matrix = QAction("Correlation Matrix", self)
        action_correlation_matrix.triggered.connect(lambda: print("Exploration -> Matriks Korelasi Test selected"))
        action_box_plot = QAction("Box Plot", self)
        action_box_plot.triggered.connect(lambda: print("Exploration -> Box plot Test selected"))
        action_line_plot = QAction("Line Plot", self)
        action_line_plot.triggered.connect(lambda: print("Exploration -> Line Plot Test selected"))
        action_histogram = QAction("Histogram", self)
        action_histogram.triggered.connect(lambda: print("Exploration -> Histogram Test selected"))
        action_multicollinearity = QAction("Multicollinearity", self)
        action_multicollinearity.triggered.connect(lambda: print("Exploration -> Multicollinearity selected"))
        action_variable_selection = QAction("Variable Selection", self)
        action_variable_selection.triggered.connect(lambda: print("Exploration -> Variable Selection selected"))

        menu_exploration.addAction(action_summary_data)
        menu_exploration.addAction(action_normality_test)
        menu_exploration.addAction(action_scatterplot)
        menu_exploration.addAction(action_correlation_matrix)
        menu_exploration.addAction(action_box_plot)
        menu_exploration.addAction(action_line_plot)
        menu_exploration.addAction(action_histogram)
        menu_exploration.addAction(action_multicollinearity)
        menu_exploration.addAction(action_variable_selection)

        # Menu "Model"
        menu_model = self.menu_bar.addMenu("Model")

        # Submenu "Area Level"
        menu_area_level = QMenu("Area Level", self)
        action_eblup_area = QAction("EBLUP", self)
        action_eblup_area.triggered.connect(lambda: print("Area Level -> EBLUP selected"))
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
        self.actionLoad_CSV = QAction(self)  # Menggunakan self untuk referensi instance
        icon_load = QIcon("assets/open.svg")
        self.actionLoad_CSV.setIcon(icon_load)
        self.actionLoad_CSV.setText("Load CSV")
        self.toolBar.addAction(self.actionLoad_CSV)

        self.actionSave_Data = QAction(self)  # Menggunakan self untuk referensi instance
        icon_save = QIcon("assets/save.svg")
        self.actionSave_Data.setIcon(icon_save)
        self.actionSave_Data.setText("Save Data")
        self.toolBar.addAction(self.actionSave_Data)

        self.actionUndo = QAction(self)
        icon_undo = QIcon("assets/undo.svg")
        self.actionUndo.setIcon(icon_undo)
        self.actionUndo.setText("Undo")
        self.toolBar.addAction(self.actionUndo)

        self.actionRedo = QAction(self)
        icon_redo = QIcon("assets/redo.svg")
        self.actionRedo.setIcon(icon_redo)
        self.actionRedo.setText("Redo")
        self.toolBar.addAction(self.actionRedo)

        # Add spacer to push following items to the right
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolBar.addWidget(spacer)

        # Add "Setting" button to the right
        self.actionSetting = QAction(self)
        icon_setting = QIcon("assets/setting.svg")
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
