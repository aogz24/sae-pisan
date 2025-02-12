from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListView, QPushButton, QLabel, QComboBox, QCheckBox, QTextEdit, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QStringListModel
from model.Scatterplot import Scatterplot
from controller.Eksploration.EksplorationController import ScatterPlotController


class ScatterPlotDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None
        self.all_columns_model1 = []
        self.all_columns_model2 = []

        self.setWindowTitle("Scatter Plot")

        # Menyimpan status variabel yang dipilih
        self.selected_status = {}

        # Layout utama
        main_layout = QVBoxLayout(self)

        # Layout konten utama
        content_layout = QHBoxLayout()

        # Layout kiri: Data Editor dan Data Output
        left_layout = QVBoxLayout()

        # Data Editor
        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_model = QStringListModel()
        self.data_editor_list = QListView(self)
        self.data_editor_list.setModel(self.data_editor_model)
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_editor_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        # Data Output
        self.data_output_label = QLabel("Data Output", self)
        self.data_output_model = QStringListModel()
        self.data_output_list = QListView(self)
        self.data_output_list.setModel(self.data_output_model)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        self.data_output_list.setEditTriggers(QListView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.data_output_label)
        left_layout.addWidget(self.data_output_list)

        content_layout.addLayout(left_layout)

        # Layout tengah: Tombol
        button_layout1 = QVBoxLayout()
        self.remove_button1 = QPushButton("\u2190", self)  # Tombol untuk menghapus variabel
        self.remove_button1.clicked.connect(self.remove_variable)  # Harusnya menghapus variabel
        button_layout1.addStretch(3)
        button_layout1.addWidget(self.remove_button1)
        button_layout1.addStretch(7)

        button_layout2 = QVBoxLayout()
        self.add_horizontal_button = QPushButton("\u2192", self)  # Tombol untuk menambahkan ke Horizontal Axis
        self.add_horizontal_button.clicked.connect(self.add_variable_horizontal)
        self.add_vertical_button = QPushButton("\u2192", self)  # Tombol untuk menambahkan ke Vertical Axis
        self.add_vertical_button.clicked.connect(self.add_variable_vertical)
        button_layout2.addStretch(1)
        button_layout2.addWidget(self.add_horizontal_button)
        button_layout2.addStretch(3)
        button_layout2.addWidget(self.add_vertical_button)
        button_layout2.addStretch(5)

        # Menambahkan kedua layout tombol ke content_layout
        content_layout.addLayout(button_layout1)
        content_layout.addLayout(button_layout2)

        # Layout kanan: Variabel yang dipilih, metode, dan grafik
        right_layout = QVBoxLayout()

        # Horizontal Axis
        horizontal_layout = QVBoxLayout()
        self.horizontal_label = QLabel("Horizontal Axis", self)
        self.horizontal_model = QStringListModel()
        self.horizontal_list = QListView(self)
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
        self.vertical_list = QListView(self)
        self.vertical_list.setModel(self.vertical_model)
        self.vertical_list.setSelectionMode(QListView.SelectionMode.MultiSelection)
        vertical_layout.addWidget(self.vertical_label)
        vertical_layout.addWidget(self.vertical_list)
        right_layout.addLayout(vertical_layout)


        # Grup metode
        method_group = QGroupBox("Metode")
        method_layout = QVBoxLayout()
        self.method_combo = QComboBox(self)
        self.method_combo.addItems(["Single Scatter Plot", "Multiple Scatter Plot"])
        self.method_combo.currentIndexChanged.connect(self.generate_r_script)
        method_layout.addWidget(self.method_combo)
        method_group.setLayout(method_layout)
        right_layout.addWidget(method_group)

        # Grup grafik
        graph_group = QGroupBox("Graph Options")  # Change the name of the graph group
        graph_layout = QVBoxLayout()
        self.regression_line_checkbox = QCheckBox("Show Regression Line", self)  # New checkbox for regression line
        self.regression_line_checkbox.stateChanged.connect(self.generate_r_script)
        graph_layout.addWidget(self.regression_line_checkbox)  # Add the regression line checkbox to the layout
        graph_group.setLayout(graph_layout)
        right_layout.addWidget(graph_group)

        content_layout.addLayout(right_layout)

        main_layout.addLayout(content_layout)

        # Script box
        self.script_label = QLabel("Script:", self)
        self.script_box = QTextEdit(self)
        main_layout.addWidget(self.script_label)
        main_layout.addWidget(self.script_box)

        # Tombol Run
        button_row_layout = QHBoxLayout()
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.accept)
        button_row_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(button_row_layout)
        
        self.data_editor_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.data_output_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.vertical_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.horizontal_list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)

    def set_model(self, model1, model2):
        self.model1 = model1
        self.model2 = model2
        self.data_editor_model.setStringList(self.get_column_with_dtype(model1))
        self.data_output_model.setStringList(self.get_column_with_dtype(model2))
        self.all_columns_model1 = self.get_column_with_dtype(model1)
        self.all_columns_model2 = self.get_column_with_dtype(model2)


    def get_column_with_dtype(self, model):
        """Mengembalikan daftar nama kolom dengan tipe datanya"""
        return [
            f"{col} [numerik]" if dtype in ['int64', 'float64'] else f"{col} [{dtype}]"
            for col, dtype in zip(model.get_data().columns, model.get_data().dtypes)
        ]
    

    def add_variable_horizontal(self):
        # Check if there is already a variable in the horizontal axis
        if len(self.horizontal_model.stringList()) >= 1:
            QMessageBox.warning(self, "Warning", "You can only add one variable to the Horizontal Axis!")
            return  # Do not add if one variable is already present

        # Get all selected indexes from data editor and data output
        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]

        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a variable first!")
            return  # Show a warning and exit if no variable is selected

        selected_list = self.horizontal_model.stringList()

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
                selected_list = [item]  # Ensure only one variable is in the horizontal axis
                break  # Exit loop after adding one item

        self.horizontal_model.setStringList(selected_list)
        self.generate_r_script()

    
    def add_variable_vertical(self):
        # Ambil semua indeks yang dipilih dari data editor dan data output
        selected_indexes = self.data_editor_list.selectedIndexes() + self.data_output_list.selectedIndexes()
        selected_items = [index.data() for index in selected_indexes]
        selected_list = self.vertical_model.stringList()

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
        # Ambil indeks yang dipilih dari daftar variabel horizontal dan vertical
        selected_horizontal_indexes = self.horizontal_list.selectedIndexes()
        selected_vertical_indexes = self.vertical_list.selectedIndexes()

        # Ambil nama variabel yang dipilih
        selected_horizontal_items = [index.data() for index in selected_horizontal_indexes]
        selected_vertical_items = [index.data() for index in selected_vertical_indexes]

        # Gabungkan kedua daftar variabel yang dipilih
        selected_items = selected_horizontal_items + selected_vertical_items

        # Ambil daftar semua variabel yang sedang dipilih
        horizontal_list = self.horizontal_model.stringList()
        vertical_list = self.vertical_model.stringList()

        # Periksa apakah variabel dikembalikan ke data editor atau data output
        for item in selected_items:
            column_name = item.split(' ')[0]  # Ambil nama kolom sebelum spasi

            if column_name in [col.split(' ')[0] for col in self.all_columns_model1]:
                editor_list = self.data_editor_model.stringList()
                if item not in editor_list:
                    editor_list.append(item)
                    self.data_editor_model.setStringList(editor_list)

            elif column_name in [col.split(' ')[0] for col in self.all_columns_model2]:
                output_list = self.data_output_model.stringList()
                if item not in output_list:
                    output_list.append(item)
                    self.data_output_model.setStringList(output_list)

            # Hapus item dari daftar horizontal atau vertical jika ada
            if item in horizontal_list:
                horizontal_list.remove(item)

            if item in vertical_list:
                vertical_list.remove(item)

        # Perbarui daftar variabel yang dipilih
        self.horizontal_model.setStringList(horizontal_list)
        self.vertical_model.setStringList(vertical_list)

        # Perbarui script R setelah perubahan
        self.generate_r_script()

    
    def get_selected_horizontal(self):
        return [
            item.split(" [")[0].replace(" ", "_")
            for item in self.horizontal_model.stringList()
        ]
    
    def get_selected_vertical(self):
        return [
            item.split(" [")[0].replace(" ", "_")
            for item in self.vertical_model.stringList()
        ]
    
    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            return
        
        scatter_plot = Scatterplot(self.model1, self.model2, self.parent)
        controller = ScatterPlotController(scatter_plot)
        controller.run_model(r_script)

        self.parent.add_output(script_text = r_script, plot_paths = scatter_plot.plot)
        self.parent.tab_widget.setCurrentWidget(self.parent.output_tab)

        self.run_button.setEnabled(True)
        self.run_button.setText("Run")
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
        show_regression = self.regression_line_checkbox.isChecked()

        r_script = ""

        # Pastikan hanya mengambil elemen pertama untuk horizontal
        selected_var_horizontal = selected_var_horizontal[0] if selected_var_horizontal else None

        # Single Scatterplot: Create multiple scatterplots, each with a random color
        if method == "Single Scatter Plot":
            for var in selected_var_vertical:
                # Generate script for each vertical variable
                r_script += f"""
# Scatterplot for {selected_var_horizontal} vs. {var}
    scatterplot_{var} <- ggplot(data, aes(x = {selected_var_horizontal}, y = {var})) +
    geom_point(color = sample(colors(), 1)) +  
    ggtitle("Scatterplot: {selected_var_horizontal} vs. {var}") +
    xlab("{selected_var_horizontal}") +
    ylab("{var}") +
    """
                # Add regression line if checkbox is checked
                if show_regression:
                    r_script += 'geom_smooth(method = "lm", se = FALSE, color = "red") + \n'
                r_script += "theme_minimal()"

        # Multiple Scatterplot: Gabungkan kolom-kolom vertikal ke dalam satu variabel y
        elif method == "Multiple Scatter Plot":
            # Buat daftar variabel vertikal dalam format string untuk R
            vertical_vars = ", ".join(f'"{var}"' for var in selected_var_vertical)

            r_script += f"""
# Multiple scatterplot for {selected_var_horizontal} vs. multiple y variables
# Konversi ke format long agar bisa digunakan dalam ggplot
data_long <- pivot_longer(data, cols = c({vertical_vars}), 
                        names_to = "variable", values_to = "value")
# Buat scatterplot
scatterplot_multiple <- ggplot(data_long, aes(x = {selected_var_horizontal}, y = value, color = variable)) +
    geom_point() +
    ggtitle("Multiple Scatterplot: {selected_var_horizontal} vs. {', '.join(selected_var_vertical)}") +
    xlab("{selected_var_horizontal}") +
    ylab("Value") +"""
            # Tambahkan regresi jika diperlukan
            if show_regression:
                r_script += 'geom_smooth(method = "lm", se = FALSE) +\n'

            r_script += "theme_minimal()"

        # Show script in text box
        self.script_box.setPlainText(r_script)


