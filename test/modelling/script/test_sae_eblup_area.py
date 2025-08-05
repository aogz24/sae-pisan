from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QAbstractItemView, QTextEdit, QComboBox, QLineEdit
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import QMessageBox

def assign_of_interest(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        for index in selected_indexes:
            if "[Numeric]" in index.data():
                parent.of_interest_var = [index.data()]
                parent.of_interest_model.setStringList(parent.of_interest_var)
                parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
                show_r_script(parent)

def assign_auxilary(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        new_vars = []
        for index in selected_indexes:
            if "[Numeric]" in index.data():
                new_vars.append(index.data())
        
        parent.auxilary_vars = list(set(parent.auxilary_vars + new_vars))  # Add new variables if they are different
        parent.auxilary_model.setStringList(parent.auxilary_vars)
        for index in sorted(selected_indexes, reverse=True):
            if "[Numeric]" in index.data():
                parent.variables_list.model().removeRow(index.row())  # Remove from variables list
        show_r_script(parent)

def assign_vardir(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        for index in selected_indexes:
            if "[Numeric]" in index.data():
                parent.vardir_var = [index.data()]
                parent.vardir_model.setStringList(parent.vardir_var)
                parent.variables_list.model().removeRow(selected_indexes[-1].row())  # Remove from variables list
                show_r_script(parent)

def assign_as_factor(parent):
    selected_indexes = parent.variables_list.selectedIndexes()
    if selected_indexes:
        new_vars = []
        for index in selected_indexes:
            new_vars.append(index.data())
        parent.as_factor_var = list(set(parent.as_factor_var + new_vars))  # Add new variables if they are different
        parent.as_factor_model.setStringList(parent.as_factor_var)
        for index in sorted(selected_indexes, reverse=True):
            parent.variables_list.model().removeRow(index.row())  # Remove from variables list
        show_r_script(parent)

def unassign_variable(parent):
    selected_indexes = parent.of_interest_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.of_interest_var = [var for var in parent.of_interest_var if var not in selected_items]
        parent.of_interest_model.setStringList(parent.of_interest_var)
        parent.variables_list.model().insertRow(0)  # Add back to variables list
        parent.variables_list.model().setData(parent.variables_list.model().index(0), selected_items[0])
        show_r_script(parent)
        return

    selected_indexes = parent.auxilary_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.auxilary_vars = [var for var in parent.auxilary_vars if var not in selected_items]
        parent.auxilary_model.setStringList(parent.auxilary_vars)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        show_r_script(parent)
        return

    selected_indexes = parent.vardir_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.vardir_var = [var for var in parent.vardir_var if var not in selected_items]
        parent.vardir_model.setStringList(parent.vardir_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        show_r_script(parent)
        return

    selected_indexes = parent.as_factor_list.selectedIndexes()
    if selected_indexes:
        selected_items = [index.data() for index in selected_indexes]
        parent.as_factor_var = [var for var in parent.as_factor_var if var not in selected_items]
        parent.as_factor_model.setStringList(parent.as_factor_var)
        for item in selected_items:
            parent.variables_list.model().insertRow(0)  # Add back to variables list
            parent.variables_list.model().setData(parent.variables_list.model().index(0), item)
        show_r_script(parent)

def get_selected_variables(parent):
    return parent.of_interest_var, parent.auxilary_vars, parent.vardir_var, parent.as_factor_var

def generate_r_script(parent):
    of_interest_var = f'{parent.of_interest_var[0].split(" [")[0].replace(" ", "_")}' if parent.of_interest_var else '""'
    auxilary_vars = " + ".join([var.split(" [")[0].replace(" ", "_") for var in parent.auxilary_vars]) if parent.auxilary_vars else '""'
    vardir_var = f'{parent.vardir_var[0].split(" [")[0].replace(" ", "_")}' if parent.vardir_var else '""'
    as_factor_var = " + ".join([f'as.factor({var.split(" [")[0].replace(" ", "_")})' for var in parent.as_factor_var]) if parent.as_factor_var else '""'
    
    if (auxilary_vars=='""' or auxilary_vars is None) and as_factor_var=='""':
        formula = f'{of_interest_var} ~ 1'
    elif as_factor_var=='""':
        formula = f'{of_interest_var} ~ {auxilary_vars}'
    elif auxilary_vars=='""':
        formula = f'{of_interest_var} ~ {as_factor_var}'
    else:
        formula = f'{of_interest_var} ~ {auxilary_vars} + {as_factor_var}'

    r_script = f'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
    r_script += f'formula <- {formula}\n'
    r_script += f'vardir_var <- data["{vardir_var}"]\n'
    if parent.selection_method=="Stepwise":
        parent.selection_method = "both"
    if parent.selection_method and parent.selection_method != "None" and auxilary_vars:
        r_script += f'stepwise_model <- step(formula, direction="{parent.selection_method.lower()}")\n'
        r_script += f'final_formula <- formula(stepwise_model)\n'
        r_script += f'model<-mseFH(final_formula, vardir_var, method = "{parent.method}", data=data)'
    else:
        r_script += f'model<-mseFH(formula, vardir_var, method = "{parent.method}", data=data)'
    return r_script

def show_r_script(parent):
    r_script = generate_r_script(parent)
    parent.r_script_edit.setText(r_script)

def get_script(parent):
    return parent.r_script_edit.toPlainText()  

def show_options(parent):
    options_dialog = QDialog(parent)
    options_dialog.setWindowTitle("Options")

    layout = QVBoxLayout()

    method_label = QLabel("Method:")
    layout.addWidget(method_label)

    parent.method_selection = QComboBox()
    parent.method_selection.addItems(["ML", "REML", "FH"])
    parent.method_selection.setCurrentText("REML")
    layout.addWidget(parent.method_selection)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)

    layout.addLayout(button_layout)

    options_dialog.setLayout(layout)

    ok_button.clicked.connect(lambda: set_selection_method(parent, options_dialog))
    cancel_button.clicked.connect(options_dialog.reject)

    options_dialog.exec()

def set_selection_method(parent, dialog):
    # parent.selection_method = parent.method_combo.currentText()
    parent.method = parent.method_selection.currentText()
    dialog.accept()
    show_r_script(parent)
    
import pytest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication, QMessageBox

# Import functions to test from the actual module
from service.modelling.SaeEblupArea import (
    assign_of_interest, 
    assign_auxilary, 
    assign_vardir, 
    assign_as_factor, 
    unassign_variable, 
    generate_r_script, 
    show_r_script,
    get_selected_variables
)

class TestSaeEblupArea:
    """Test suite for SAE EBLUP Area functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test method."""
        # Arrange - Create test fixtures
        if not QApplication.instance():
            self.app = QApplication([])  # Required for creating PyQt widgets
        
        self.parent = MagicMock()
        self.parent.variables_list.selectedIndexes.return_value = []
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        self.parent.of_interest_model = MagicMock()
        self.parent.auxilary_model = MagicMock()
        self.parent.vardir_model = MagicMock()
        self.parent.as_factor_model = MagicMock()
        self.parent.r_script_edit = MagicMock()
        self.parent.method = "REML"
        self.parent.selection_method = "None"


    def test_assign_of_interest_with_numeric_success(self):
        """Test assigning numeric variable to of_interest successfully."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_of_interest(self.parent)
        
        # Assert
        assert self.parent.of_interest_var == ["variable1 [Numeric]"], \
            f"Expected of_interest_var to be ['variable1 [Numeric]'], got {self.parent.of_interest_var}"
        self.parent.of_interest_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_assign_of_interest_with_string_should_fail(self):
        """Test assigning string variable to of_interest should be rejected."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_of_interest(self.parent)
        
        # Assert
        assert self.parent.of_interest_var == [], \
            f"Expected of_interest_var to remain empty for string variables, got {self.parent.of_interest_var}"
        self.parent.of_interest_model.setStringList.assert_not_called()
        self.parent.variables_list.model().removeRow.assert_not_called()

    def test_assign_of_interest_with_no_selection_should_do_nothing(self):
        """Test assign_of_interest with no selection should not change anything."""
        # Arrange
        self.parent.variables_list.selectedIndexes.return_value = []
        initial_of_interest = self.parent.of_interest_var.copy()
        
        # Act
        assign_of_interest(self.parent)
        
        # Assert
        assert self.parent.of_interest_var == initial_of_interest, \
            "Expected of_interest_var to remain unchanged when no selection"

    def test_assign_auxilary_with_numeric_success(self):
        """Test assigning numeric variable to auxiliary successfully."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_auxilary(self.parent)
        
        # Assert
        assert self.parent.auxilary_vars == ["variable1 [Numeric]"], \
            f"Expected auxilary_vars to be ['variable1 [Numeric]'], got {self.parent.auxilary_vars}"
        self.parent.auxilary_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_assign_auxilary_with_string_should_be_filtered(self):
        """Test assigning string variable to auxiliary should be filtered out."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_auxilary(self.parent)
        
        # Assert
        assert self.parent.auxilary_vars == [], \
            f"Expected auxilary_vars to remain empty for string variables, got {self.parent.auxilary_vars}"
        self.parent.variables_list.model().removeRow.assert_not_called()

    def test_assign_auxilary_multiple_variables_success(self):
        """Test assigning multiple numeric variables to auxiliary."""
        # Arrange
        index1 = MagicMock()
        index1.data.return_value = "variable1 [Numeric]"
        index2 = MagicMock()
        index2.data.return_value = "variable2 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index1, index2]
        
        # Act
        assign_auxilary(self.parent)
        
        # Assert
        assert set(self.parent.auxilary_vars) == {"variable1 [Numeric]", "variable2 [Numeric]"}, \
            f"Expected auxilary_vars to contain both variables, got {self.parent.auxilary_vars}"
        assert self.parent.variables_list.model().removeRow.call_count == 2, \
            "Expected removeRow to be called twice for two variables"
    
    def test_assign_vardir_with_numeric_success(self):
        """Test assigning numeric variable to vardir successfully."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_vardir(self.parent)
        
        # Assert
        assert self.parent.vardir_var == ["variable1 [Numeric]"], \
            f"Expected vardir_var to be ['variable1 [Numeric]'], got {self.parent.vardir_var}"
        self.parent.vardir_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()
    
    def test_assign_vardir_with_string_should_fail(self):
        """Test assigning string variable to vardir should be rejected."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_vardir(self.parent)
        
        # Assert
        assert self.parent.vardir_var == [], \
            f"Expected vardir_var to remain empty for string variables, got {self.parent.vardir_var}"
        self.parent.vardir_model.setStringList.assert_not_called()
        self.parent.variables_list.model().removeRow.assert_not_called()
    
    def test_assign_as_factor_success(self):
        """Test assigning variable to as_factor successfully."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_as_factor(self.parent)
        
        # Assert
        assert self.parent.as_factor_var == ["variable1 [String]"], \
            f"Expected as_factor_var to be ['variable1 [String]'], got {self.parent.as_factor_var}"
        self.parent.as_factor_model.setStringList.assert_called_with(["variable1 [String]"])
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_assign_as_factor_multiple_variables(self):
        """Test assigning multiple variables to as_factor."""
        # Arrange
        index1 = MagicMock()
        index1.data.return_value = "variable1 [String]"
        index2 = MagicMock()
        index2.data.return_value = "variable2 [Numeric]"
        self.parent.variables_list.selectedIndexes.return_value = [index1, index2]
        
        # Act
        assign_as_factor(self.parent)
        
        # Assert
        assert set(self.parent.as_factor_var) == {"variable1 [String]", "variable2 [Numeric]"}, \
            f"Expected as_factor_var to contain both variables, got {self.parent.as_factor_var}"
    
    def test_unassign_variable_of_interest_success(self):
        """Test unassigning variable from of_interest successfully."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.of_interest_model.setStringList(["variable1 [Numeric]"])
        self.parent.variables_list.model().insertRow = MagicMock()
        
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.of_interest_list.selectedIndexes.return_value = [index]
        
        # Act
        unassign_variable(self.parent)
        
        # Assert
        assert self.parent.of_interest_var == [], \
            f"Expected of_interest_var to be empty after unassign, got {self.parent.of_interest_var}"
        self.parent.of_interest_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
        self.parent.variables_list.model().setData.assert_called_with(
            self.parent.variables_list.model().index(0), "variable1 [Numeric]"
        )
    
    def test_unassign_variable_auxilary_success(self):
        """Test unassigning variable from auxiliary successfully."""
        # Arrange
        self.parent.auxilary_vars = ["variable1 [Numeric]"]
        self.parent.auxilary_model.setStringList(["variable1 [Numeric]"])
        self.parent.variables_list.model().insertRow = MagicMock()
        self.parent.variables_list.model().setData = MagicMock()
        self.parent.variables_list.model().index = MagicMock(return_value=0)

        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.auxilary_list.selectedIndexes.return_value = [index]

        # Patch selectedIndexes for other lists to return empty
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.vardir_list.selectedIndexes.return_value = []
        self.parent.as_factor_list.selectedIndexes.return_value = []

        # Act
        unassign_variable(self.parent)

        # Assert
        assert self.parent.auxilary_vars == [], \
            f"Expected auxilary_vars to be empty after unassign, got {self.parent.auxilary_vars}"
        self.parent.auxilary_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
        self.parent.variables_list.model().setData.assert_called_with(
            self.parent.variables_list.model().index(0), "variable1 [Numeric]"
        )
        
    def test_unassign_variable_vardir_success(self):
        """Test unassigning variable from vardir successfully."""
        # Arrange
        self.parent.vardir_var = ["variable1 [Numeric]"]
        self.parent.vardir_model.setStringList(["variable1 [Numeric]"])
        self.parent.variables_list.model().insertRow = MagicMock()
        self.parent.variables_list.model().setData = MagicMock()
        self.parent.variables_list.model().index = MagicMock(return_value=0)

        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        self.parent.vardir_list.selectedIndexes.return_value = [index]

        # Patch selectedIndexes for other lists to return empty
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_list.selectedIndexes.return_value = []
        self.parent.as_factor_list.selectedIndexes.return_value = []

        # Act
        unassign_variable(self.parent)

        # Assert
        assert self.parent.vardir_var == [], \
            f"Expected vardir_var to be empty after unassign, got {self.parent.vardir_var}"
        self.parent.vardir_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
        self.parent.variables_list.model().setData.assert_called_with(
            self.parent.variables_list.model().index(0), "variable1 [Numeric]"
        )
    
    def test_unassign_variable_as_factor_success(self):
        """Test unassigning variable from as_factor successfully."""
        # Arrange
        self.parent.as_factor_var = ["variable1 [String]"]
        self.parent.as_factor_model.setStringList(["variable1 [String]"])
        self.parent.variables_list.model().insertRow = MagicMock()
        self.parent.variables_list.model().setData = MagicMock()
        self.parent.variables_list.model().index = MagicMock(return_value=0)

        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.as_factor_list.selectedIndexes.return_value = [index]

        # Patch selectedIndexes for other lists to return empty
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_list.selectedIndexes.return_value = []
        self.parent.vardir_list.selectedIndexes.return_value = []

        # Act
        unassign_variable(self.parent)

        # Assert
        assert self.parent.as_factor_var == [], \
            f"Expected as_factor_var to be empty after unassign, got {self.parent.as_factor_var}"
        self.parent.as_factor_model.setStringList.assert_called_with([])
        self.parent.variables_list.model().insertRow.assert_called_once()
        self.parent.variables_list.model().setData.assert_called_with(
            self.parent.variables_list.model().index(0), "variable1 [String]"
        )

    def test_unassign_variable_no_selection_should_do_nothing(self):
        """Test unassign_variable with no selection should not change anything."""
        # Arrange
        initial_of_interest = self.parent.of_interest_var.copy()
        initial_auxilary = self.parent.auxilary_vars.copy()
        initial_vardir = self.parent.vardir_var.copy()
        initial_as_factor = self.parent.as_factor_var.copy()
        
        # Mock all lists to return empty selections
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_list.selectedIndexes.return_value = []
        self.parent.vardir_list.selectedIndexes.return_value = []
        self.parent.as_factor_list.selectedIndexes.return_value = []
        
        # Act
        unassign_variable(self.parent)
        
        # Assert
        assert self.parent.of_interest_var == initial_of_interest, \
            "Expected of_interest_var to remain unchanged when no selection"
        assert self.parent.auxilary_vars == initial_auxilary, \
            "Expected auxilary_vars to remain unchanged when no selection"
        assert self.parent.vardir_var == initial_vardir, \
            "Expected vardir_var to remain unchanged when no selection"
        assert self.parent.as_factor_var == initial_as_factor, \
            "Expected as_factor_var to remain unchanged when no selection"
    
    def test_get_selected_variables_success(self):
        """Test getting selected variables returns correct values."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]"]
        self.parent.vardir_var = ["variable3 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        
        # Act
        of_interest, auxilary, vardir, as_factor = get_selected_variables(self.parent)
        
        # Assert
        assert of_interest == ["variable1 [Numeric]"], \
            f"Expected of_interest to be ['variable1 [Numeric]'], got {of_interest}"
        assert auxilary == ["variable2 [Numeric]"], \
            f"Expected auxilary to be ['variable2 [Numeric]'], got {auxilary}"
        assert vardir == ["variable3 [Numeric]"], \
            f"Expected vardir to be ['variable3 [Numeric]'], got {vardir}"
        assert as_factor == ["variable4 [String]"], \
            f"Expected as_factor to be ['variable4 [String]'], got {as_factor}"

    def test_get_selected_variables_empty_lists(self):
        """Test getting selected variables with empty lists."""
        # Arrange - all variables are already empty from setup
        
        # Act
        of_interest, auxilary, vardir, as_factor = get_selected_variables(self.parent)
        
        # Assert
        assert of_interest == [], "Expected empty of_interest list"
        assert auxilary == [], "Expected empty auxilary list"
        assert vardir == [], "Expected empty vardir list"
        assert as_factor == [], "Expected empty as_factor list"

    def test_generate_r_script_complete_variables(self):
        """Test generating R script with all variable types."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]"]
        self.parent.vardir_var = ["variable3 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- variable1 ~ variable2 + as.factor(variable4)\n'
            'vardir_var <- data["variable3"]\n'
            'model<-mseFH(formula, vardir_var, method = "REML", data=data)'
        )
        assert r_script == expected_script, \
            f"Expected R script:\n{expected_script}\n\nGot:\n{r_script}"
    
    def test_generate_r_script_with_empty_vars_should_handle_gracefully(self):
        """Test generating R script with empty variables should create valid R code."""
        # Arrange
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- "" ~ 1\n'
            'vardir_var <- data[""""]\n'
            'model<-mseFH(formula, vardir_var, method = "REML", data=data)'
        )
        assert r_script == expected_script, \
            f"Expected R script for empty vars:\n{expected_script}\n\nGot:\n{r_script}"
        
    def test_generate_r_script_only_of_interest(self):
        """Test generating R script with only of_interest variable."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = []
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- variable1 ~ 1\n'
            'vardir_var <- data[""""]\n'
            'model<-mseFH(formula, vardir_var, method = "REML", data=data)'
        )
        assert r_script == expected_script, \
            f"Expected R script with only of_interest:\n{expected_script}\n\nGot:\n{r_script}"
    
    def test_generate_r_script_only_auxilary_should_create_incomplete_formula(self):
        """Test generating R script with only auxiliary variable creates incomplete formula."""
        # Arrange
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = ["variable2 [Numeric]"]
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- "" ~ variable2\n'
            'vardir_var <- data[""""]\n'
            'model<-mseFH(formula, vardir_var, method = "REML", data=data)'
        )
        assert r_script == expected_script, \
            f"Expected R script with only auxilary:\n{expected_script}\n\nGot:\n{r_script}"
    
    def test_generate_r_script_only_vardir(self):
        """Test generating R script with only vardir variable."""
        # Arrange
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.vardir_var = ["variable3 [Numeric]"]
        self.parent.as_factor_var = []
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- "" ~ 1\n'
            'vardir_var <- data["variable3"]\n'
            'model<-mseFH(formula, vardir_var, method = "REML", data=data)'
        )
        assert r_script == expected_script, \
            f"Expected R script with only vardir:\n{expected_script}\n\nGot:\n{r_script}"
    
    def test_generate_r_script_only_as_factor_should_create_incomplete_formula(self):
        """Test generating R script with only as_factor variable creates incomplete formula."""
        # Arrange
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.vardir_var = []
        self.parent.as_factor_var = ["variable4 [String]"]
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- "" ~ as.factor(variable4)\n'
            'vardir_var <- data[""""]\n'
            'model<-mseFH(formula, vardir_var, method = "REML", data=data)'
        )
        assert r_script == expected_script, \
            f"Expected R script with only as_factor:\n{expected_script}\n\nGot:\n{r_script}"
    
    def test_generate_r_script_multiple_auxilary_and_as_factor(self):
        """Test generating R script with multiple auxiliary and as_factor variables."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]", "variable3 [Numeric]"]
        self.parent.vardir_var = ["variable4 [Numeric]"]
        self.parent.as_factor_var = ["variable5 [String]", "variable6 [String]"]
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- variable1 ~ variable2 + variable3 + as.factor(variable5) + as.factor(variable6)\n'
            'vardir_var <- data["variable4"]\n'
            'model<-mseFH(formula, vardir_var, method = "REML", data=data)'
        )
        assert r_script == expected_script, \
            f"Expected R script with multiple variables:\n{expected_script}\n\nGot:\n{r_script}"
    
    def test_generate_r_script_multi_of_interest_should_use_first_only(self):
        """Test generating R script with multiple of_interest variables uses only the first one."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]", "variable2 [Numeric]"]
        self.parent.auxilary_vars = []
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- variable1 ~ 1\n'
            'vardir_var <- data[""""]\n'
            'model<-mseFH(formula, vardir_var, method = "REML", data=data)'
        )
        assert r_script == expected_script, \
            f"Expected R script with multi of_interest to use first only:\n{expected_script}\n\nGot:\n{r_script}"
    
    def test_generate_r_script_multi_vardir_should_use_first_only(self):
        """Test generating R script with multiple vardir variables uses only the first one."""
        # Arrange
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.vardir_var = ["variable1 [Numeric]", "variable2 [Numeric]"]
        self.parent.as_factor_var = []
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        expected_script = (
            'names(data) <- gsub(" ", "_", names(data)); #Replace space with underscore\n'
            'formula <- "" ~ 1\n'
            'vardir_var <- data["variable1"]\n'
            'model<-mseFH(formula, vardir_var, method = "REML", data=data)'
        )
        assert r_script == expected_script, \
            f"Expected R script with multi vardir to use first only:\n{expected_script}\n\nGot:\n{r_script}"

    def test_generate_r_script_with_invalid_method_should_fail(self):
        """Test generating R script with invalid method should be handled gracefully."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = []
        self.parent.vardir_var = ["variable2 [Numeric]"]
        self.parent.as_factor_var = []
        self.parent.method = "INVALID_METHOD"
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        assert "INVALID_METHOD" in r_script, \
            "Expected invalid method to be included in script for debugging purposes"

# Additional test configurations for pytest
def test_show_r_script_integration():
    """Integration test for show_r_script function."""
    # This test would require the actual function implementation
    pass

def test_edge_cases_and_error_handling():
    """Test edge cases and error handling scenarios."""
    # This would test various edge cases
    pass


if __name__ == '__main__':
    # Run with pytest for better output
    import sys
    import subprocess
    
    # Check if pytest is available
    try:
        import pytest
        # Run pytest with verbose output and custom formatting
        pytest.main([
            __file__, 
            '-v',  # verbose output
            '-s',  # show print statements
            '--tb=short',  # shorter traceback format
            '--color=yes',  # colored output
            '-x',  # stop on first failure
            '--disable-warnings'  # disable warnings for cleaner output
        ])
    except ImportError:
        print("pytest not found. Please install pytest: pip install pytest")
        print("Running basic test discovery...")
        # Fallback to basic test discovery
        import unittest
        unittest.main(verbosity=2)
