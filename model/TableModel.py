from PyQt6 import QtCore
from PyQt6.QtCore import Qt
import polars as pl

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            value = self._data[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical:
                return str(section + 1)  # Polars does not have an index like Pandas

    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            row = index.row()
            column = index.column()

            column_name = self._data.columns[column]
            
            # Periksa tipe data kolom
            if self._data[column_name].dtype in [pl.Float64, pl.Int64]:
                try:
                    # Jika value berupa string yang bisa dikonversi menjadi angka
                    if isinstance(value, str):
                        value = float(value)  # Mengonversi value ke float

                    # Set nilai ke DataFrame jika konversi berhasil
                    self._data = self._data.with_column(pl.lit(value).alias(column_name)).with_row(row)
                    return True
                except ValueError:
                    # Jika value tidak bisa dikonversi, tampilkan pesan error
                    print(f"Invalid numeric value: {value} for column {column_name}")
                    return False
            else:
                # Jika kolom adalah string atau tipe lainnya, biarkan nilai sebagai string
                self._data = self._data.with_column(pl.lit(value).alias(column_name)).with_row(row)
                return True

        return False

    def set_data(self, new_data):
        if isinstance(new_data, pl.DataFrame):
            self.beginResetModel()
            self._data = new_data
            self.endResetModel()
        else:
            raise ValueError("Data must be a Polars DataFrame")
    
    def get_data(self):
        return self._data
