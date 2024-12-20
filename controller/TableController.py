from PyQt6.QtWidgets import QMessageBox, QFileDialog
import pandas as pd
from view.CsvDialogOption import CSVOptionsDialog  # Pastikan file dialog ada

class TableController:
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view

        # Hubungkan menu bar dengan fungsi
        self.view.load_action.triggered.connect(self.load_csv)
        self.view.save_action.triggered.connect(self.save_csv)

    def load_csv(self):
        # Tampilkan dialog opsi CSV
        dialog = CSVOptionsDialog(self.view)
        file_path, separator, header = dialog.get_csv_options()

        # Jika pengguna membatalkan atau file tidak dipilih
        if not file_path:
            return

        try:
            # Muat data dari file CSV, tanpa header jika opsi header tidak dipilih
            if header:
                data = pd.read_csv(file_path, sep=separator, header=0)
            else:
                data = pd.read_csv(file_path, sep=separator, header=None)
                data.columns = [f"Column {i+1}" for i in range(data.shape[1])]

            # Memperbarui data untuk kedua sheet
            self.model1.set_data(data)

            # Memperbarui tampilan pada sheet pertama (untuk demo)
            self.view.update_table(1, self.model1)

        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load file: {str(e)}")

    def save_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self.view, "Save CSV File", "", "CSV Files (*.csv)")
        if file_path:
            try:
                data1 = self.model1.get_data()
                data1.to_csv(file_path, index=False)
                QMessageBox.information(self.view, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Failed to save file: {str(e)}")
