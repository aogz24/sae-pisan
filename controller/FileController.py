from PyQt6.QtWidgets import QMessageBox, QFileDialog, QLabel, QFrame
import polars as pl
from view.components.CsvDialogOption import CSVOptionsDialog
from PyQt6.QtCore import Qt, QBuffer, QIODevice
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QLabel, QFrame, QTextEdit, QTableView
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageTemplate, Frame
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
import io

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
        self.view.recent_data.triggered.connect(self.view.load_temp_data)
        self.view.load_secondary_data.triggered.connect(self.load_secondary_data)  

    def load_file(self):
        """Muat file CSV, Excel, atau Text ke model pertama."""
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self.view, "Open File", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;Text Files (*.txt);;TSV Files (*.tsv);;JSON Files (*.json)"
        )

        if not file_path:  # Jika file tidak dipilih
            return

        try:
            if selected_filter in ["CSV Files (*.csv)", "Text Files (*.txt)", "TSV Files (*.tsv)"]:
                dialog = CSVOptionsDialog(self.view)
                dialog.file_path = file_path
                dialog.file_label.setText(f"Selected: {file_path}")
                dialog.update_preview()
                file_path, separator, header = dialog.get_csv_options()

                if not file_path:  # Jika file tidak dipilih
                    return
                
                if separator == r"\t":  # Jika input adalah string literal "\t"
                    separator = "\t"

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
            elif selected_filter == "JSON Files (*.json)":
                data = pl.read_json(file_path)

            self.model1.set_data(data)
            self.view.update_table(1, self.model1)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load file: {str(e)}")
    
    def load_secondary_data(self):
        main_df = self.model1.get_data()
        if main_df is None:
            QMessageBox.warning(self.view, "Warning", "No data loaded in Sheet 1. Please load data first.")
            return
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self.view, "Open File", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;Text Files (*.txt);;TSV Files (*.tsv);;JSON Files (*.json)"
        )

        if not file_path:  # Jika file tidak dipilih
            return

        try:
            if selected_filter in ["CSV Files (*.csv)", "Text Files (*.txt)", "TSV Files (*.tsv)"]:
                dialog = CSVOptionsDialog(self.view)
                dialog.file_path = file_path
                dialog.file_label.setText(f"Selected: {file_path}")
                dialog.update_preview()
                file_path, separator, header = dialog.get_csv_options()

                if not file_path:  # Jika file tidak dipilih
                    return
                
                if separator == r"\t":  # Jika input adalah string literal "\t"
                    separator = "\t"

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
            elif selected_filter == "JSON Files (*.json)":
                data = pl.read_json(file_path)

            merged_data = pl.concat([main_df, data], how="horizontal")
            self.model1.set_data(merged_data)
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
        """Export the content of all widgets in the output layout to a PDF file (menggunakan reportlab untuk tabel)."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.view, "Save PDF", "", "PDF Files (*.pdf)"
        )

        if not file_path:
            return
        
        def add_footer(canvas, doc):
            canvas.saveState()
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
            footer_text = f"Generated by saePisan at {timestamp}"
            canvas.setFont("Helvetica-Oblique", 8)
            width, height = A4
            canvas.drawRightString(width - 30, 20, footer_text)
            canvas.restoreState()
        
        doc = SimpleDocTemplate(
            file_path, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=40, bottomMargin=40
        )
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        doc.addPageTemplates([PageTemplate(id='footer', frames=frame, onPage=add_footer)])
        
        elements = []
        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        
        for i in range(self.view.output_layout.count()):
            item = self.view.output_layout.itemAt(i)
            widget = item.widget()
            if widget is None:
                continue

            if isinstance(widget, QFrame):
                for j in range(widget.layout().count()):
                    sub_widget = widget.layout().itemAt(j).widget()
                    if isinstance(sub_widget, QLabel) and "<b>R Script:</b>" in sub_widget.text():
                        script_box = widget.layout().itemAt(j + 1).widget()
                        text = script_box.toPlainText()
                        elements.append(Paragraph("R Script:", styles["Heading4"]))
                        script_style = ParagraphStyle(
                            name="ScriptStyle",
                            parent=styles["Normal"],
                            fontName="Courier",
                            fontSize=9,
                            leading=12,
                        )
                        elements.append(Paragraph(text.replace("\n", "<br/>"), script_style))
                        elements.append(Spacer(1, 12))
                    elif isinstance(sub_widget, QLabel) and "Output" in sub_widget.text():
                        result_box = widget.layout().itemAt(j + 1).widget()
                        if isinstance(result_box, QTextEdit):
                            text = result_box.toPlainText()
                            elements.append(Paragraph("Output:", styles["Heading4"]))
                            elements.append(Paragraph(text.replace("\n", "<br/>"), normal_style))
                            elements.append(Spacer(1, 12))
                        else:
                            elements.append(Paragraph("Output:", styles["Heading4"]))
                            elements.append(Spacer(1, 12))
                    elif isinstance(sub_widget, QTableView):
                        model = sub_widget.model()
                        if model:
                            columns = [model.headerData(col, Qt.Orientation.Horizontal) for col in range(model.columnCount())]
                            data_rows = []
                            for row in range(model.rowCount()):
                                row_data = []
                                for col in range(model.columnCount()):
                                    index = model.index(row, col)
                                    row_data.append(str(model.data(index)))
                                data_rows.append(row_data)
                            if data_rows:
                                table_data = [columns] + data_rows
                                table = Table(table_data, repeatRows=1)
                                table.setStyle(TableStyle([
                                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                ]))
                                elements.append(table)
                                elements.append(Spacer(1, 12))
                    elif isinstance(sub_widget, QLabel) and "<b>Plot:</b>" in sub_widget.text():
                        for k in range(j + 1, widget.layout().count()):
                            plot_label = widget.layout().itemAt(k).widget()
                            if isinstance(plot_label, QLabel):
                                pixmap = plot_label.pixmap()
                                if pixmap:
                                    buffer = QBuffer()
                                    buffer.open(QIODevice.OpenModeFlag.ReadWrite)
                                    pixmap.toImage().save(buffer, "PNG")
                                    buffer.seek(0)
                                    img = Image(io.BytesIO(buffer.data()), width=400, height=250)
                                    elements.append(img)
                                    elements.append(Spacer(1, 12))
                    elif isinstance(sub_widget, QLabel):
                        text = sub_widget.text().replace("<b>", "").replace("</b>", "")
                        text = text.replace("<i>", "").replace("</i>", "")
                        if "Summary of" in sub_widget.text():
                            summary_style = ParagraphStyle(
                                name="SummaryHeading",
                                parent=styles["Heading1"],
                                alignment=TA_CENTER,
                                fontName="Helvetica-Bold"
                            )
                            elements.append(Paragraph(text, summary_style))
                            elements.append(Spacer(1, 12))
                        elif "Generated on" in sub_widget.text():
                            generated_style = ParagraphStyle(
                                name="GeneratedHeading",
                                parent=styles["Normal"],
                                alignment=2,  # TA_RIGHT is 2
                                fontName="Helvetica-Oblique",  # Italic
                                fontSize=10,
                                textColor=colors.black
                            )
                            elements.append(Paragraph(text, generated_style))
                            elements.append(Spacer(1, 12))
                        else:
                            elements.append(Paragraph(text, normal_style))
                            elements.append(Spacer(1, 12))

        doc.build(elements)
        QMessageBox.information(self.view, "Success", "PDF exported successfully!")