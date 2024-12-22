from PyQt6.QtWidgets import (
    QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QMenuBar,
    QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QAction
import pandas as pd
from model.TableModel import TableModel
from model.SpreadsheetWidgetModel import SpreadsheetWidgetModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SAE Pisan: Small Area Estimation Programming for Statistical Analysis v0.1")

        # Data awal untuk Sheet 1 dan Sheet 2
        columns = [f"Column {i+1}" for i in range(30)]
        self.data1 = pd.DataFrame("", index=range(10), columns=columns)
        self.data2 = pd.DataFrame("", index=range(10), columns=["Estimated Value", "Standar Error", "CV"])

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
        self.file_menu = self.menu_bar.addMenu("File")

        # Membuat menu File -> Load dan Save
        self.load_action = QAction("Load CSV", self)
        self.save_action = QAction("Save Data", self)
        self.save_data_output_action = QAction("Save Data Output", self)

        self.file_menu.addAction(self.load_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_data_output_action)

        # Menetapkan ukuran default
        self.resize(800, 600)

    def add_row(self, sheet_number):
        """Sinkronisasi data ketika baris baru ditambahkan di SpreadsheetWidget."""
        if sheet_number == 1:
            # Tambahkan baris baru di DataFrame data1
            new_row = pd.DataFrame("", index=[self.data1.shape[0]], columns=self.data1.columns)
            self.data1 = pd.concat([self.data1, new_row], ignore_index=True)
        elif sheet_number == 2:
            pass  # Tidak digunakan untuk Sheet 2
    
    def add_column(self, sheet_number):
        """Sinkronisasi data ketika kolom baru ditambahkan di SpreadsheetWidget."""
        if sheet_number == 1:
            # Tambahkan kolom baru di DataFrame data1
            new_column = pd.DataFrame("", index=self.data1.index, columns=[f"Column {self.data1.shape[1] + 1}"])
            self.data1 = pd.concat([self.data1, new_column], axis=1)
        elif sheet_number == 2:
            pass  # Tidak digunakan untuk Sheet 2
    
    def update_table(self, sheet_number, model):
        """Memperbarui tabel pada sheet tertentu dengan model baru"""
        if sheet_number == 1:
            self.spreadsheet.update_table(model.get_data())
        elif sheet_number == 2:
            self.table_view2.setModel(model)
