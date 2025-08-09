"""
Unit tests for SAE EBLUP Area functionality using pytest with AAA pattern.
This test suite follows the Arrange-Act-Assert pattern and includes both success and failure scenarios.
"""

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
        index.row.return_value = 0
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_of_interest(self.parent)
        
        # Assert
        assert self.parent.of_interest_var == ["variable1 [Numeric]"], \
            f"Expected of_interest_var to be ['variable1 [Numeric]'], got {self.parent.of_interest_var}"
        self.parent.of_interest_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()

    def test_assign_of_interest_with_string_should_show_warning(self):
        """Test assigning string variable to of_interest should show warning."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        initial_of_interest = self.parent.of_interest_var.copy()
        
        # Act
        assign_of_interest(self.parent)
        
        # Assert
        assert self.parent.of_interest_var == initial_of_interest, \
            f"Expected of_interest_var to remain unchanged for string variables, got {self.parent.of_interest_var}"
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
        index.row.return_value = 0
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_auxilary(self.parent)
        
        # Assert
        assert "variable1 [Numeric]" in self.parent.auxilary_vars, \
            f"Expected 'variable1 [Numeric]' to be in auxilary_vars, got {self.parent.auxilary_vars}"
        self.parent.auxilary_model.setStringList.assert_called()
        self.parent.variables_list.model().removeRow.assert_called()

    def test_assign_auxilary_with_string_should_be_filtered(self):
        """Test assigning string variable to auxiliary should be filtered out."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        initial_auxilary = self.parent.auxilary_vars.copy()
        
        # Act
        assign_auxilary(self.parent)
        
        # Assert
        assert self.parent.auxilary_vars == initial_auxilary, \
            f"Expected auxilary_vars to remain unchanged for string variables, got {self.parent.auxilary_vars}"

    def test_assign_auxilary_multiple_variables_success(self):
        """Test assigning multiple numeric variables to auxiliary."""
        # Arrange
        index1 = MagicMock()
        index1.data.return_value = "variable1 [Numeric]"
        index1.row.return_value = 0
        index1.__lt__ = MagicMock(return_value=True)  # Make MagicMock sortable
        index2 = MagicMock()
        index2.data.return_value = "variable2 [Numeric]"
        index2.row.return_value = 1
        index2.__lt__ = MagicMock(return_value=False)  # Make MagicMock sortable
        self.parent.variables_list.selectedIndexes.return_value = [index1, index2]
        
        # Act
        assign_auxilary(self.parent)
        
        # Assert
        assert "variable1 [Numeric]" in self.parent.auxilary_vars, \
            "Expected variable1 to be in auxilary_vars"
        assert "variable2 [Numeric]" in self.parent.auxilary_vars, \
            "Expected variable2 to be in auxilary_vars"
    
    def test_assign_vardir_with_numeric_success(self):
        """Test assigning numeric variable to vardir successfully."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        index.row.return_value = 0
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_vardir(self.parent)
        
        # Assert
        assert self.parent.vardir_var == ["variable1 [Numeric]"], \
            f"Expected vardir_var to be ['variable1 [Numeric]'], got {self.parent.vardir_var}"
        self.parent.vardir_model.setStringList.assert_called_with(["variable1 [Numeric]"])
        self.parent.variables_list.model().removeRow.assert_called_once()
    
    def test_assign_vardir_with_string_should_show_warning(self):
        """Test assigning string variable to vardir should show warning."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        initial_vardir = self.parent.vardir_var.copy()
        
        # Act
        assign_vardir(self.parent)
        
        # Assert
        assert self.parent.vardir_var == initial_vardir, \
            f"Expected vardir_var to remain unchanged for string variables, got {self.parent.vardir_var}"
        self.parent.variables_list.model().removeRow.assert_not_called()
    
    def test_assign_as_factor_success(self):
        """Test assigning variable to as_factor successfully."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        index.row.return_value = 0
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_as_factor(self.parent)
        
        # Assert
        assert "variable1 [String]" in self.parent.as_factor_var, \
            f"Expected 'variable1 [String]' to be in as_factor_var, got {self.parent.as_factor_var}"
        self.parent.as_factor_model.setStringList.assert_called()
        self.parent.variables_list.model().removeRow.assert_called()

    def test_assign_as_factor_multiple_variables(self):
        """Test assigning multiple variables to as_factor."""
        # Arrange
        index1 = MagicMock()
        index1.data.return_value = "variable1 [String]"
        index1.row.return_value = 0
        index1.__lt__ = MagicMock(return_value=True)  # Make MagicMock sortable
        index2 = MagicMock()
        index2.data.return_value = "variable2 [Numeric]"
        index2.row.return_value = 1
        index2.__lt__ = MagicMock(return_value=False)  # Make MagicMock sortable
        self.parent.variables_list.selectedIndexes.return_value = [index1, index2]
        
        # Act
        assign_as_factor(self.parent)
        
        # Assert
        assert "variable1 [String]" in self.parent.as_factor_var, \
            "Expected variable1 to be in as_factor_var"
        assert "variable2 [Numeric]" in self.parent.as_factor_var, \
            "Expected variable2 to be in as_factor_var"

    def test_unassign_variable_of_interest_success(self):
        """Test unassigning variable from of_interest successfully."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
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
        self.parent.variables_list.model().insertRow.assert_called()

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
        assert "variable1" in r_script, "Expected variable1 in R script"
        assert "variable2" in r_script, "Expected variable2 in R script"
        assert "variable3" in r_script, "Expected variable3 in R script"
        assert "as.factor(variable4)" in r_script, "Expected as.factor(variable4) in R script"
        assert "mseFH" in r_script, "Expected mseFH function call in R script"
    
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
        assert "formula" in r_script, "Expected formula definition in R script"
        assert "mseFH" in r_script, "Expected mseFH function call in R script"
        assert "method" in r_script, "Expected method parameter in R script"
        
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
        assert "variable1" in r_script, "Expected variable1 in R script"
        assert "~ 1" in r_script, "Expected intercept-only formula"
    
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
        assert "variable1" in r_script, "Expected variable1 in R script"
        assert "variable2" in r_script, "Expected variable2 in R script"
        assert "variable3" in r_script, "Expected variable3 in R script"
        assert "variable4" in r_script, "Expected variable4 in R script"
        assert "as.factor(variable5)" in r_script, "Expected as.factor(variable5) in R script"
        assert "as.factor(variable6)" in r_script, "Expected as.factor(variable6) in R script"


