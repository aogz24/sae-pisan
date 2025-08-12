from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QTextEdit, QGroupBox, QComboBox, QSpacerItem, QSizePolicy, QMessageBox, QToolButton
)
from PyQt6.QtCore import Qt, QStringListModel, QSize
from PyQt6.QtGui import QIcon
import polars as pl
import re
from model.BoxPlot import BoxPlot
from controller.Graph.GraphController import BoxPlotController
from service.utils.utils import display_script_and_output
from view.components.DragDropListView import DragDropListView

class BoxPlotDialog(QDialog):
    """
    A dialog for creating and displaying box plots using selected variables from two data models.
    Attributes:
        parent (QWidget): The parent widget.
        model1 (Any): The first data model.
        model2 (Any): The second data model.
        all_columns_model1 (list): List of all columns from the first data model.
        all_columns_model2 (list): List of all columns from the second data model.
        selected_status (dict): Dictionary to store the status of selected variables.
        data_editor_label (QLabel): Label for the data editor list.
        data_editor_model (QStringListModel): Model for the data editor list.
        data_editor_list (QListView): List view for the data editor.
        data_output_label (QLabel): Label for the data output list.
        data_output_model (QStringListModel): Model for the data output list.
        data_output_list (QListView): List view for the data output.
        add_button (QPushButton): Button to add selected variables.
        remove_button (QPushButton): Button to remove selected variables.
        selected_label (QLabel): Label for the selected variables list.
        selected_model (QStringListModel): Model for the selected variables list.
        selected_list (QListView): List view for the selected variables.
        method_combo (QComboBox): Combo box to select the box plot method.
        script_layout (QHBoxLayout): Layout for the R script display.
        script_label (QLabel): Label for the R script.
        icon_label (QLabel): Label to display the running icon.
        script_box (QTextEdit): Text box to display the generated R script.
        run_button (QPushButton): Button to run the generated R script.
    Methods:
        set_model(model1, model2): Sets the data models and updates the data editor and output lists.
        get_column_with_dtype(model): Returns a list of columns with their data types from the given model.
        add_variable(): Adds selected variables from the data editor and output lists to the selected variables list.
        remove_variable(): Removes selected variables from the selected variables list and adds them back to the data editor or output lists.
        get_selected_columns(): Returns a list of selected columns formatted for R script.
        generate_r_script(): Generates the R script based on the selected variables and method.
        accept(): Runs the generated R script and displays the result.
        closeEvent(event): Resets the dialog when it is closed.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Box Plot")

        # Menyimpan status variabel yang dipilih
        self.selected_status = {}

        # Layout utama
        self.main_layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        # Layout kiri untuk Data Editor dan Data Output
        left_layout = QVBoxLayout()

        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_model = QStringListModel()
        self.data_editor_list = DragDropListView(parent=self)
        self.data_editor_list.setModel(self.data_editor_model)
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_editor_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        self.data_output_label = QLabel("Data Output", self)
        self.data_output_model = QStringListModel()
        self.data_output_list = DragDropListView(parent=self)
        self.data_output_list.setModel(self.data_output_model)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_output_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_output_label)
        left_layout.addWidget(self.data_output_list)

        content_layout.addLayout(left_layout)

        # Layout tengah untuk tombol
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

        # Layout kanan
        right_layout = QVBoxLayout()
        self.selected_label = QLabel("Variable", self)
        self.selected_model = QStringListModel()
        self.selected_list = DragDropListView(parent=self)
        self.selected_list.setModel(self.selected_model)
        self.selected_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        # Grup metode
        method_group = QGroupBox("Metode")
        method_layout = QVBoxLayout()
        self.method_combo = QComboBox(self)
        self.method_combo.addItems(["Single Box plot", "Multiple Box Plot"])
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
        self.selected_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

    def handle_drop(self, target_widget, items):
        # Map widget to model
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
            # Reject if String or None type
            if "[String]" in item or "[NULL]" in item:
                continue

            if target_widget == self.selected_list:
                filtered_items.append(item)
            else:
                column_name = item.split(" ")[0]
                if allowed_columns and column_name in [col.split(" ")[0] for col in allowed_columns]:
                    filtered_items.append(item)

        # ❗️Show warning if there are String or None types
        if contains_string:
            QMessageBox.warning(self, "Warning", "Selected variables must be of type Numeric.")

        # Add valid items to the target model
        for item in filtered_items:
            if item not in current_items:
                current_items.append(item)

        # Remove from other models
        for other_widget, (model, _) in widget_model_map.items():
            if model == target_model:
                continue
            other_items = model.stringList()
            for item in filtered_items:
                if item in other_items:
                    other_items.remove(item)
            model.setStringList(other_items)

        # Reorder items
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
        return [f"`{item.rsplit(' [String]', 1)[0].rsplit(' [Numeric]', 1)[0]}`" 
                for item in self.selected_model.stringList()]

    def generate_r_script(self):
        # Get selected columns
        selected_columns = self.get_selected_columns()
        if not selected_columns:
            self.script_box.setPlainText("")
            return

        # Get selected method
        method = self.method_combo.currentText()
        formatted_columns = ', '.join(selected_columns)  # Tetap gunakan backticks di sini
        r_script = ""

        # Single Box Plot: Jika ada banyak variabel, buat plot terpisah
        if method == "Single Box plot":
            for col in selected_columns:
                clean_name = re.sub(r"\W+", "_", col.strip("`"))  # Bersihkan nama untuk penamaan objek
                r_script += (
                    f"# Box plot for {col}\n"
                    f"boxplot_{clean_name} <- ggplot(data, aes(y = {col})) +\n"
                    f"    geom_boxplot(fill = 'darkorange3') +\n"
                    f"    ggtitle('Box Plot: {col.strip('`')}') +\n"
                    f"    ylab('{col.strip('`')}') +\n"
                    f"    theme_minimal()\n\n"
                )

        # Multiple Box Plot: Gabungkan semua variabel dalam satu plot
        elif method == "Multiple Box Plot":
            r_script += (
                f"# Convert to long format for ggplot compatibility\n"
                f"data_long <- pivot_longer(data, cols = c({formatted_columns}), \n"
                f"    names_to = 'variable', values_to = 'value')\n\n"
                f"# Create multiple box plot\n"
                f"boxplot_multiple <- ggplot(data_long, aes(x = variable, y = value, fill = variable)) +\n"
                f"    geom_boxplot() +\n"
                f"    ggtitle('Multiple Box Plot') +\n"
                f"    xlab('Variable') +\n"
                f"    ylab('Value') +\n"
                f"    theme_minimal()\n"
            )

        # Show script in text box
        self.script_box.setPlainText(r_script)

    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            if len(self.selected_model.stringList()) == 0:
                QMessageBox.warning(self, "No Variables Selected", "Please select at least one variable.")
                return
            else:
                QMessageBox.warning(self, "Empty Script", "Please generate a script before running.")
                return
        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")
        self.icon_label.setVisible(True)
        box_plot = BoxPlot(self.model1, self.model2, self.parent)
        controller = BoxPlotController(box_plot)
        controller.run_model(r_script)
        if box_plot.error:
            QMessageBox.critical(self, "Box Plot", box_plot.result)
        else:
            QMessageBox.information(self, "Box Plot", "Graph has been generated")

        display_script_and_output(self.parent, r_script, box_plot.result, box_plot.plot)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)

        self.icon_label.setVisible(False)
        self.run_button.setText("Run")
        self.run_button.setEnabled(True)
        self.close()

    def closeEvent(self, event):
        self.selected_model.setStringList([])
        self.script_box.setPlainText("")
        event.accept()
