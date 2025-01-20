from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, QComboBox, QCheckBox, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from model.NormalityTest import NormalityTest
from controller.Eksploration.NormalityTestController import NormalityTestController

class NormalityTestDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.model1 = None
        self.model2 = None

        self.setWindowTitle("Normality Test")

        self.selected_status = {}

        # Layout utama
        main_layout = QVBoxLayout(self)

        # Layout konten utama
        content_layout = QHBoxLayout()

        # Layout kiri untuk Data Editor dan Data Output
        left_layout = QVBoxLayout()
        self.data_editor_label = QLabel("Data Editor", self)
        self.data_editor_list = QListWidget(self)
        self.data_editor_list.itemClicked.connect(self.toggle_selection)
        left_layout.addWidget(self.data_editor_label)
        left_layout.addWidget(self.data_editor_list)

        self.data_output_label = QLabel("Data Output", self)
        self.data_output_list = QListWidget(self)
        self.data_output_list.itemClicked.connect(self.toggle_selection)
        left_layout.addWidget(self.data_output_label)
        left_layout.addWidget(self.data_output_list)

        content_layout.addLayout(left_layout)

        # Layout tengah untuk tombol
        button_layout = QVBoxLayout()
        self.add_button = QPushButton("\u2192", self)
        self.add_button.clicked.connect(self.add_variable)
        self.remove_button = QPushButton("\u2190", self)
        self.remove_button.clicked.connect(self.remove_variable)
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()

        content_layout.addLayout(button_layout)

        # Layout kanan untuk variabel yang dipilih
        right_layout = QVBoxLayout()
        self.selected_label = QLabel("Variabel", self)
        self.selected_list = QListWidget(self)
        right_layout.addWidget(self.selected_label)
        right_layout.addWidget(self.selected_list)

        # Grup Metode Uji Normalitas
        method_group = QGroupBox("Metode")
        method_layout = QVBoxLayout()
        self.method_combo = QComboBox(self)
        self.method_combo.addItems(["Shapiro-Wilk", "Jarque-Bera", "Lilliefors"])
        self.method_combo.currentIndexChanged.connect(self.generate_r_script)
        method_layout.addWidget(self.method_combo)
        method_group.setLayout(method_layout)
        right_layout.addWidget(method_group)

        # Grup Grafik
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

        main_layout.addLayout(content_layout)

        # Box untuk script
        self.script_label = QLabel("Script:", self)
        self.script_box = QTextEdit(self)
        self.script_box.setReadOnly(True)
        main_layout.addWidget(self.script_label)
        main_layout.addWidget(self.script_box)

        # Layout untuk tombol Run
        button_row_layout = QHBoxLayout()
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.accept)
        button_row_layout.addWidget(self.run_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(button_row_layout)

    def set_model(self, model1, model2):
        self.model1 = model1
        self.model2 = model2

        # Ambil kolom dari model1 dan model2
        self.all_columns_model1 = self.get_column_with_dtype(self.model1)
        self.all_columns_model2 = self.get_column_with_dtype(self.model2)

        self.data_editor_list.clear()
        self.data_output_list.clear()
        self.data_editor_list.addItems(self.all_columns_model1)
        self.data_output_list.addItems(self.all_columns_model2)

    def get_column_with_dtype(self, model):
        return [
            f"{col} [numerik]" if dtype in ['int64', 'float64'] else f"{col} [{dtype}]"
            for col, dtype in zip(model.get_data().columns, model.get_data().dtypes)
        ]

    def toggle_selection(self, item):
        text = item.text()
        self.selected_status[text] = not self.selected_status.get(text, False)
        item.setSelected(self.selected_status[text])

    def add_variable(self):
        selected_items = self.data_editor_list.selectedItems() + self.data_output_list.selectedItems()
        for item in selected_items:
            if self.selected_status.get(item.text(), False):
                self.selected_list.addItem(item.text())
                list_widget = self.data_editor_list if item in self.data_editor_list.selectedItems() else self.data_output_list
                list_widget.takeItem(list_widget.row(item))
                self.selected_status[item.text()] = False
        self.generate_r_script()

    def remove_variable(self):
        selected_items = self.selected_list.selectedItems()
        for item in selected_items:
            column_name = item.text().split(' ')[0]
            if column_name in [col.split(' ')[0] for col in self.all_columns_model1]:
                self.data_editor_list.addItem(item.text())
            elif column_name in [col.split(' ')[0] for col in self.all_columns_model2]:
                self.data_output_list.addItem(item.text())
            self.selected_list.takeItem(self.selected_list.row(item))
        self.generate_r_script()

    def get_selected_columns(self):
        return [
            item.text().split(" [")[0].replace(" ", "_")
            for i in range(self.selected_list.count())
            for item in [self.selected_list.item(i)]
        ]

    def generate_r_script(self):
        # Ambil kolom yang dipilih untuk diuji
        selected_vars = self.get_selected_columns()
        
        # Ambil metode uji normalitas
        method = self.method_combo.currentText().lower().replace("-", "_")
        
        # Ambil opsi tambahan (histogram & Q-Q plot)
        show_histogram = self.histogram_checkbox.isChecked()
        show_qqplot = self.qqplot_checkbox.isChecked()

        if not selected_vars:
            self.script_box.setPlainText("stop('Tidak ada variabel yang dipilih untuk diuji.')")
            return

        # Awal script R
        r_script = 'normality_results <- list()\n'
        for var in selected_vars:
            # Tambahkan metode uji berdasarkan pilihan
            if method == "shapiro_wilk":
                r_script += f'normality_results[["{var}"]] <- shapiro.test(data${var})\n'
            elif method == "jarque_bera":
                r_script += f'normality_results[["{var}"]] <- tseries::jarque.bera.test(data${var})\n'
            elif method == "lilliefors":
                r_script += f'normality_results[["{var}"]] <- nortest::lillie.test(data${var})\n'
            else:
                r_script += f'stop("Metode {method} tidak dikenali.")\n'
            
            # Tambahkan visualisasi jika diperlukan
            if show_histogram:
                r_script += f'png("{var}_histogram.png")\n'
                r_script += f'hist(data${var}, main="Histogram of {var}", xlab="{var}")\n'
                r_script += 'dev.off()\n'

            if show_qqplot:
                r_script += f'png("{var}_qqplot.png")\n'
                r_script += f'qqnorm(data${var}, main="Q-Q Plot of {var}")\n'
                r_script += 'qqline(data${var}, col="red")\n'
                r_script += 'dev.off()\n'

        # Outputkan script ke text box
        self.script_box.setPlainText(r_script)


    def accept(self):
        r_script = self.script_box.toPlainText()
        if not r_script:
            return

        normality_test = NormalityTest(self.model1, self.model2, self.parent)
        controller = NormalityTestController(normality_test)
        controller.run_model(r_script)

        self.parent.add_output(r_script, normality_test.result)

        self.run_button.setEnabled(True)
        self.run_button.setText("Run")
        self.close()

