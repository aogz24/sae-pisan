from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QApplication
from PyQt6.QtGui import QKeySequence, QUndoStack
from PyQt6.QtCore import Qt
from service.EditDataCommand import EditDataCommand
import pandas as pd

class SpreadsheetWidgetModel(QTableWidget):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.main_window = parent  # Reference ke MainWindow
        self.data = data
        self.setRowCount(data.shape[0])  # Set jumlah baris awal
        self.setColumnCount(data.shape[1])  # Set jumlah kolom sesuai data
        self.setHorizontalHeaderLabels(data.columns.tolist())
        self.populate_table()
        self.setSelectionMode(QTableWidget.SelectionMode.ContiguousSelection)  # Aktifkan seleksi
        
        self.undo_stack = QUndoStack(self)
        self.setRowCount(data.shape[0])
        self.setColumnCount(data.shape[1])
        self.setHorizontalHeaderLabels(data.columns.tolist())
        self.populate_table()
        self.setSelectionMode(QTableWidget.SelectionMode.ContiguousSelection)
        
        # Koneksi sinyal itemChanged ke handler
        self.itemChanged.connect(self.handle_item_changed)
        self.previous_value = None  # Untuk menyimpan nilai sebelumnya
        self.is_updating = False    # Flag untuk mencegah recursive updates
    
    def handle_item_changed(self, item):
        """Handle perubahan nilai dalam sel"""
        if self.is_updating:
            return

        row = item.row()
        column = item.column()
        new_value = item.text()
        
        # Ambil nilai sebelumnya dari DataFrame
        old_value = str(self.data.iloc[row, column])
        
        if new_value != old_value:
            # Buat dan push command ke undo stack
            command = EditDataCommand(self, row, column, old_value, new_value)
            self.undo_stack.push(command)
            
            # Update DataFrame
            self.is_updating = True
            self.data.iloc[row, column] = new_value
            self.is_updating = False

    
    def populate_table(self):
        """Isi tabel dengan data dari model."""
        self.blockSignals(True)  # Block signals sementara mengisi tabel
        for row in range(self.data.shape[0]):
            for col in range(self.data.shape[1]):
                item = QTableWidgetItem(str(self.data.iloc[row, col]))
                self.setItem(row, col, item)
        self.blockSignals(False)

    def update_table(self, data):
        """Perbarui tabel dengan data baru."""
        self.blockSignals(True)
        self.data = data
        self.setRowCount(data.shape[0])
        self.setColumnCount(data.shape[1])
        self.setHorizontalHeaderLabels(data.columns.tolist())
        self.populate_table()
        self.blockSignals(False)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Down and self.currentRow()==self.rowCount() - 1:
            self.add_row()
        elif event.key() == Qt.Key.Key_Right and self.currentColumn()==self.columnCount() - 1:
            self.add_column()
        elif event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selection()
        elif event.matches(QKeySequence.StandardKey.Paste):
            self.paste_selection()
        elif event.matches(QKeySequence.StandardKey.Undo):
            self.undo()
        elif event.matches(QKeySequence.StandardKey.Redo):
            self.redo()
        else:
            super().keyPressEvent(event)

    def add_row(self):
        """Tambahkan baris kosong baru ke tabel."""
        current_row_count = self.rowCount()
        self.setRowCount(current_row_count + 1)
        for col in range(self.columnCount()):
            self.setItem(current_row_count, col, QTableWidgetItem(""))
        self.main_window.add_row(1)  
    
    def add_column(self):
        """Tambahkan kolom kosong baru ke tabel."""
        current_column_count = self.columnCount()
        self.setColumnCount(current_column_count + 1)
        new_column_label = f"Column {current_column_count + 1}"
        self.setHorizontalHeaderItem(current_column_count, QTableWidgetItem(new_column_label))
        for row in range(self.rowCount()):
            self.setItem(row, current_column_count, QTableWidgetItem(""))
        self.main_window.add_column(1)

    def copy_selection(self):
        """Salin data yang dipilih ke clipboard."""
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return

        copied_data = []
        for selection in selected_ranges:
            rows = range(selection.topRow(), selection.bottomRow() + 1)
            cols = range(selection.leftColumn(), selection.rightColumn() + 1)
            # Membuat list untuk setiap baris
            for row in rows:
                row_data = [
                    self.item(row, col).text() if self.item(row, col) else ""
                    for col in cols
                ]
                copied_data.append(row_data)

        # Gabungkan setiap baris dengan tab, dan setiap baris dipisahkan oleh newline
        clipboard_data = "\n".join(["\t".join(row) for row in copied_data])
        print(clipboard_data)  # Debugging output
        QApplication.clipboard().setText(clipboard_data)

    def paste_selection(self):
        """Tempel data dari clipboard ke tabel."""
        clipboard_data = QApplication.clipboard().text()
        if not clipboard_data:
            return

        start_row = self.currentRow()
        start_col = self.currentColumn()
        rows = clipboard_data.split("\n")
        for r, row_data in enumerate(rows):
            cols = row_data.split("\t")
            for c, cell_data in enumerate(cols):
                row = start_row + r
                col = start_col + c
                if row < self.rowCount() and col < self.columnCount():
                    self.setItem(row, col, QTableWidgetItem(cell_data))
    
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
    
    def can_undo(self):
        return self.undo_stack.canUndo()

    def can_redo(self):
        return self.undo_stack.canRedo()

    def undo(self):
        if self.can_undo():
            self.undo_stack.undo()

    def redo(self):
        if self.can_redo():
            self.undo_stack.redo()

    def get_data(self):
        """Ambil data dari tabel dan kembalikan sebagai DataFrame."""
        return self.data.copy()