# Additional test configurations for pytest
def test_show_r_script_integration():
    """Integration test for show_r_script function."""
    # Arrange
    parent = MagicMock()
    parent.r_script_edit = MagicMock()
    parent.of_interest_var = ["test [Numeric]"]
    parent.auxilary_vars = []
    parent.vardir_var = ["variance [Numeric]"]
    parent.as_factor_var = []
    parent.method = "REML"
    parent.selection_method = "None"
    
    # Act
    show_r_script(parent)
    
    # Assert
    parent.r_script_edit.setText.assert_called_once()


@pytest.mark.parametrize("method,expected", [
    ("REML", "REML"),
    ("ML", "ML"),
    ("FH", "FH"),
])
def test_generate_r_script_with_different_methods(method, expected):
    """Test generating R script with different statistical methods."""
    # Arrange
    parent = MagicMock()
    parent.of_interest_var = ["variable1 [Numeric]"]
    parent.auxilary_vars = []
    parent.vardir_var = ["variable2 [Numeric]"]
    parent.as_factor_var = []
    parent.method = method
    parent.selection_method = "None"
    
    # Act
    r_script = generate_r_script(parent)
    
    # Assert
    assert f'method = "{expected}"' in r_script, \
        f"Expected method '{expected}' in R script, got: {r_script}"


if __name__ == '__main__':
    # Run with pytest for better output
    import sys
    import subprocess
    
    # Check if pytest is available
    try:
        import pytest
        print("=" * 80)
        print("🧪 RUNNING SAE EBLUP AREA TESTS WITH PYTEST")
        print("=" * 80)
        
        # Run pytest with verbose output and custom formatting
        exit_code = pytest.main([
            __file__, 
            '-v',  # verbose output
            '-s',  # show print statements
            '--tb=short',  # shorter traceback format
            '--color=yes',  # colored output
            '-x',  # stop on first failure
            '--disable-warnings',  # disable warnings for cleaner output
            '--capture=no',  # don't capture output
            '-q'  # quiet mode to reduce clutter
        ])
        
        print("\n" + "=" * 80)
        if exit_code == 0:
            print("✅ ALL TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED!")
        print("=" * 80)
        
    except ImportError:
        print("❌ pytest not found. Please install pytest: pip install pytest")
        print("Running basic test discovery...")
        # Fallback to basic test discovery
        import unittest
        unittest.main(verbosity=2)
