from PyQt6.QtWidgets import QMessageBox, QFileDialog, QLabel, QFrame
import polars as pl
from view.components.CsvDialogOption import CSVOptionsDialog
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtGui import QPainter, QPdfWriter
from PyQt6.QtCore import QRectF

class FileController:
    """
    Controller class to handle file operations such as loading, saving, and exporting data.
    Attributes:
        model1: The first data model.
        model2: The second data model.
        view: The view component of the MVC architecture.
    Methods:
        __init__(model1, model2, view):
            Initializes the FileController with the given models and view.
        load_file():
            Loads a CSV or Excel file into the first model.
        save_data():
            Saves data from the first model to a file in various formats (CSV, Excel, JSON, Text).
        save_data_output():
            Saves data from the second model to a file in various formats (CSV, Excel, JSON, Text).
        save_as_csv(file_path, model):
            Saves data from the given model as a CSV file.
        save_as_excel(file_path, model):
            Saves data from the given model as an Excel file.
        save_as_json(file_path, model):
            Saves data from the given model as a JSON file.
        save_as_txt(file_path, model):
            Saves data from the given model as a text file with tab-separated values.
        export_output_to_pdf():
            Exports the content of all widgets in the output layout to a PDF file.
    """
    
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
        self.view.save_output_pdf.triggered.connect(self.export_output_to_pdf)  

    def load_file(self):
        """Muat file CSV atau Excel ke model pertama."""
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self.view, "Open File", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )

        if not file_path:  # Jika file tidak dipilih
            return

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
                    data = pl.read_csv(file_path, separator=separator, ignore_errors=True, has_header=True, null_values=["NA", "NULL", "na", "null"])
                else:
                    data = pl.read_csv(file_path, separator=separator, ignore_errors=True, has_header=False, null_values=["NA", "NULL", "na", "null"])
                    data.columns = [f"Column {i+1}" for i in range(data.shape[1])]
            elif selected_filter == "Excel Files (*.xlsx)":
                import pandas as pd
                sheet_names = pd.ExcelFile(file_path).sheet_names
                sheet_name, ok = QInputDialog.getItem(self.view, "Select Sheet", "Sheet:", sheet_names, 0, False)
                if not ok:
                    return
                data = pl.read_excel(file_path, sheet_name=sheet_name)

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
    
    def export_output_to_pdf(self):
        """Export the content of all widgets in the output layout to a PDF file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.view, "Save PDF", "", "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        pdf_writer = QPdfWriter(file_path)
        painter = QPainter(pdf_writer)

        # Convert cm to points (1 cm = 28.3465 points)
        top_margin = 4 * 28.3465
        side_margin = 3 * 28.3465

        y_offset = top_margin
        page_height = pdf_writer.height()
        page_width = pdf_writer.width()

        def draw_text_multiline(text, y_offset):
            """Helper function to split text and draw it across multiple pages if needed."""
            font_metrics = painter.fontMetrics()
            line_height = font_metrics.lineSpacing()
            lines = text.splitlines()
            for line in lines:
                if y_offset + line_height > page_height - top_margin:
                    pdf_writer.newPage()
                    y_offset = top_margin
                painter.drawText(QRectF(side_margin, y_offset, page_width - 2 * side_margin, line_height),
                                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, line)
                y_offset += line_height
            return y_offset

        for i in range(self.view.output_layout.count()):
            widget = self.view.output_layout.itemAt(i).widget()
            if isinstance(widget, QFrame):
                for j in range(widget.layout().count()):
                    sub_widget = widget.layout().itemAt(j).widget()
                    if isinstance(sub_widget, QLabel) and "<b>Script R:</b>" in sub_widget.text():
                        script_box = widget.layout().itemAt(j + 1).widget()
                        text = script_box.toPlainText()
                        y_offset = draw_text_multiline(text, y_offset)
                    elif isinstance(sub_widget, QLabel) and "<b>Output:</b>" in sub_widget.text():
                        result_box = widget.layout().itemAt(j + 1).widget()
                        text = result_box.toPlainText()
                        y_offset = draw_text_multiline(text, y_offset)
                    elif isinstance(sub_widget, QLabel) and "<b>Plot:</b>" in sub_widget.text():
                        for k in range(j + 1, widget.layout().count()):
                            plot_label = widget.layout().itemAt(k).widget()
                            if isinstance(plot_label, QLabel):
                                image = plot_label.pixmap().toImage()
                                image_height = image.height() * (page_width - 2 * side_margin) / image.width()
                                if y_offset + image_height > page_height - top_margin:
                                    pdf_writer.newPage()
                                    y_offset = top_margin
                                rect = QRectF(side_margin, y_offset, page_width - 2 * side_margin, image_height)
                                painter.drawImage(rect, image)
                                y_offset += image_height

            # Check if y_offset exceeds page height for next widget
            if y_offset > page_height - top_margin:
                pdf_writer.newPage()
                y_offset = top_margin

        painter.end()

        QMessageBox.information(self.view, "Success", "PDF exported successfully!")