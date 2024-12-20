from PyQt6.QtWidgets import QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QPushButton, QHBoxLayout, QMenuBar
import pandas as pd
from model.TableModel import TableModel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SAE Pisan v0.1")

        # Inisialisasi model untuk kedua sheet dengan data kosong
        self.model1 = TableModel(pd.DataFrame("", index=range(1000), columns=["Column 1", "Column 2", "Column 3", "Column 4", "Column 5", "Column 6", "Column 7", "Column8"]))
        self.model2 = TableModel(pd.DataFrame("", index=range(1000),columns=["Nilai Estimasi", "Standar Error", "CV"]))

        # Inisialisasi UI
        self.init_ui()

    def init_ui(self):
        # Membuat QTabWidget untuk menampilkan dua sheet secara vertikal
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.South)  # Set tabs at the bottom
        
        # Membuat widget untuk tab pertama (Sheet 1)
        self.tab1 = QWidget()
        self.table_view1 = QTableView(self.tab1)
        self.table_view1.setModel(self.model1)
        tab1_layout = QVBoxLayout(self.tab1)
        tab1_layout.addWidget(self.table_view1)

        # Membuat widget untuk tab kedua (Sheet 2)
        self.tab2 = QWidget()
        self.table_view2 = QTableView(self.tab2)
        self.table_view2.setModel(self.model2)
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
        self.save_action = QAction("Save CSV", self)

        self.file_menu.addAction(self.load_action)
        self.file_menu.addAction(self.save_action)

        # Menetapkan ukuran default
        self.resize(800, 600)

    def switch_to_sheet1(self):
        """Berpindah ke tab pertama (Sheet 1)"""
        self.tab_widget.setCurrentIndex(0)

    def switch_to_sheet2(self):
        """Berpindah ke tab kedua (Sheet 2)"""
        self.tab_widget.setCurrentIndex(1)

    def update_table(self, sheet_number, model):
        """Memperbarui tabel pada sheet tertentu dengan model baru"""
        if sheet_number == 1:
            self.table_view1.setModel(model)
        elif sheet_number == 2:
            self.table_view2.setModel(model)
