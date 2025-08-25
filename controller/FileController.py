from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QScrollArea, QWidget, QApplication
import polars as pl
from view.components.CsvDialogOption import CSVOptionsDialog
from view.components.ExcelDialogOption import ExcelOptionsDialog
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
from service.command.LoadDataCommand import LoadDataCommand
from service.command.LoadSecondaryDataCommand import LoadSecondaryDataCommand

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

    def open_file(self):
        """Open file CSV, Excel, atau Text and load to first model"""
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
                dialog = ExcelOptionsDialog(self.view)
                dialog.file_path = file_path
                import pandas as pd
                xls = pd.ExcelFile(file_path)
                dialog.sheet_names = xls.sheet_names
                dialog.sheet_combo.addItems(dialog.sheet_names)
                dialog.file_label.setText(f"Selected: {file_path}")
                dialog.update_preview()
                
                file_path, selected_sheet, hdr = dialog.get_excel_options()
                
                if not file_path or not selected_sheet:  # Jika file tidak dipilih
                    return
                data = pl.read_excel(file_path, sheet_name=selected_sheet, has_header=hdr)
                
            elif selected_filter == "JSON Files (*.json)":
                data = pl.read_json(file_path)
            
            return data
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Failed to load file: {str(e)}")
    
    def load_file(self):
        """Load file CSV, Excel, atau Text to first model (Sheet 1) and update tabel."""
        data = self.open_file()
        if data is None:
            return
        else:
            # Create and execute the LoadDataCommand
            command = LoadDataCommand(self.model1, data)
            self.model1.undo_stack.push(command)
            self.view.update_table(1, self.model1)
            QMessageBox.information(self.view, "Success", "File loaded successfully!")
            self.view.autosave_data()
        
    
    def load_secondary_data(self):
        """
        Load file CSV, Excel, atau Text to first model (Sheet 2) for secondary data and update tabel.
        Allows merging data with two options:
        1. Horizontal: Add columns from secondary data to main data
        2. Diagonal: Add rows and unique columns from secondary data to main data
        
        For diagonal merge, the function can:
        - Auto-detect columns with identical names
        - Allow manual column mapping for columns with different names but same meaning
        """

        main_df = self.model1.get_data()
        if main_df is None:
            QMessageBox.warning(self.view, "Warning", "No data loaded in Sheet 1. Please load data first.")
            return
        data = self.open_file()
        if data is None:
            return

        class MergeOptionDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Select Merge Method")
                layout = QVBoxLayout(self)
                label = QLabel("Select data merge method:", self)
                self.combo = QComboBox(self)
                self.combo.addItems(["Horizontal", "Diagonal"])
                explanation = QLabel(
                    "<b>Explanation:</b><br>"
                    "<b>Horizontal (Merge Columns):</b> Combines data horizontally by adding columns from the second file to the main file. "
                    "If there are columns with the same name, the columns from the second file will be suffixed with '_duplicate'.<br><br>"
                    "<b>Diagonal (Merge ColRows):</b> Combines data vertically by adding rows where column has same name and adding columns where column has different name from the second file to the main file. "
                    "If the number of columns is different, the columns will be automatically adjusted."
                )
                explanation.setWordWrap(True)
                ok_btn = QPushButton("OK", self)
                ok_btn.clicked.connect(self.accept)
                layout.addWidget(label)
                layout.addWidget(self.combo)
                layout.addWidget(ok_btn)
                layout.addWidget(explanation)
                layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                self.setLayout(layout)

            def get_option(self):
                return self.combo.currentIndex()

        class ColumnMappingDialog(QDialog):
            def __init__(self, main_columns, sec_columns, same_names=None, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Map Columns for Diagonal Merge")
                self.auto_mappings = []  # Mappings for auto-detected columns
                self.manual_mappings = []  # Manual mappings added by the user
                self.main_columns = main_columns
                self.sec_columns = sec_columns
                self.same_names = same_names or []
                
                # Initialize auto mappings with same name columns
                for col in self.same_names:
                    self.auto_mappings.append((col, col))
                
                # Set dialog size to max 80% of screen size
                screen_size = QApplication.primaryScreen().size()
                max_width = int(screen_size.width() * 0.8)
                max_height = int(screen_size.height() * 0.8)
                self.resize(min(800, max_width), min(600, max_height))
                
                layout = QVBoxLayout(self)
                
                # Add explanation
                explanation = QLabel(
                    "<b>Column Mapping:</b><br>"
                    "This dialog helps you map columns from the secondary data to the main data.<br>"
                    "- Columns with the same name are automatically matched but can be modified.<br>"
                    "- You can add additional column mappings for different column names with the same meaning.<br>"
                    "- Unmapped columns from secondary data will be added as new columns."
                )
                explanation.setWordWrap(True)
                layout.addWidget(explanation)
                layout.addSpacing(10)
                
                # Create scroll area for the main content
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                scroll_content = QWidget()
                scroll_layout = QVBoxLayout(scroll_content)
                
                # Auto-detected mappings section
                if self.same_names:
                    auto_label = QLabel("<b>Auto-detected matches:</b>")
                    auto_label.setWordWrap(True)
                    scroll_layout.addWidget(auto_label)
                    
                    for i, col in enumerate(self.same_names):
                        row_layout = QHBoxLayout()
                        
                        # Source column (secondary data)
                        row_layout.addWidget(QLabel(f"Secondary column: {col}"))
                        
                        row_layout.addWidget(QLabel("maps to"))
                        
                        # Target column selection (main data)
                        target_combo = QComboBox()
                        target_combo.addItems(self.main_columns)
                        target_combo.setCurrentText(col)  # Default to same name
                        target_combo.setProperty("index", i)  # Store index for identification
                        target_combo.setProperty("type", "auto")
                        target_combo.currentTextChanged.connect(self.update_auto_mapping)
                        
                        row_layout.addWidget(target_combo)
                        
                        # Delete button
                        delete_btn = QPushButton("Remove")
                        delete_btn.setProperty("index", i)
                        delete_btn.setProperty("type", "auto")
                        delete_btn.clicked.connect(self.remove_mapping)
                        row_layout.addWidget(delete_btn)
                        
                        scroll_layout.addLayout(row_layout)
                    
                    scroll_layout.addSpacing(10)
                
                # Manual mapping section
                manual_label = QLabel("<b>Add column mapping:</b>")
                manual_label.setWordWrap(True)
                scroll_layout.addWidget(manual_label)
                
                # Get all available columns for mapping
                all_main_cols = list(self.main_columns)
                all_sec_cols = list(self.sec_columns)
                
                # Add mapping controls
                mapping_layout = QHBoxLayout()
                self.sec_combo = QComboBox()
                self.sec_combo.addItems(all_sec_cols)
                self.main_combo = QComboBox()
                self.main_combo.addItems(all_main_cols)
                
                add_btn = QPushButton("Add Mapping")
                add_btn.clicked.connect(self.add_mapping)
                
                mapping_layout.addWidget(QLabel("Secondary column:"))
                mapping_layout.addWidget(self.sec_combo)
                mapping_layout.addWidget(QLabel("maps to"))
                mapping_layout.addWidget(self.main_combo)
                mapping_layout.addWidget(add_btn)
                
                scroll_layout.addLayout(mapping_layout)
                scroll_layout.addSpacing(20)
                
                # Container for manual mappings
                self.manual_container = QWidget()
                self.manual_layout = QVBoxLayout(self.manual_container)
                self.manual_layout.setContentsMargins(0, 0, 0, 0)
                scroll_layout.addWidget(QLabel("<b>Current manual mappings:</b>"))
                scroll_layout.addWidget(self.manual_container)
                
                # Add stretcher to push everything up
                scroll_layout.addStretch()
                
                # Finish setting up scroll area
                scroll_area.setWidget(scroll_content)
                layout.addWidget(scroll_area)
                
                # Buttons at bottom
                btn_layout = QHBoxLayout()
                ok_btn = QPushButton("OK")
                ok_btn.clicked.connect(self.accept)
                cancel_btn = QPushButton("Cancel")
                cancel_btn.clicked.connect(self.reject)
                btn_layout.addWidget(cancel_btn)
                btn_layout.addWidget(ok_btn)
                
                layout.addLayout(btn_layout)
                self.setLayout(layout)
            
            def update_auto_mapping(self):
                # Update auto mapping when target combo box changes
                sender = self.sender()
                index = sender.property("index")
                sec_col = self.same_names[index]
                main_col = sender.currentText()
                
                # Update the mapping
                self.auto_mappings[index] = (sec_col, main_col)
            
            def add_mapping(self):
                if not self.main_combo.count() or not self.sec_combo.count():
                    return
                    
                sec_col = self.sec_combo.currentText()
                main_col = self.main_combo.currentText()
                
                # Check if this mapping already exists
                all_mappings = self.get_all_mappings()
                for src, tgt in all_mappings:
                    if src == sec_col:
                        QMessageBox.warning(self, "Duplicate Mapping", 
                                           f"Secondary column '{sec_col}' is already mapped to '{tgt}'.")
                        return
                
                # Add to manual mappings
                self.manual_mappings.append((sec_col, main_col))
                
                # Add to UI
                self.add_mapping_to_ui(len(self.manual_mappings) - 1, sec_col, main_col)
            
            def add_mapping_to_ui(self, index, sec_col, main_col):
                row_layout = QHBoxLayout()
                
                # Source column (secondary data)
                row_layout.addWidget(QLabel(f"Secondary column: {sec_col}"))
                
                row_layout.addWidget(QLabel("maps to"))
                
                # Target column selection (main data)
                target_combo = QComboBox()
                target_combo.addItems(self.main_columns)
                target_combo.setCurrentText(main_col)
                target_combo.setProperty("index", index)
                target_combo.setProperty("type", "manual")
                target_combo.currentTextChanged.connect(self.update_manual_mapping)
                
                row_layout.addWidget(target_combo)
                
                # Delete button
                delete_btn = QPushButton("Remove")
                delete_btn.setProperty("index", index)
                delete_btn.setProperty("type", "manual")
                delete_btn.clicked.connect(self.remove_mapping)
                
                row_layout.addWidget(delete_btn)
                
                # Add to manual layout
                self.manual_layout.addLayout(row_layout)
            
            def update_manual_mapping(self):
                # Update manual mapping when target combo box changes
                sender = self.sender()
                index = sender.property("index")
                main_col = self.manual_mappings[index][0]
                target_col = sender.currentText()
                
                # Update the mapping
                self.manual_mappings[index] = (main_col, target_col)
            
            def remove_mapping(self):
                # Remove a mapping when delete button is clicked
                sender = self.sender()
                index = sender.property("index")
                mapping_type = sender.property("type")
                
                if mapping_type == "auto":
                    # Remove from auto mappings
                    del self.auto_mappings[index]
                    del self.same_names[index]
                    
                    # Clear and rebuild the UI (simplest approach)
                    # This would require more complex code to properly handle just removing one item
                    # For now, we'll just accept the dialog and reopen it if needed
                    self.accept()
                elif mapping_type == "manual":
                    # Remove from manual mappings
                    del self.manual_mappings[index]
                    
                    # Clear and rebuild all manual mappings UI
                    # This is simpler than trying to remove just one layout
                    for i in reversed(range(self.manual_layout.count())): 
                        item = self.manual_layout.itemAt(i)
                        if item:
                            if item.layout():
                                for j in reversed(range(item.layout().count())):
                                    item.layout().itemAt(j).widget().deleteLater()
                                self.manual_layout.removeItem(item)
                            elif item.widget():
                                item.widget().deleteLater()
                    
                    # Rebuild manual mappings UI
                    for i, (main_col, sec_col) in enumerate(self.manual_mappings):
                        self.add_mapping_to_ui(i, main_col, sec_col)
            
            def get_all_mappings(self):
                # Return both auto-detected and manual mappings
                return self.auto_mappings + self.manual_mappings

        dialog = MergeOptionDialog(self.view)
        if dialog.exec():
            option = dialog.get_option()
        else:
            return

        mapping_columns = None
        if option == 1:  # Diagonal
            # Detect columns with the same name
            main_cols = list(main_df.columns)
            sec_cols = list(data.columns)
            same_names = list(set(main_cols) & set(sec_cols))
            
            # Show column mapping dialog
            col_dialog = ColumnMappingDialog(main_cols, sec_cols, same_names, self.view)
            if col_dialog.exec():
                mapping_columns = col_dialog.get_all_mappings()
            else:
                return

        # Create and execute the LoadSecondaryDataCommand
        command = LoadSecondaryDataCommand(self.model1, main_df, data, option, mapping_columns)
        self.model1.undo_stack.push(command)
        self.view.update_table(1, self.model1)
        QMessageBox.information(self.view, "Success", "Secondary data loaded successfully!")
        self.view.autosave_data()
        
    def save_data(self):
        """Save data from the first model (Sheet 1)."""
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
        """Save data from the first model (Sheet 1)."""
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
        """Save data as CSV."""
        data = model.get_data()
        data.write_csv(file_path)

    def save_as_excel(self, file_path, model):
        """Save data as Excel."""
        data = model.get_data()
        data.write_excel(file_path)

    def save_as_json(self, file_path, model):
        """Save data as JSON."""
        data = model.get_data()
        data.write_json(file_path, orient="records", lines=True)

    def save_as_txt(self, file_path, model):
        """Save data as file teks."""
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
                            max_col_lens = [len(str(col)) for col in columns]
                            for row in range(model.rowCount()):
                                row_data = []
                                for col in range(model.columnCount()):
                                    index = model.index(row, col)
                                    value = model.data(index)
                                    value_str = str(value)
                                    try:
                                        float_val = float(value)
                                        if '.' in value_str and len(value_str) > max_col_lens[col]:
                                            value_str = f"{float_val:.5f}"
                                    except Exception:
                                        pass
                                    row_data.append(value_str)
                                    if len(value_str) > max_col_lens[col]:
                                        max_col_lens[col] = len(value_str)
                                data_rows.append(row_data)
                            if data_rows:
                                table_data = [columns] + data_rows
                                total_len = sum(max_col_lens)
                                max_width = doc.width
                                col_widths = [
                                    max(40, (l / total_len) * max_width) for l in max_col_lens
                                ]
                                table = Table(table_data, repeatRows=1, colWidths=col_widths)
                                table.setStyle(TableStyle([
                                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
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
                                    # Resize image to fit page width if needed
                                    img_width = min(400, doc.width)
                                    img_height = 250 * (img_width / 400)  # maintain aspect ratio
                                    img = Image(io.BytesIO(buffer.data()), width=img_width, height=img_height)
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
                                alignment=2,
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