from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListView, QPushButton, QHBoxLayout, QAbstractItemView
from PyQt6.QtCore import QStringListModel

class ModelingSaeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SAE HB Modelling")

        self.columns = []

        layout = QVBoxLayout()

        # Variables List
        self.variables_label = QLabel("Pilih Variabel:")
        self.variables_list = QListView()
        self.variables_model = QStringListModel(self.columns)
        self.variables_list.setModel(self.variables_model)
        self.variables_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Buttons for assigning variables
        self.assign_dependent_button = QPushButton("Assign as Dependent Variable")
        self.assign_independent_button = QPushButton("Assign as Independent Variables")
        self.assign_vardir_button = QPushButton("Assign as Vardir")

        self.assign_dependent_button.clicked.connect(self.assign_dependent)
        self.assign_independent_button.clicked.connect(self.assign_independent)
        self.assign_vardir_button.clicked.connect(self.assign_vardir)

        # Single button for unassigning variables
        self.unassign_button = QPushButton("Unassign Variable")
        self.unassign_button.clicked.connect(self.unassign_variable)

        # Lists for assigned variables
        self.dependent_label = QLabel("Dependent Variable:")
        self.dependent_list = QListView()
        self.dependent_model = QStringListModel()
        self.dependent_list.setModel(self.dependent_model)
        self.dependent_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.independent_label = QLabel("Independent Variables:")
        self.independent_list = QListView()
        self.independent_model = QStringListModel()
        self.independent_list.setModel(self.independent_model)

        self.vardir_label = QLabel("Vardir Variable:")
        self.vardir_list = QListView()
        self.vardir_model = QStringListModel()
        self.vardir_list.setModel(self.vardir_model)

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
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.dependent_var = []
        self.independent_vars = []
        self.vardir_var = []

    def assign_dependent(self):
        selected_indexes = self.variables_list.selectedIndexes()
        self.dependent_var = [index.data() for index in selected_indexes]
        self.dependent_model.setStringList(self.dependent_var)

    def assign_independent(self):
        selected_indexes = self.variables_list.selectedIndexes()
        if selected_indexes:
            self.independent_vars = [selected_indexes[-1].data()]
            self.independent_model.setStringList(self.independent_vars)

    def assign_vardir(self):
        selected_indexes = self.variables_list.selectedIndexes()
        if selected_indexes:
            self.vardir_var = [selected_indexes[-1].data()]
            self.vardir_model.setStringList(self.vardir_var)

    def unassign_variable(self):
        selected_indexes = self.dependent_list.selectedIndexes()
        if selected_indexes:
            selected_items = [index.data() for index in selected_indexes]
            self.dependent_var = [var for var in self.dependent_var if var not in selected_items]
            self.dependent_model.setStringList(self.dependent_var)
            return

        selected_indexes = self.independent_list.selectedIndexes()
        if selected_indexes:
            selected_items = [index.data() for index in selected_indexes]
            self.independent_vars = [var for var in self.independent_vars if var not in selected_items]
            self.independent_model.setStringList(self.independent_vars)
            return

        selected_indexes = self.vardir_list.selectedIndexes()
        if selected_indexes:
            selected_items = [index.data() for index in selected_indexes]
            self.vardir_var = [var for var in self.vardir_var if var not in selected_items]
            self.vardir_model.setStringList(self.vardir_var)

    def get_selected_variables(self):
        return self.dependent_var, self.independent_vars, self.vardir_var
    
    def set_model(self, model):
        self.model = model
        self.columns = [f"{col} [numerik]" if dtype in ['int64', 'float64'] else f"{col} [{dtype}]" for col, dtype in zip(self.model.get_data().columns, self.model.get_data().dtypes)]
        self.variables_model.setStringList(self.columns)
