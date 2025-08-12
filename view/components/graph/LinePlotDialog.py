from PyQt6.QtWidgets import (
    QToolButton, QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QComboBox,  QTextEdit, QGroupBox, QMessageBox, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QStringListModel, QSize
from PyQt6.QtGui import QIcon
import polars as pl
import re
from model.LinePlot import Lineplot
from controller.Graph.GraphController import LinePlotController
from service.utils.utils import display_script_and_output, check_script
from view.components.DragDropListView import DragDropListView

class LinePlotDialog(QDialog):
    """
    A dialog for creating line plots using selected data from two models.
    Attributes:
        parent (QWidget): The parent widget.
        model1 (Any): The first data model.
        model2 (Any): The second data model.
        all_columns_model1 (list): List of all columns from model1.
        all_columns_model2 (list): List of all columns from model2.
        selected_status (dict): Dictionary to store the status of selected variables.
        data_editor_label (QLabel): Label for the data editor section.
        data_editor_model (QStringListModel): Model for the data editor list view.
        data_editor_list (QListView): List view for the data editor.
        data_output_label (QLabel): Label for the data output section.
        data_output_model (QStringListModel): Model for the data output list view.
        data_output_list (QListView): List view for the data output.
        remove_button1 (QPushButton): Button to remove selected variables.
        add_horizontal_button (QPushButton): Button to add selected variable to the horizontal axis.
        add_vertical_button (QPushButton): Button to add selected variables to the vertical axis.
        horizontal_label (QLabel): Label for the horizontal axis section.
        horizontal_model (QStringListModel): Model for the horizontal axis list view.
        horizontal_list (QListView): List view for the horizontal axis.
        vertical_label (QLabel): Label for the vertical axis section.
        vertical_model (QStringListModel): Model for the vertical axis list view.
        vertical_list (QListView): List view for the vertical axis.
        method_combo (QComboBox): Combo box to select the plotting method.
        script_label (QLabel): Label for the R script section.
        icon_label (QLabel): Label to display the running icon.
        script_box (QTextEdit): Text edit box to display the generated R script.
        run_button (QPushButton): Button to run the generated R script.
    Methods:
        set_model(model1, model2): Sets the data models and updates the data editor and output lists.
        get_column_with_dtype(model): Returns a list of columns with their data types from the given model.
        add_variable_horizontal(): Adds a selected variable to the horizontal axis.
        add_variable_vertical(): Adds selected variables to the vertical axis.
        remove_variable(): Removes selected variables from the horizontal and vertical axes.
        get_selected_horizontal(): Returns a list of selected variables for the horizontal axis.
        get_selected_vertical(): Returns a list of selected variables for the vertical axis.
        accept(): Runs the generated R script and displays the result.
        closeEvent(event): Clears selected variables and script when the dialog is closed.
        generate_r_script(): Generates the R script based on selected variables and method.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Line Plot")

        
        # Menyimpan status variabel yang dipilih
        self.selected_status = {}

        # Layout utama
        self.main_layout = QVBoxLayout(self)

        # Layout konten utama
        content_layout = QHBoxLayout()

        # Layout kiri: Data Editor dan Data Output
        left_layout = QVBoxLayout()

        # Data Editor
        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_model = QStringListModel()
        self.data_editor_list = DragDropListView(parent=self)
        self.data_editor_list.setModel(self.data_editor_model)
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_editor_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        # Data Output
        self.data_output_label = QLabel("Data Output", self)
        self.data_output_model = QStringListModel()
        self.data_output_list = DragDropListView(parent=self)
        self.data_output_list.setModel(self.data_output_model)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_output_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_output_label)
        left_layout.addWidget(self.data_output_list)

        content_layout.addLayout(left_layout)

        # Layout tengah: Tombol
        button_layout1 = QVBoxLayout()
        self.remove_button1 = QPushButton("🡄", self)  
        self.remove_button1.clicked.connect(self.remove_variable) 
        self.remove_button1.setStyleSheet("font-size: 24px;") 
        self.remove_button1.setFixedSize(50,35)
        button_layout1.addStretch(3)
        button_layout1.addWidget(self.remove_button1)
        button_layout1.addStretch(7)

        button_layout2 = QVBoxLayout()
        self.add_horizontal_button = QPushButton("🡆", self)  
        self.add_horizontal_button.clicked.connect(self.add_variable_horizontal)
        self.add_horizontal_button.setFixedSize(50,35)
        self.add_horizontal_button.setStyleSheet("font-size: 24px;")
        self.add_vertical_button = QPushButton("🡆", self)
        self.add_vertical_button.clicked.connect(self.add_variable_vertical)
        self.add_vertical_button.setFixedSize(50,35)
        self.add_vertical_button.setStyleSheet("font-size: 24px;")
        button_layout2.addStretch(1)
        button_layout2.addWidget(self.add_horizontal_button)
        button_layout2.addStretch(5)
        button_layout2.addWidget(self.add_vertical_button)
        button_layout2.addStretch(6)

        # Menambahkan kedua layout tombol ke content_layout
        content_layout.addLayout(button_layout1)
        content_layout.addLayout(button_layout2)

        # Layout kanan: Variabel yang dipilih, metode, dan grafik
        right_layout = QVBoxLayout()

        # Horizontal Axis
        horizontal_layout = QVBoxLayout()
        self.horizontal_label = QLabel("Horizontal Axis", self)
        self.horizontal_model = QStringListModel()
        self.horizontal_list = DragDropListView(parent=self)
        self.horizontal_list.setModel(self.horizontal_model)
        self.horizontal_list.setSelectionMode(QListView.SelectionMode.MultiSelection)

        # Batasi tinggi 
        item_height = 30  
        self.horizontal_list.setFixedHeight(item_height + 4)  

        horizontal_layout.addWidget(self.horizontal_label)
        horizontal_layout.addWidget(self.horizontal_list)
        right_layout.addLayout(horizontal_layout)


        # Vertical Axis
        vertical_layout = QVBoxLayout()
        self.vertical_label = QLabel("Vertical Axis", self)
        self.vertical_model = QStringListModel()
        self.vertical_list = DragDropListView(parent=self)
        self.vertical_list.setModel(self.vertical_model)
        self.vertical_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        vertical_layout.addWidget(self.vertical_label)
        vertical_layout.addWidget(self.vertical_list)
        right_layout.addLayout(vertical_layout,1)


        # Grup metode
        method_group = QGroupBox("Metode")
        method_layout = QVBoxLayout()
        self.method_combo = QComboBox(self)
        self.method_combo.addItems(["Single Lineplot", "Multiple Lineplot"])
        self.method_combo.currentIndexChanged.connect(self.generate_r_script)
        method_layout.addWidget(self.method_combo)
        method_group.setLayout(method_layout)
        right_layout.addWidget(method_group)


        content_layout.addLayout(right_layout)
        self.main_layout.addLayout(content_layout)

        # Horizontal layout for label and icon
        script_layout = QHBoxLayout()
        self.script_label = QLabel("R Script:", self)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Spacer to keep the icon_label on the right end
        spacer = QSpacerItem(40, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        self.toggle_script_button = QToolButton()
        self.toggle_script_button.setIcon(QIcon("assets/more.svg"))
        self.toggle_script_button.setIconSize(QSize(16, 16))
        self.toggle_script_button.setCheckable(True)
        self.toggle_script_button.setChecked(False)
        self.toggle_script_button.clicked.connect(self.toggle_r_script_visibility)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.script_label)
        self.button_layout.addWidget(self.toggle_script_button)
        self.button_layout.setAlignment(self.script_label, Qt.AlignmentFlag.AlignLeft)
        self.button_layout.setAlignment(self.toggle_script_button, Qt.AlignmentFlag.AlignLeft)

        self.script_layout = QHBoxLayout()
        self.script_layout.addLayout(self.button_layout)
        self.script_layout.addStretch()
        self.script_layout.addWidget(self.icon_label)
        self.icon_label.setVisible(False)
        self.script_layout.setAlignment(self.script_label, Qt.AlignmentFlag.AlignLeft)

        self.main_layout.addLayout(self.script_layout)

        self.script_box = QTextEdit()
        self.script_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.script_box.setReadOnly(False)
        self.script_box.setVisible(False)
        self.main_layout.addWidget(self.script_box)

        # Tombol Run
        button_row_layout = QHBoxLayout()
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.accept)
        button_row_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.main_layout.addLayout(button_row_layout)
        
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.vertical_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.horizontal_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
    
    def handle_drop(self, target_widget, items):
        widget_model_map = {
            self.data_editor_list: (self.data_editor_model, self.all_columns_model1),
            self.data_output_list: (self.data_output_model, self.all_columns_model2),
            self.horizontal_list: (self.horizontal_model, None),
            self.vertical_list: (self.vertical_model, None),
        }

        if target_widget not in widget_model_map:
            return
        target_model, allowed_columns = widget_model_map[target_widget]
        current_items = target_model.stringList()

        # Validasi: hanya 1 variabel untuk horizontal
        if target_widget == self.horizontal_list:
            if len(items) > 1 or len(current_items) >= 1:
                QMessageBox.warning(self, "Warning", "You can only add one variable to the horizontal Axis!")
                return

        filtered_items = []
        contains_invalid = False
        rejected_items = []

        for item in items:
            if target_widget in [self.horizontal_list, self.vertical_list]:
                # Tolak jika [String] atau [None]
                if "[String]" in item or "[None]" in item:
                    contains_invalid = True
                    rejected_items.append(item)
                    continue
                filtered_items.append(item)
            else:
                # Editor/output: cocokkan dengan kolom aslinya
                column_name = item.split(" ")[0]
                if allowed_columns and any(column_name == col.split(" ")[0] for col in allowed_columns):
                    filtered_items.append(item)

        if contains_invalid:
            QMessageBox.warning(self, "Warning", "Selected variables must be of type Numeric.")

        # Hapus dari semua model lain
        for _, (model, _) in widget_model_map.items():
            if model == target_model:
                continue
            other_items = model.stringList()
            for item in filtered_items:
                if item in other_items:
                    other_items.remove(item)
            model.setStringList(other_items)

        # Tambahkan ke target jika belum ada
        for item in filtered_items:
            if item not in current_items:
                current_items.append(item)

        # Urutkan kembali jika editor atau output
        if target_widget in [self.data_editor_list, self.data_output_list]:
            original_order = self.all_columns_model1 if target_widget == self.data_editor_list else self.all_columns_model2
            reference_map = {col: i for i, col in enumerate(original_order)}
            current_items = sorted(current_items, key=lambda x: reference_map.get(x, float('inf')))

        target_model.setStringList(current_items)
        self.generate_r_script()


    def set_model(self, model1, model2):
        self.model1 = model1
        self.model2 = model2
        self.data_editor_model.setStringList(self.get_column_with_dtype(model1))
        self.data_output_model.setStringList(self.get_column_with_dtype(model2))
        self.all_columns_model1 = self.get_column_with_dtype(model1)
        self.all_columns_model2 = self.get_column_with_dtype(model2)

    def toggle_r_script_visibility(self):
        """
        Toggles the visibility of the R script text edit area and updates the toggle button text.
        """
        is_visible = self.script_box.isVisible()
        self.script_box.setVisible(not is_visible)
        if not is_visible:
            self.toggle_script_button.setIcon(QIcon("assets/less.svg"))
        else:
            self.toggle_script_button.setIcon(QIcon("assets/more.svg"))

    def get_column_with_dtype(self, model):
        """
        Returns a list of columns with simplified data types:
        String, Numeric, or None.
        """
        self.columns = []
        for col, dtype in zip(model.get_data().columns, model.get_data().dtypes):
            if dtype == pl.Utf8:
                tipe = "String"
            elif dtype == pl.Null:
                tipe = "NULL"
            else:
                tipe = "Numeric"
            self.columns.append(f"{col} [{tipe}]")
        return self.columns
    
    def add_variable_horizontal(self):
        if len(self.horizontal_model.stringList()) >= 1:
            QMessageBox.warning(self, "Warning", "You can only add one variable to the Horizontal Axis!")
            return

        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]

        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a variable first!")
            return

        if len(selected_items) > 1:
            QMessageBox.warning(self, "Warning", "Please select only one variable!")
            return

        item = selected_items[0]

        if "[String]" in item or "[NULL]" in item:
            QMessageBox.warning(self, "Warning", "Selected variable must be of type Numeric.")
            return

        if item in self.data_editor_model.stringList():
            editor_list = self.data_editor_model.stringList()
            editor_list.remove(item)
            self.data_editor_model.setStringList(editor_list)
        elif item in self.data_output_model.stringList():
            output_list = self.data_output_model.stringList()
            output_list.remove(item)
            self.data_output_model.setStringList(output_list)

        self.horizontal_model.setStringList([item])
        self.generate_r_script()


    
    def add_variable_vertical(self):
        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]
        selected_list = self.vertical_model.stringList()

        contains_invalid = any("[String]" in item or "[NULL]" in item for item in selected_items)
        selected_items = [item for item in selected_items if "[String]" not in item and "[NULL]" not in item]

        if contains_invalid:
            QMessageBox.warning(None, "Warning", "Selected variables must be of type Numeric.")

        for item in selected_items:
            if item in self.data_editor_model.stringList():
                editor_list = self.data_editor_model.stringList()
                editor_list.remove(item)
                self.data_editor_model.setStringList(editor_list)
            elif item in self.data_output_model.stringList():
                output_list = self.data_output_model.stringList()
                output_list.remove(item)
                self.data_output_model.setStringList(output_list)

            if item not in selected_list:
                selected_list.append(item)

        self.vertical_model.setStringList(selected_list)
        self.generate_r_script()


    def remove_variable(self):
        # Ambil item terpilih
        selected_indexes = self.horizontal_list.selectedIndexes() + self.vertical_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]

        # Ambil semua list sekarang
        horizontal_list = self.horizontal_model.stringList()
        vertical_list = self.vertical_model.stringList()
        editor_list = self.data_editor_model.stringList()
        output_list = self.data_output_model.stringList()

        for item in selected_items:
            column_name = item.split(" ")[0]

            # Kembalikan ke model asal
            if column_name in [col.split(" ")[0] for col in self.all_columns_model1]:
                if item not in editor_list:
                    editor_list.append(item)
            elif column_name in [col.split(" ")[0] for col in self.all_columns_model2]:
                if item not in output_list:
                    output_list.append(item)

            # Hapus dari horizontal/vertical
            if item in horizontal_list:
                horizontal_list.remove(item)
            if item in vertical_list:
                vertical_list.remove(item)

        # Sort ulang sesuai urutan awal
        editor_list = sorted(editor_list, key=lambda x: self.all_columns_model1.index(x) if x in self.all_columns_model1 else float('inf'))
        output_list = sorted(output_list, key=lambda x: self.all_columns_model2.index(x) if x in self.all_columns_model2 else float('inf'))

        # Update model
        self.horizontal_model.setStringList(horizontal_list)
        self.vertical_model.setStringList(vertical_list)
        self.data_editor_model.setStringList(editor_list)
        self.data_output_model.setStringList(output_list)

        # Update R script
        self.generate_r_script()


    def get_selected_horizontal(self):
        return [
            item.rsplit(" [String]", 1)[0].rsplit(" [Numeric]", 1)[0]
            for item in self.horizontal_model.stringList()
        ]

    def get_selected_vertical(self):
        return [
            item.rsplit(" [String]", 1)[0].rsplit(" [Numeric]", 1)[0]
            for item in self.vertical_model.stringList()
        ]
    
    def accept(self):
        r_script = self.script_box.toPlainText()
        selected_horizontal = self.get_selected_horizontal()
        selected_vertical = self.get_selected_vertical()

        if not selected_horizontal:
            QMessageBox.warning(self, "No Variable", "Please select one variable for the Horizontal Axis.")
            return
        if len(selected_horizontal) > 1:
            QMessageBox.warning(self, "Too Many Variables", "Only one variable is allowed for the Horizontal Axis.")
            return
        if not selected_vertical:
            QMessageBox.warning(self, "No Variable", "Please select at least one variable for the Vertical Axis.")
            return
        if not r_script:
            QMessageBox.warning(self, "Empty Script", "Please generate a script before running.")
            return
        
        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")
        self.icon_label.setVisible(True)

        line_plot = Lineplot(self.model1, self.model2, self.parent)
        controller = LinePlotController(line_plot)
        controller.run_model(r_script)

        if line_plot.error:
            QMessageBox.critical(self, "Line Plot", line_plot.result)
        else:
            QMessageBox.information(self, "Line Plot", "Graph has been generated.")

        # self.parent.add_output(script_text = r_script, result_text = line_plot.result, plot_paths = line_plot.plot)
        display_script_and_output(self.parent, r_script, line_plot.result, line_plot.plot)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)

        self.icon_label.setVisible(False)
        self.run_button.setText("Run")
        self.run_button.setEnabled(True)
        self.close()

    def closeEvent(self, event):
        """Menghapus variabel yang dipilih ketika dialog ditutup."""
        self.horizontal_model.setStringList([]) 
        self.vertical_model.setStringList([])
        self.script_box.setPlainText("")  
        event.accept()

    def generate_r_script(self): 
        # Get selected variables
        selected_var_horizontal = self.get_selected_horizontal()
        selected_var_vertical = self.get_selected_vertical()

        # Get selected method
        method = self.method_combo.currentText()

        r_script = ""

        # Pastikan hanya mengambil elemen pertama untuk horizontal
        selected_var_horizontal = selected_var_horizontal[0] if selected_var_horizontal else None
        if not selected_var_horizontal or not selected_var_vertical:
            self.script_box.setPlainText("")
            return

        # Bersihkan nama horizontal untuk objek (hilangkan spasi & karakter tak valid)
        clean_horizontal = re.sub(r"\W+", "_", selected_var_horizontal.strip("`"))

        # Single Line Plot
        if method == "Single Lineplot":
            for var in selected_var_vertical:
                clean_var = re.sub(r"\W+", "_", var.strip("`"))  # Bersihkan nama untuk objek
                r_script += (
                    f"lineplot_{clean_var} <- ggplot(data, aes(x = `{selected_var_horizontal}`, y = `{var}`)) +\n"
                    f"    geom_line(color = 'darkorange3') +\n"
                    f"    geom_point() +\n"
                    f"    ggtitle(\"Line Plot: {selected_var_horizontal} vs. {var.strip('`')}\") +\n"
                    f"    xlab(\"{selected_var_horizontal}\") +\n"
                    f"    ylab(\"{var.strip('`')}\") +\n"
                    f"    theme_minimal()\n\n"
                )

        # Multiple Line Plot
        elif method == "Multiple Lineplot":
            vertical_vars = ", ".join(f"`{var}`" for var in selected_var_vertical)  # Pakai backticks
            formatted_var_list = ", ".join(var.strip("`") for var in selected_var_vertical)

            r_script = (
                f"data_long <- pivot_longer(data, cols = c({vertical_vars}),\n"
                f"                        names_to = \"variable\", values_to = \"value\")\n\n"
                f"lineplot_{clean_horizontal}_multiple <- ggplot(data_long, aes(x = `{selected_var_horizontal}`, y = value, color = variable)) +\n"
                f"    geom_line() +\n"
                f"    geom_point() +\n"
                f"    ggtitle(\"Multiple Line Plot: {selected_var_horizontal} vs. {formatted_var_list}\") +\n"
                f"    xlab(\"{selected_var_horizontal}\") +\n"
                f"    ylab(\"Value\") +\n"
                f"    theme_minimal()\n"
            )

        self.script_box.setPlainText(r_script)
