from PyQt6.QtWidgets import QMessageBox, QFileDialog
import pandas as pd
from view.CsvDialogOption import CSVOptionsDialog


class FileController:
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view

        # Hubungkan menu bar dengan fungsi
        self.view.load_action.triggered.connect(self.load_csv)
        self.view.save_action.triggered.connect(self.save_data)
        self.view.save_data_output_action.triggered.connect(self.save_data_output)

    def load_csv(self):
        """Muat file CSV ke model pertama."""
        dialog = CSVOptionsDialog(self.view)
        file_path, separator, header = dialog.get_csv_options()

        if not file_path:  # Jika file tidak dipilih
            return

        try:
            # Baca data dari CSV dengan atau tanpa header
            if header:
                data = pd.read_csv(file_path, sep=separator, header=0)
            else:
                data = pd.read_csv(file_path, sep=separator, header=None)
                data.columns = [f"Column {i+1}" for i in range(data.shape[1])]

            self.model1.set_data(data)
            self.view.update_table(1, self.model1)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load file: {str(e)}")

    def save_data(self):
        """Simpan data dari model pertama (Sheet 1)."""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.view, "Save File", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                if selected_filter == "CSV Files (*.csv)":
                    self.save_as_csv(file_path, self.model1)
                elif selected_filter == "Excel Files (*.xlsx)":
                    self.save_as_excel(file_path, self.model1)
                elif selected_filter == "JSON Files (*.json)":
                    self.save_as_json(file_path, self.model1)
                elif selected_filter == "Text Files (*.txt)":
                    self.save_as_txt(file_path, self.model1)

                QMessageBox.information(self.view, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Failed to save file: {str(e)}")

    def save_data_output(self):
        """Simpan data dari model kedua (Sheet 2)."""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.view, "Save Output Data", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                if selected_filter == "CSV Files (*.csv)":
                    self.save_as_csv(file_path, self.model2)
                elif selected_filter == "Excel Files (*.xlsx)":
                    self.save_as_excel(file_path, self.model2)
                elif selected_filter == "JSON Files (*.json)":
                    self.save_as_json(file_path, self.model2)
                elif selected_filter == "Text Files (*.txt)":
                    self.save_as_txt(file_path, self.model2)

                QMessageBox.information(self.view, "Success", "Output file saved successfully!")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Failed to save file: {str(e)}")

    def save_as_csv(self, file_path, model):
        """Simpan data sebagai CSV."""
        data = model.get_data()
        data.to_csv(file_path, index=False)

    def save_as_excel(self, file_path, model):
        """Simpan data sebagai Excel."""
        data = model.get_data()
        data.to_excel(file_path, index=False)

    def save_as_json(self, file_path, model):
        """Simpan data sebagai JSON."""
        data = model.get_data()
        data.to_json(file_path, orient="records", lines=True)

    def save_as_txt(self, file_path, model):
        """Simpan data sebagai file teks."""
        data = model.get_data()
        data.to_csv(file_path, index=False, sep="\t")