from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QCheckBox, QTextEdit, QGroupBox, QSizePolicy, QMessageBox, QSpacerItem, QToolButton
)
from PyQt6.QtCore import Qt, QStringListModel, QSize
from PyQt6.QtGui import QIcon
import polars as pl
from model.NormalityTest import NormalityTest
from controller.Eksploration.EksplorationController import NormalityTestController
from service.utils.utils import display_script_and_output
from view.components.DragDropListView import DragDropListView
import re

class NormalityTestDialog(QDialog):
    """z
    A dialog for performing normality tests on selected variables from two data models.
    
    Attributes:
        parent (QWidget): The parent widget.
        model1 (Any): The first data model.
        model2 (Any): The second data model.
        all_columns_model1 (list): List of all columns in the first data model.
        all_columns_model2 (list): List of all columns in the second data model.
        selected_status (dict): Dictionary to store the status of selected variables.
        data_editor_label (QLabel): Label for the data editor section.
        data_editor_model (QStringListModel): Model for the data editor list view.
        data_editor_list (DragDropListView): List view for the data editor.
        data_output_label (QLabel): Label for the data output section.
        data_output_model (QStringListModel): Model for the data output list view.
        data_output_list (DragDropListView): List view for the data output.
        add_button (QPushButton): Button to add selected variables.
        remove_button (QPushButton): Button to remove selected variables.
        selected_label (QLabel): Label for the selected variables section.
        selected_model (QStringListModel): Model for the selected variables list view.
        selected_list (DragDropListView): List view for the selected variables.
        shapiro_checkbox (QCheckBox): Checkbox for the Shapiro-Wilk test.
        jarque_checkbox (QCheckBox): Checkbox for the Jarque-Bera test.
        lilliefors_checkbox (QCheckBox): Checkbox for the Lilliefors test.
        histogram_checkbox (QCheckBox): Checkbox for displaying histograms.
        qqplot_checkbox (QCheckBox): Checkbox for displaying Q-Q plots.
        script_layout (QHBoxLayout): Layout for the R script section.
        script_label (QLabel): Label for the R script section.
        icon_label (QLabel): Label for the running icon.
        script_box (QTextEdit): Text box for displaying the generated R script.
        run_button (QPushButton): Button to run the normality test.
    
    Methods:
        __init__(parent): Initializes the dialog and its components.
        set_model(model1, model2): Sets the data models and updates the data editor and output lists.
        get_column_with_dtype(model): Returns a list of columns with their data types from the given model.
        add_variable(): Adds selected variables to the selected list and updates the R script.
        remove_variable(): Removes selected variables from the selected list and updates the R script.
        get_selected_columns(): Returns a list of selected columns without their data types.
        generate_r_script(): Generates the R script based on selected variables, methods, and graph options.
        accept(): Runs the normality test using the generated R script and displays the results.
        closeEvent(event): Resets the dialog when it is closed.
        handle_drop(target_widget, items): Handles the drop event for drag-and-drop functionality.
        toggle_r_script_visibility(): Toggles the visibility of the R script text edit area.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Normality Test")

        # Store selected variable status
        self.selected_status = {}

        # Main layout
        self.main_layout = QVBoxLayout(self)

        # Main content layout
        content_layout = QHBoxLayout()

        # Left layout: Data Editor and Data Output
        left_layout = QVBoxLayout()

        # Data Editor
        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_model = QStringListModel()
        self.data_editor_list =  DragDropListView(parent=self)
        self.data_editor_list.setModel(self.data_editor_model)
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_editor_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        # Data Output
        self.data_output_label = QLabel("Data Output", self)
        self.data_output_model = QStringListModel()
        self.data_output_list =  DragDropListView(parent=self)
        self.data_output_list.setModel(self.data_output_model)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_output_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_output_label)
        left_layout.addWidget(self.data_output_list)

        content_layout.addLayout(left_layout)

        # Middle layout: Buttons
        button_layout = QVBoxLayout()
        self.add_button = QPushButton("🡆", self)  
        self.add_button.clicked.connect(self.add_variable)
        self.add_button.setFixedSize(50, 35) 
        self.add_button.setStyleSheet("font-size: 24px;")  
        self.remove_button = QPushButton("🡄", self)  
        self.remove_button.clicked.connect(self.remove_variable)
        self.remove_button.setFixedSize(50, 35)
        self.remove_button.setStyleSheet("font-size: 24px;") 
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        content_layout.addLayout(button_layout)

        # Right layout: Selected variables, methods, and graphs
        right_layout = QVBoxLayout()
        self.selected_label = QLabel("Variables", self)
        self.selected_model = QStringListModel()
        self.selected_list =  DragDropListView(parent=self)
        self.selected_list.setModel(self.selected_model)
        self.selected_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        # Method group with checkboxes
        method_group = QGroupBox("Methods")
        method_layout = QVBoxLayout()
        self.shapiro_checkbox = QCheckBox("Shapiro-Wilk")
        self.jarque_checkbox = QCheckBox("Jarque-Bera")
        self.lilliefors_checkbox = QCheckBox("Lilliefors")
        self.shapiro_checkbox.stateChanged.connect(self.generate_r_script)
        self.jarque_checkbox.stateChanged.connect(self.generate_r_script)
        self.lilliefors_checkbox.stateChanged.connect(self.generate_r_script)
        method_layout.addWidget(self.shapiro_checkbox)
        method_layout.addWidget(self.jarque_checkbox)
        method_layout.addWidget(self.lilliefors_checkbox)
        method_group.setLayout(method_layout)
        right_layout.addWidget(method_group)

        # Graph group
        graph_group = QGroupBox("Graph")
        graph_layout = QVBoxLayout()
        self.histogram_checkbox = QCheckBox("Histogram", self)
        self.histogram_checkbox.stateChanged.connect(self.generate_r_script)
        self.qqplot_checkbox = QCheckBox("Q-Q Plot", self)
        self.qqplot_checkbox.stateChanged.connect(self.generate_r_script)
        graph_layout.addWidget(self.histogram_checkbox)
        graph_layout.addWidget(self.qqplot_checkbox)
        graph_group.setLayout(graph_layout)
        right_layout.addWidget(graph_group)

        content_layout.addLayout(right_layout)
        self.main_layout.addLayout(content_layout)

        self.script_layout = QHBoxLayout() 
        self.script_label = QLabel("R Script:", self)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

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

        # Run button
        button_row_layout = QHBoxLayout()
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.accept)
        button_row_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.main_layout.addLayout(button_row_layout)

        self.data_editor_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.selected_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

    def handle_drop(self, target_widget, items):
        # Mapping widget to model
        widget_model_map = {
            self.data_editor_list: (self.data_editor_model, self.all_columns_model1),
            self.data_output_list: (self.data_output_model, self.all_columns_model2),
            self.selected_list: (self.selected_model, None),
        }

        if target_widget not in widget_model_map:
            return

        target_model, allowed_columns = widget_model_map[target_widget]
        current_items = target_model.stringList()

        filtered_items = []
        contains_string = any("[String]" in item or "[NULL]" in item for item in items)

        for item in items:
            # Tolak jika String atau None
            if "[String]" in item or "[NULL]" in item:
                continue

            if target_widget == self.selected_list:
                filtered_items.append(item)
            else:
                column_name = item.split(" ")[0]
                if allowed_columns and column_name in [col.split(" ")[0] for col in allowed_columns]:
                    filtered_items.append(item)

        # ❗️Warning kalau ada String atau None
        if contains_string:
            QMessageBox.warning(self, "Warning", "Selected variables must be of type Numeric.")

        # Tambahkan item yang valid ke target
        for item in filtered_items:
            if item not in current_items:
                current_items.append(item)

        # Hapus dari model lain
        for other_widget, (model, _) in widget_model_map.items():
            if model == target_model:
                continue
            other_items = model.stringList()
            for item in filtered_items:
                if item in other_items:
                    other_items.remove(item)
            model.setStringList(other_items)

        # Urutkan kembali
        if target_widget == self.data_editor_list:
            ordered = [col for col in self.all_columns_model1 if col in current_items]
            target_model.setStringList(ordered)
        elif target_widget == self.data_output_list:
            ordered = [col for col in self.all_columns_model2 if col in current_items]
            target_model.setStringList(ordered)
        else:
            target_model.setStringList(current_items)

        self.generate_r_script()

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
    

    def set_model(self, model1, model2):
        self.model1 = model1
        self.model2 = model2
        self.data_editor_model.setStringList(self.get_column_with_dtype(model1))
        self.data_output_model.setStringList(self.get_column_with_dtype(model2))
        self.all_columns_model1 = self.get_column_with_dtype(model1)
        self.all_columns_model2 = self.get_column_with_dtype(model2)


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

    
    def add_variable(self):
        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]
        selected_list = self.selected_model.stringList()

        contains_invalid = any("[String]" in item or "[NULL]" in item for item in selected_items)

        selected_items = [item for item in selected_items if "[Numeric]" in item]

        # Tampilkan warning jika ada yang tidak valid
        if contains_invalid:
            QMessageBox.warning(self, "Warning", "Selected variables must be of type Numeric.")

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

        self.selected_model.setStringList(selected_list)
        self.generate_r_script()


    def remove_variable(self):
        selected_indexes = self.selected_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]
        selected_list = self.selected_model.stringList()

        for item in selected_items:
            column_name = item.split(' ')[0]
            if column_name in [col.split(' ')[0] for col in self.all_columns_model1]:
                editor_list = self.data_editor_model.stringList()
                editor_list.append(item)
                self.data_editor_model.setStringList(editor_list)
            elif column_name in [col.split(' ')[0] for col in self.all_columns_model2]:
                output_list = self.data_output_model.stringList()
                output_list.append(item)
                self.data_output_model.setStringList(output_list)

            if item in selected_list:
                selected_list.remove(item)

        self.selected_model.setStringList(selected_list)
        self.generate_r_script()

    def remove_variable(self):
        """
        Removes selected variables from the selected list and generates the R script.
        """
        selected_indexes = self.selected_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]

        selected_list = self.selected_model.stringList()
        editor_list = self.data_editor_model.stringList()
        output_list = self.data_output_model.stringList()

        for item in selected_items:
            column_name = item.split(" ")[0]

            # Check if the item belongs to model1 (editor) or model2 (output)
            if column_name in [col.split(" ")[0] for col in self.all_columns_model1]:
                if item not in editor_list:
                    editor_list.append(item)
                    # Re-sort according to all_columns_model1
                    editor_list = [col for col in self.all_columns_model1 if col in editor_list]

            elif column_name in [col.split(" ")[0] for col in self.all_columns_model2]:
                if item not in output_list:
                    output_list.append(item)
                    # Re-sort according to all_columns_model2
                    output_list = [col for col in self.all_columns_model2 if col in output_list]

            # Remove from selected
            if item in selected_list:
                selected_list.remove(item)

        self.selected_model.setStringList(selected_list)
        self.data_editor_model.setStringList(editor_list)
        self.data_output_model.setStringList(output_list)
        self.generate_r_script()
    
    def get_selected_columns(self):
        return [item.rsplit(" [String]", 1)[0].rsplit(" [Numeric]", 1)[0] for item in self.selected_model.stringList()]

    
    def generate_r_script(self):
        def make_safe_object_name(raw):
            name = re.sub(r'\W+', '_', raw)          # non-alphanumeric jadi underscore
            name = re.sub(r'_+', '_', name)          # gabungkan underscore beruntun
            name = name.strip('_')                   # buang underscore di pinggir
            if re.match(r'^\d', name):               # kalau mulai angka, prefix
                name = f"v_{name}"
            return name or "var"

        def escape_title(raw):
            return raw.replace("'", "\\'")  # escape single quote agar aman di string R

        selected_vars = self.get_selected_columns()
        if not selected_vars:
            self.script_box.setPlainText("")
            return

        selected_methods = []
        if self.shapiro_checkbox.isChecked():
            selected_methods.append("shapiro")
        if self.jarque_checkbox.isChecked():
            selected_methods.append("jarque_bera")
        if self.lilliefors_checkbox.isChecked():
            selected_methods.append("lilliefors")

        if not selected_methods:
            self.script_box.setPlainText("")
            return

        show_histogram = self.histogram_checkbox.isChecked()
        show_qqplot = self.qqplot_checkbox.isChecked()

        lines = []

        for var in selected_vars:
            safe_name = make_safe_object_name(var)
            title_safe = escape_title(var)
            aes_var = f"`{var}`"

            for method in selected_methods:
                if method == "shapiro":
                    lines.append(
                        f"normality_results_{safe_name}_shapiro <- shapiro.test(data${aes_var})"
                    )
                elif method == "jarque_bera":
                    lines.append(
                        f"normality_results_{safe_name}_jarque <- tseries::jarque.bera.test(data${aes_var})"
                    )
                elif method == "lilliefors":
                    lines.append(
                        f"normality_results_{safe_name}_lilliefors <- nortest::lillie.test(data${aes_var})"
                    )

            if show_histogram:
                lines.append(
                    f"histogram_{safe_name} <- ggplot(data, aes(x = {aes_var})) +\n"
                    f"    geom_histogram(bins = 10, color = 'black', fill = 'darkorange3') +\n"
                    f"    ggtitle('Histogram of {title_safe}') +\n"
                    f"    xlab('{title_safe}') +\n"
                    f"    ylab('Frequency')"
                )

            if show_qqplot:
                lines.append(
                    f"qqplot_{safe_name} <- ggplot(data, aes(sample = {aes_var})) +\n"
                    f"    stat_qq() +\n"
                    f"    stat_qq_line(color = 'darkorange3') +\n"
                    f"    ggtitle('Q-Q Plot of {title_safe}') +\n"
                    f"    xlab('Theoretical Quantiles') +\n"
                    f"    ylab('Sample Quantiles')"
                )

        r_script = "\n\n".join(lines) + "\n"
        self.script_box.setPlainText(r_script)


    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            QMessageBox.warning(self, "Empty Script", "Please generate a script before running.")
            return
        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")
        self.icon_label.setVisible(True)
        normality_test = NormalityTest(self.model1, self.model2, self.get_selected_columns())
        print("Plot:", normality_test.plot)
        controller = NormalityTestController(normality_test)
        controller.run_model(r_script)

        if not normality_test.error:
            QMessageBox.information(self, "Normality Test", "Exploration has been completed.")
        else:
            QMessageBox.critical(self, "Normality Test", normality_test.result) 
        print("Plot:", normality_test.plot)
        # self.parent.add_output(r_script, normality_test.result, normality_test.plot)
        display_script_and_output(self.parent, r_script, normality_test.result, normality_test.plot)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)
        self.icon_label.setVisible(False)
        self.run_button.setText("Run")
        self.run_button.setEnabled(True)
        self.close()

    def closeEvent(self, event):
        self.selected_model.setStringList([]) 
        self.script_box.setPlainText("") 
        event.accept()