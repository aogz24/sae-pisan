from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListView, QPushButton, QHBoxLayout, QAbstractItemView, QTextEdit
from PyQt6.QtCore import QStringListModel
from service.modelling.SaeHB import *

class ModelingSaeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SAE HB Modelling")

        self.columns = []

        layout = QVBoxLayout()

        # Variables List
        self.variables_label = QLabel("Select Variables:")
        self.variables_list = QListView()
        self.variables_model = QStringListModel(self.columns)
        self.variables_list.setModel(self.variables_model)
        self.variables_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Buttons for assigning variables
        self.assign_dependent_button = QPushButton("Assign as Dependent Variable")
        self.assign_independent_button = QPushButton("Assign as Independent Variables")
        self.assign_vardir_button = QPushButton("Assign as Vardir")

        self.assign_dependent_button.clicked.connect(lambda : assign_dependent(self))
        self.assign_independent_button.clicked.connect(lambda : assign_independent(self))
        self.assign_vardir_button.clicked.connect(lambda: assign_vardir(self))

        # Single button for unassigning variables
        self.unassign_button = QPushButton("Unassign Variable")
        self.unassign_button.clicked.connect(lambda : unassign_variable(self))

        # Lists for assigned variables
        self.dependent_label = QLabel("Dependent Variable:")
        self.dependent_list = QListView()
        self.dependent_model = QStringListModel()
        self.dependent_list.setModel(self.dependent_model)
        self.dependent_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.independent_label = QLabel("Independent Variable(s):")
        self.independent_list = QListView()
        self.independent_model = QStringListModel()
        self.independent_list.setModel(self.independent_model)

        self.vardir_label = QLabel("Varian Diect:")
        self.vardir_list = QListView()
        self.vardir_model = QStringListModel()
        self.vardir_list.setModel(self.vardir_model)
        
        self.variables_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.dependent_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.independent_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.vardir_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Text area for displaying and editing R script
        self.r_script_edit = QTextEdit()
        self.r_script_edit.setReadOnly(False)

        # Button for generating R script
        self.generate_r_script_button = QPushButton("Update R Script")
        self.generate_r_script_button.clicked.connect(lambda : show_r_script(self))

        # Buttons for dialog actions
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # Add widgets to layout
        layout.addWidget(self.variables_label)
        layout.addWidget(self.variables_list)
        layout.addWidget(self.assign_dependent_button)
        layout.addWidget(self.assign_independent_button)
        layout.addWidget(self.assign_vardir_button)
        layout.addWidget(self.unassign_button)
        layout.addWidget(self.dependent_label)
        layout.addWidget(self.dependent_list)
        layout.addWidget(self.independent_label)
        layout.addWidget(self.independent_list)
        layout.addWidget(self.vardir_label)
        layout.addWidget(self.vardir_list)
        layout.addWidget(self.generate_r_script_button)
        layout.addWidget(self.r_script_edit)
        layout.addLayout(button_layout)

        self.setLayout(layout)

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
