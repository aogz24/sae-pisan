from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QTextEdit, QGroupBox, QComboBox, QSpacerItem, QSizePolicy, QMessageBox, QSpinBox
)

from PyQt6.QtCore import Qt, QStringListModel, QSize
from PyQt6.QtGui import QIcon
import polars as pl
from model.Histogram import Histogram
from controller.Graph.GraphController import HistogramController

class HistogramDialog(QDialog):
    """
    A dialog for creating histograms using selected variables from data models.
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
        add_button (QPushButton): Button to add selected variables.
        remove_button (QPushButton): Button to remove selected variables.
        selected_label (QLabel): Label for the selected variables section.
        selected_model (QStringListModel): Model for the selected variables list view.
        selected_list (QListView): List view for the selected variables.
        method_combo (QComboBox): Combo box to select the histogram method.
        graph_option_combo (QComboBox): Combo box to select between Bins or Binwidth.
        graph_option_spinbox (QSpinBox): Spin box to set the value for Bins or Binwidth.
        script_layout (QHBoxLayout): Layout for the R script section.
        script_label (QLabel): Label for the R script section.
        icon_label (QLabel): Label to display the running icon.
        script_box (QTextEdit): Text edit to display the generated R script.
        run_button (QPushButton): Button to run the generated R script.
    Methods:
        set_model(model1, model2): Sets the data models and updates the list views.
        get_column_with_dtype(model): Returns a list of columns with their data types.
        add_variable(): Adds selected variables to the selected list and updates the R script.
        remove_variable(): Removes selected variables from the selected list and updates the R script.
        get_selected_columns(): Returns a list of selected columns formatted for R script.
        generate_r_script(): Generates the R script based on selected variables and options.
        accept(): Runs the generated R script and handles the result.
        closeEvent(event): Resets the dialog when it is closed.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Histogram")

        # Menyimpan status variabel yang dipilih
        self.selected_status = {}

        # Layout utama
        main_layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        # Layout kiri untuk Data Editor dan Data Output
        left_layout = QVBoxLayout()

        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_model = QStringListModel()
        self.data_editor_list = QListView(self)
        self.data_editor_list.setModel(self.data_editor_model)
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_editor_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        self.data_output_label = QLabel("Data Output", self)
        self.data_output_model = QStringListModel()
        self.data_output_list = QListView(self)
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
        self.selected_label = QLabel("Variabel", self)
        self.selected_model = QStringListModel()
        self.selected_list = QListView(self)
        self.selected_list.setModel(self.selected_model)
        self.selected_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        # Grup metode
        method_group = QGroupBox("Metode")
        method_layout = QVBoxLayout()
        self.method_combo = QComboBox(self)
        self.method_combo.addItems(["Single Histogram", "Multiple Histogram"])
        self.method_combo.currentIndexChanged.connect(self.generate_r_script)
        method_layout.addWidget(self.method_combo)
        method_group.setLayout(method_layout)
        right_layout.addWidget(method_group)

        # Grup Graph Options
        graph_option_group = QGroupBox("Graph Options")
        graph_option_layout = QVBoxLayout()

        # Dropdown untuk memilih antara Bins atau Binwidth
        self.graph_option_combo = QComboBox(self)
        self.graph_option_combo.addItems(["Bins", "Binwidth"])
        self.graph_option_combo.currentIndexChanged.connect(self.generate_r_script)
        graph_option_layout.addWidget(self.graph_option_combo)

        # Spinbox untuk nilai Bins atau Binwidth
        self.graph_option_spinbox = QSpinBox(self)
        self.graph_option_spinbox.setMinimum(1)
        self.graph_option_spinbox.setMaximum(100)
        self.graph_option_spinbox.setValue(10)
        graph_option_layout.addWidget(self.graph_option_spinbox)

        graph_option_group.setLayout(graph_option_layout)
        right_layout.addWidget(graph_option_group)

        content_layout.addLayout(right_layout)
        main_layout.addLayout(content_layout)

        self.script_layout = QHBoxLayout()  # Tambahkan self. di sini
        self.script_label = QLabel("R Script:", self)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon("assets/running.svg").pixmap(QSize(16, 30)))
        self.icon_label.setFixedSize(16, 30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        spacer = QSpacerItem(40, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.script_layout.addWidget(self.script_label)
        self.script_layout.addItem(spacer)  
        self.script_layout.addWidget(self.icon_label)
        self.icon_label.setVisible(False)
        self.script_box = QTextEdit(self)

        # Tambahkan ke layout utama
        main_layout.addLayout(self.script_layout)  # Sekarang script_layout adalah atribut kelas
        main_layout.addWidget(self.script_box)

        # Tombol Run
        button_row_layout = QHBoxLayout()
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.accept)
        button_row_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(button_row_layout)

        self.data_editor_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.selected_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

    def set_model(self, model1, model2):
        self.model1 = model1
        self.model2 = model2
        self.data_editor_model.setStringList(self.get_column_with_dtype(model1))
        self.data_output_model.setStringList(self.get_column_with_dtype(model2))
        self.all_columns_model1 = self.get_column_with_dtype(model1)
        self.all_columns_model2 = self.get_column_with_dtype(model2)

    def get_column_with_dtype(self, model):
        self.columns = [
            f"{col} [{dtype}]" if dtype == pl.Utf8 else f"{col} [Numeric]"
            for col, dtype in zip(model.get_data().columns, model.get_data().dtypes)
        ]
        return self.columns  


    def add_variable(self):
        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]
        selected_list = self.selected_model.stringList()
        
        contains_string = any("[String]" in item for item in selected_items)   
        selected_items = [item for item in selected_items if "[String]" not in item] 

        if contains_string:
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

    def get_selected_columns(self):
        return [f"`{item.rsplit(' [String]', 1)[0].rsplit(' [Numeric]', 1)[0]}`" 
                for item in self.selected_model.stringList()]

   
    def generate_r_script(self):
        # Get selected columns
        selected_columns = self.get_selected_columns()
        if not selected_columns:
            self.script_box.setPlainText("Tidak ada kolom yang dipilih.")
            return

        # Get selected method
        method = self.method_combo.currentText()
        graph_option = self.graph_option_combo.currentText()  # Bins atau Binwidth
        bin_value = self.graph_option_spinbox.value()  # Nilai dari spinbox

        # Pastikan bin_value valid
        if bin_value <= 0:
            self.script_box.setPlainText("Nilai bin harus lebih besar dari 0.")
            return

        r_script = ""

        if method == "Single Histogram":
            for col in selected_columns:
                col_safe = col.strip("`")  # Bersihkan backticks agar tidak dobel
                r_script += (
                    f"histogram_{col_safe.replace(' ', '_')} <- ggplot(data, aes(x = `{col_safe}`)) +\n"  
                    f"    geom_histogram("
                    f"{'bins = ' + str(bin_value) if graph_option == 'Bins' else 'binwidth = ' + str(bin_value)}, "
                    f"fill = sample(colors(), 1), color = 'black') +\n"
                    f"    ggtitle('Histogram: {col_safe}') +\n"  # Tidak pakai backticks
                    f"    xlab('{col_safe}') +\n"  # Tidak pakai backticks
                    f"    ylab('Frequency') +\n"
                    f"    theme_minimal()\n\n"
                )

        elif method == "Multiple Histogram":
            formatted_columns = ', '.join(f'`{col.strip("`")}`' for col in selected_columns)  # Hapus backticks dobel
            r_script += (
                f"data_long <- pivot_longer(data, cols = c({formatted_columns}), \n"
                f"    names_to = 'variable', values_to = 'value')\n\n"
                f"histogram_multiple <- ggplot(data_long, aes(x = value, fill = variable)) +\n"
                f"    geom_histogram("
                f"{'bins = ' + str(bin_value) if graph_option == 'Bins' else 'binwidth = ' + str(bin_value)}, "
                f"alpha = 0.6, position = 'identity', color = 'black') +\n"
                f"    ggtitle('Multiple Histogram') +\n"
                f"    xlab('Value') +\n"
                f"    ylab('Frequency') +\n"
                f"    theme_minimal()\n"
            )

        # Tampilkan script di text box
        self.script_box.setPlainText(r_script)



    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            QMessageBox.warning(self, "Empty Script", "Please generate a script before running.")
            return
        if len(self.selected_model.stringList()) == 0:
            QMessageBox.warning(self, "No Variables Selected", "Please select at least one variable.")
            return
        self.run_button.setEnabled(False)
        self.run_button.setText("Running...")
        self.icon_label.setVisible(True)
        histogram = Histogram(self.model1, self.model2, self.parent)
        controller = HistogramController(histogram)
        controller.run_model(r_script)
        if histogram.error:
            QMessageBox.critical(self, "Histogram", histogram.result)
        else:
            QMessageBox.information(self, "Histogram", "Graph has been generated.")

        self.parent.add_output(script_text=r_script, result_text=histogram.result, plot_paths=histogram.plot)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)
        self.icon_label.setVisible(False)
        self.run_button.setText("Run")
        self.run_button.setEnabled(True)
        self.close()

    def closeEvent(self, event):
        self.selected_model.setStringList([])
        self.script_box.setPlainText("")
        event.accept()
