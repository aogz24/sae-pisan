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
        self.view.save_action.triggered.connect(self.save_data)
        self.view.save_data_output_action.triggered.connect(self.save_data_output)

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

    def save_data(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.view, "Save File", "", "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                # Select the appropriate format based on the file extension
                if selected_filter == "CSV Files (*.csv)":
                    self.save_as_csv(file_path)
                elif selected_filter == "Excel Files (*.xlsx)":
                    self.save_as_excel(file_path)
                elif selected_filter == "JSON Files (*.json)":
                    self.save_as_json(file_path)
                elif selected_filter == "Text Files (*.txt)":
                    self.save_as_txt(file_path)

                QMessageBox.information(self.view, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Failed to save file: {str(e)}")

    def save_as_csv(self, file_path):
        data1 = self.model1.get_data()
        data1.to_csv(file_path, index=False)

    def save_as_excel(self, file_path):
        data1 = self.model1.get_data()
        data1.to_excel(file_path, index=False)

    def save_as_json(self, file_path):
        data1 = self.model1.get_data()
        data1.to_json(file_path, orient="records", lines=True)

    def save_as_txt(self, file_path):
        data1 = self.model1.get_data()
        data1.to_csv(file_path, index=False, sep="\t")

    def save_data_output(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.view, "Save Output Data", "", "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                # Select the appropriate format based on the file extension
                if selected_filter == "CSV Files (*.csv)":
                    self.save_output_as_csv(file_path)
                elif selected_filter == "Excel Files (*.xlsx)":
                    self.save_output_as_excel(file_path)
                elif selected_filter == "JSON Files (*.json)":
                    self.save_output_as_json(file_path)
                elif selected_filter == "Text Files (*.txt)":
                    self.save_output_as_txt(file_path)

                QMessageBox.information(self.view, "Success", "Output file saved successfully!")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Failed to save file: {str(e)}")

    def save_output_as_csv(self, file_path):
        data_output = self.model2.get_data()
        data_output.to_csv(file_path, index=False)

    def save_output_as_excel(self, file_path):
        data_output = self.model2.get_data()
        data_output.to_excel(file_path, index=False)

    def save_output_as_json(self, file_path):
        data_output = self.model2.get_data()
        data_output.to_json(file_path, orient="records", lines=True)

    def save_output_as_txt(self, file_path):
        data_output = self.model2.get_data()
        data_output.to_csv(file_path, index=False, sep="\t")
