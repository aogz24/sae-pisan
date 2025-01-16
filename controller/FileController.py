from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
import polars as pl
from view.components.CsvDialogOption import CSVOptionsDialog
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtWidgets import QInputDialog

class FileController:
    def __init__(self, model1, model2, view):
        self.model1 = model1
        self.model2 = model2
        self.view = view

        # Hubungkan menu bar dengan fungsi
        self.view.load_action.triggered.connect(self.load_file)
        self.view.save_action.triggered.connect(self.save_data)
        self.view.save_data_output_action.triggered.connect(self.save_data_output)
        self.view.actionLoad_file.triggered.connect(self.load_file)
        self.view.actionSave_Data.triggered.connect(self.save_data)  

    def load_file(self):
        """Muat file CSV atau Excel ke model pertama."""
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self.view, "Open File", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )

        if not file_path:  # Jika file tidak dipilih
            return

        progress_dialog = QProgressDialog("Loading file...", "Cancel", 0, 100, self.view)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.show()

        try:
            if selected_filter == "CSV Files (*.csv)":
                dialog = CSVOptionsDialog(self.view)
                dialog.file_path = file_path
                dialog.file_label.setText(f"Selected: {file_path}")
                dialog.update_preview()
                file_path, separator, header = dialog.get_csv_options()

                if not file_path:  # Jika file tidak dipilih
                    return

                # Baca data dari CSV dengan atau tanpa header
                if header:
                    data = pl.read_csv(file_path, separator=separator, has_header=True)
                else:
                    data = pl.read_csv(file_path, separator=separator, has_header=False)
                    data.columns = [f"Column {i+1}" for i in range(data.shape[1])]
            elif selected_filter == "Excel Files (*.xlsx)":
                import pandas as pd
                sheet_names = pd.ExcelFile(file_path).sheet_names
                sheet_name, ok = QInputDialog.getItem(self.view, "Select Sheet", "Sheet:", sheet_names, 0, False)
                if not ok:
                    return
                data = pl.read_excel(file_path, sheet_name=sheet_name)

            for i in range(1, 101):
                QCoreApplication.processEvents()
                progress_dialog.setValue(i)
                if progress_dialog.wasCanceled():
                    break

            self.model1.set_data(data)
            self.view.update_table(1, self.model1)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load file: {str(e)}")
        finally:
            progress_dialog.setValue(100)

    def save_data(self):
        """Simpan data dari model pertama (Sheet 1)."""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.view, "Save File", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if file_path:
            progress_dialog = QProgressDialog("Saving data...", "Cancel", 0, 100, self.view)
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.show()

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
            finally:
                progress_dialog.setValue(100)

    def save_data_output(self):
        """Simpan data dari model kedua (Sheet 2)."""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.view, "Save Output Data", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if file_path:
            progress_dialog = QProgressDialog("Saving output data...", "Cancel", 0, 100, self.view)
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.show()

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
            finally:
                progress_dialog.setValue(100)

    def save_as_csv(self, file_path, model):
        """Simpan data sebagai CSV."""
        data = model.get_data()
        data.write_csv(file_path)

    def save_as_excel(self, file_path, model):
        """Simpan data sebagai Excel."""
        data = model.get_data()
        data.write_excel(file_path)

    def save_as_json(self, file_path, model):
        """Simpan data sebagai JSON."""
        data = model.get_data()
        data.write_json(file_path, orient="records", lines=True)

    def save_as_txt(self, file_path, model):
        """Simpan data sebagai file teks."""
        data = model.get_data()
        data.write_csv(file_path, separator="\t")