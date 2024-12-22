from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
import pandas as pd

class SpreadsheetWidgetModel(QTableWidget):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.main_window = parent  # Reference ke MainWindow
        self.data = data
        self.setRowCount(data.shape[0])  # Set jumlah baris awal
        self.setColumnCount(data.shape[1])  # Set jumlah kolom sesuai data
        self.populate_table()

    def populate_table(self):
        """Isi tabel dengan data dari model."""
        for row in range(self.data.shape[0]):
            for col in range(self.data.shape[1]):
                item = QTableWidgetItem(str(self.data.iloc[row, col]))
                self.setItem(row, col, item)

    def update_table(self, data):
        """Perbarui tabel dengan data baru."""
        self.data = data
        self.setRowCount(data.shape[0])  # Perbarui jumlah baris
        self.setColumnCount(data.shape[1])
        self.setHorizontalHeaderLabels(data.columns.tolist())
        self.populate_table()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Down:
            current_row = self.currentRow()
            if current_row == self.rowCount() - 1:
                print(self.currentColumn())
                self.add_row()
        if event.key() == Qt.Key.Key_Right:
            curent_columns = self.currentColumn()
            if curent_columns == self.columnCount()-1:
                self.add_column()
        super().keyPressEvent(event)

    def add_row(self):
        """Tambahkan baris kosong baru ke tabel."""
        current_row_count = self.rowCount()
        self.setRowCount(current_row_count + 1)
        for col in range(self.columnCount()):
            self.setItem(current_row_count, col, QTableWidgetItem(""))
        self.main_window.add_row(1)  # Panggil metode di MainWindow untuk sinkronisasi
    
    def add_column(self):
        """Tambahkan kolom kosong baru ke tabel."""
        current_column_count = self.columnCount()
        self.setColumnCount(current_column_count + 1)
        for row in range(self.rowCount()):
            self.setItem(row, current_column_count, QTableWidgetItem(""))
        self.main_window.add_column(1)  # Panggil metode di MainWindow untuk sinkronisasi
    
    def get_data(self):
        """Ambil data dari tabel dan kembalikan sebagai DataFrame."""
        data = []
        for row in range(self.rowCount()):
            row_data = []
            for col in range(self.columnCount()):
                item = self.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return pd.DataFrame(data)