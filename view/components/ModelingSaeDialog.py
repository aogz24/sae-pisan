from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListView, QPushButton, QHBoxLayout, QAbstractItemView, QTextEdit
from PyQt6.QtCore import QStringListModel
from service.modelling.SaeHB import *

class ModelingSaeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SAE HB Modelling")

        self.columns = []

        main_layout = QVBoxLayout()

        # Layout utama untuk membagi area menjadi dua bagian (kiri dan kanan)
        split_layout = QHBoxLayout()

        # Layout kiri untuk daftar variabel
        left_layout = QVBoxLayout()
        self.variables_label = QLabel("Select Variables:")
        self.variables_list = QListView()
        self.variables_model = QStringListModel(self.columns)
        self.variables_list.setModel(self.variables_model)
        self.variables_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        left_layout.addWidget(self.variables_label)
        left_layout.addWidget(self.variables_list)
        
        middle_layout1 = QVBoxLayout()
        self.unassign_button = QPushButton("←")
        middle_layout1.addWidget(self.unassign_button)

        # Layout tengah untuk tombol panah
        middle_layout = QVBoxLayout()
        self.assign_dependent_button = QPushButton("→")
        self.assign_independent_button = QPushButton("→")
        self.assign_vardir_button = QPushButton("→")
        self.assign_dependent_button.clicked.connect(lambda: assign_dependent(self))
        self.assign_independent_button.clicked.connect(lambda: assign_independent(self))
        self.assign_vardir_button.clicked.connect(lambda: assign_vardir(self))
        self.unassign_button.clicked.connect(lambda: unassign_variable(self))
        middle_layout.addWidget(self.assign_dependent_button)
        middle_layout.addWidget(self.assign_independent_button)
        middle_layout.addWidget(self.assign_vardir_button)
        

        # Layout kanan untuk daftar dependen, independen, dan vardir
        right_layout = QVBoxLayout()
        self.dependent_label = QLabel("Dependent Variable:")
        self.dependent_list = QListView()
        self.dependent_model = QStringListModel()
        self.dependent_list.setModel(self.dependent_model)
        self.dependent_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        right_layout.addWidget(self.dependent_label)
        right_layout.addWidget(self.dependent_list)

        self.independent_label = QLabel("Independent Variable(s):")
        self.independent_list = QListView()
        self.independent_model = QStringListModel()
        self.independent_list.setModel(self.independent_model)
        self.independent_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        right_layout.addWidget(self.independent_label)
        right_layout.addWidget(self.independent_list)

        self.vardir_label = QLabel("Varian Direct:")
        self.vardir_list = QListView()
        self.vardir_model = QStringListModel()
        self.vardir_list.setModel(self.vardir_model)
        right_layout.addWidget(self.vardir_label)
        right_layout.addWidget(self.vardir_list)

        # Menambahkan layout kiri, tengah, dan kanan ke layout utama
        split_layout.addLayout(left_layout)
        split_layout.addLayout(middle_layout1)
        split_layout.addLayout(middle_layout)
        split_layout.addLayout(right_layout)

        main_layout.addLayout(split_layout)

        # Tombol untuk menghasilkan skrip R
        self.generate_r_script_button = QPushButton("Update R Script")
        self.text_script = QLabel("Script R:")
        self.generate_r_script_button.setObjectName("generate_r_script_button")
        self.generate_r_script_button.clicked.connect(lambda: show_r_script(self))
        main_layout.addWidget(self.generate_r_script_button)
        main_layout.addWidget(self.text_script)
        
        # Area teks untuk menampilkan dan mengedit skrip R
        self.r_script_edit = QTextEdit()
        self.r_script_edit.setReadOnly(False)
        main_layout.addWidget(self.r_script_edit)

        # Tombol untuk tindakan dialog
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Run Model")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.dependent_var = []
        self.independent_vars = []
        self.vardir_var = []

    def set_model(self, model):
        self.model = model
        self.columns = [f"{col} [numerik]" if dtype in ['int64', 'float64'] else f"{col} [{dtype}]" for col, dtype in zip(self.model.get_data().columns, self.model.get_data().dtypes)]
        self.variables_model.setStringList(self.columns)
    
    def accept(self):
        get_script(self)
        return super().accept()