from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QMenuBar, QMenu,
    QAbstractItemView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QAction
import polars as pl
from model.TableModel import TableModel
from model.SpreadsheetWidgetModel import SpreadsheetWidgetModel

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
        self.spreadsheet = SpreadsheetWidgetModel(self, self.model1.get_data())
        tab1_layout = QVBoxLayout(self.tab1)
        tab1_layout.addWidget(self.spreadsheet)

        # Membuat widget untuk tab kedua (Sheet 2) dengan QTableView
        self.tab2 = QWidget()
        self.table_view2 = QTableView(self.tab2)
        self.table_view2.setModel(self.model2)
        self.table_view2.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tab2_layout = QVBoxLayout(self.tab2)
        tab2_layout.addWidget(self.table_view2)

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
        action_scatterplot.triggered.connect(lambda: print("Exploration -> Scatterplot selected"))
        action_correlation_matrix = QAction("Correlation Matrix", self)
        action_correlation_matrix.triggered.connect(lambda: print("Exploration -> Correlation Matrix selected"))
        action_box_plot = QAction("Box Plot", self)
        action_box_plot.triggered.connect(lambda: print("Exploration -> Box Plot selected"))
        action_line_plot = QAction("Line Plot", self)
        action_line_plot.triggered.connect(lambda: print("Exploration -> Line Plot selected"))
        action_histogram = QAction("Histogram", self)
        action_histogram.triggered.connect(lambda: print("Exploration -> Histogram selected"))
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
            if model.get_data().shape[0] > 100:
                self.spreadsheet.update_table(model.get_data()[:100, :])
                QMessageBox.information(self.tab_widget,"Informasi", "Only 10,000 records are displayed due to data exceeding 10,000, but full data can be analyzed.")  
            else:
                self.spreadsheet.update_table(model.get_data())
        elif sheet_number == 2:
            self.table_view2.setModel(model)
