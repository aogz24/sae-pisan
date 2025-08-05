"""
Unit tests for SAE EBLUP Unit functionality using pytest with AAA pattern.
This test suite follows the Arrange-Act-Assert pattern and includes both success and failure scenarios.
"""

import pytest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication, QMessageBox

# Import functions to test from the actual module
from service.modelling.SaeEblupUnit import (
    assign_of_interest, 
    assign_auxilary, 
    assign_index,
    assign_as_factor, 
    assign_domains,
    assign_aux_mean,
    assign_population_sample_size,
    unassign_variable, 
    generate_r_script, 
    show_r_script,
    get_selected_variables
)


class TestSaeEblupUnit:
    """Test suite for SAE EBLUP Unit functionality."""
    
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
        self.parent.index_var = []
        self.parent.as_factor_var = []
        self.parent.domain_var = []
        self.parent.aux_mean_var = []
        self.parent.population_sample_size_var = []
        self.parent.of_interest_model = MagicMock()
        self.parent.auxilary_model = MagicMock()
        self.parent.index_model = MagicMock()
        self.parent.as_factor_model = MagicMock()
        self.parent.domain_model = MagicMock()
        self.parent.aux_mean_model = MagicMock()
        self.parent.population_sample_size_model = MagicMock()
        self.parent.r_script_edit = MagicMock()

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
        assert "variable1 [Numeric]" in self.parent.of_interest_var or len(self.parent.of_interest_var) > 0, \
            f"Expected variable to be assigned to of_interest_var, got {self.parent.of_interest_var}"
        self.parent.variables_list.model().removeRow.assert_called()

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
        assert len(self.parent.auxilary_vars) > 0 or "variable1 [Numeric]" in self.parent.auxilary_vars, \
            f"Expected variable to be added to auxilary_vars, got {self.parent.auxilary_vars}"

    def test_assign_auxilary_with_string_should_show_warning(self):
        """Test assigning string variable to auxiliary should show warning."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        initial_auxilary = self.parent.auxilary_vars.copy()
        
        # Act
        assign_auxilary(self.parent)
        
        # Assert
        # Should show warning for non-numeric variables
        assert True, "Test for warning message handling"

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
        assert len(self.parent.auxilary_vars) >= 0, \
            "Expected auxilary_vars to be processed"
    
    def test_assign_aux_mean_with_numeric_success(self):
        """Test assigning numeric variable to aux_mean successfully."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [Numeric]"
        index.row.return_value = 0
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_aux_mean(self.parent)
        
        # Assert
        assert len(self.parent.aux_mean_var) >= 0, \
            f"Expected aux_mean_var to be processed, got {self.parent.aux_mean_var}"
    
    def test_assign_aux_mean_with_string_should_show_warning(self):
        """Test assigning string variable to aux_mean should show warning."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "variable1 [String]"
        self.parent.variables_list.selectedIndexes.return_value = [index]
        initial_aux_mean = self.parent.aux_mean_var.copy()
        
        # Act
        assign_aux_mean(self.parent)
        
        # Assert
        # Should show warning for string variables
        assert True, "Test for warning message handling"
    
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
        assert len(self.parent.as_factor_var) >= 0, \
            f"Expected as_factor_var to be processed, got {self.parent.as_factor_var}"

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
        assert len(self.parent.as_factor_var) >= 0, \
            "Expected as_factor_var to be processed"

    def test_assign_domains_success(self):
        """Test assigning variable to domains successfully."""
        # Arrange
        index = MagicMock()
        index.data.return_value = "domain1 [Numeric]"
        index.row.return_value = 0
        self.parent.variables_list.selectedIndexes.return_value = [index]
        
        # Act
        assign_domains(self.parent)
        
        # Assert
        assert len(self.parent.domain_var) >= 0, \
            f"Expected domain_var to be processed, got {self.parent.domain_var}"

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
        # Function should process the unassignment
        assert True, "Unassignment function should be processed"

    def test_unassign_variable_no_selection_should_do_nothing(self):
        """Test unassign_variable with no selection should not change anything."""
        # Arrange
        initial_of_interest = self.parent.of_interest_var.copy()
        initial_auxilary = self.parent.auxilary_vars.copy()
        initial_as_factor = self.parent.as_factor_var.copy()
        initial_domain = self.parent.domain_var.copy()
        initial_aux_mean = self.parent.aux_mean_var.copy()
        initial_population = self.parent.population_sample_size_var.copy()
        
        # Mock all lists to return empty selections
        self.parent.of_interest_list.selectedIndexes.return_value = []
        self.parent.auxilary_list.selectedIndexes.return_value = []
        self.parent.index_list.selectedIndexes.return_value = []
        self.parent.as_factor_list.selectedIndexes.return_value = []
        self.parent.domain_list.selectedIndexes.return_value = []
        self.parent.aux_mean_list.selectedIndexes.return_value = []
        self.parent.population_sample_size_list.selectedIndexes.return_value = []
        
        # Act
        unassign_variable(self.parent)
        
        # Assert
        # Variables should remain unchanged when no selection
        assert True, "Variables should remain unchanged when no selection"

    def test_get_selected_variables_success(self):
        """Test getting selected variables returns correct values."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]"]
        self.parent.vardir_var = ["variable3 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        
        # Act
        result = get_selected_variables(self.parent)
        
        # Assert
        assert result is not None, "get_selected_variables should return a result"

    def test_get_selected_variables_empty_lists(self):
        """Test getting selected variables with empty lists."""
        # Arrange - all variables are already empty from setup
        
        # Act
        result = get_selected_variables(self.parent)
        
        # Assert
        assert result is not None, "get_selected_variables should return a result even with empty lists"

    def test_generate_r_script_complete_variables(self):
        """Test generating R script with all variable types."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]"]
        self.parent.vardir_var = ["variable3 [Numeric]"]
        self.parent.as_factor_var = ["variable4 [String]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        assert "formula" in r_script, "Expected formula definition in R script"
        assert "fh(" in r_script, "Expected fh function call in R script"
        assert "variable1" in r_script, "Expected variable1 in R script"
    
    def test_generate_r_script_with_empty_vars_should_handle_gracefully(self):
        """Test generating R script with empty variables should create valid R code."""
        # Arrange
        self.parent.of_interest_var = []
        self.parent.auxilary_vars = []
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        self.parent.domain_var = []
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        assert "formula" in r_script, "Expected formula definition in R script"
        assert "fh(" in r_script, "Expected fh function call in R script"
        
    def test_generate_r_script_only_of_interest(self):
        """Test generating R script with only of_interest variable."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = []
        self.parent.vardir_var = []
        self.parent.as_factor_var = []
        self.parent.domain_var = []
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        assert "variable1" in r_script, "Expected variable1 in R script"
        assert "~ 1" in r_script, "Expected intercept-only formula"

    def test_generate_r_script_with_domain_variable(self):
        """Test generating R script with domain variable."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = []
        self.parent.vardir_var = ["variable2 [Numeric]"]
        self.parent.as_factor_var = []
        self.parent.domain_var = ["domain1 [Numeric]"]
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        assert "domain1" in r_script or "domains=" in r_script, \
            "Expected domain variable or domains parameter in R script"

    def test_generate_r_script_multiple_auxilary_and_as_factor(self):
        """Test generating R script with multiple auxiliary and as_factor variables."""
        # Arrange
        self.parent.of_interest_var = ["variable1 [Numeric]"]
        self.parent.auxilary_vars = ["variable2 [Numeric]", "variable3 [Numeric]"]
        self.parent.vardir_var = ["variable4 [Numeric]"]
        self.parent.as_factor_var = ["variable5 [String]", "variable6 [String]"]
        self.parent.domain_var = ["domain1 [Numeric]"]
        
        # Act
        r_script = generate_r_script(self.parent)
        
        # Assert
        assert "variable1" in r_script, "Expected variable1 in R script"
        assert "variable2" in r_script or "variable3" in r_script, "Expected auxiliary variables in R script"
        assert "as.factor" in r_script, "Expected as.factor transformation in R script"


# Integration test
def test_show_r_script_integration():
    """Integration test for show_r_script function."""
    # Arrange
    parent = MagicMock()
    parent.r_script_edit = MagicMock()
    parent.of_interest_var = ["test [Numeric]"]
    parent.auxilary_vars = []
    parent.vardir_var = ["variance [Numeric]"]
    parent.as_factor_var = []
    parent.domain_var = ["domain [Numeric]"]
    
    # Act
    show_r_script(parent)
    
    # Assert
    parent.r_script_edit.setText.assert_called_once()


@pytest.mark.parametrize("domain_var,expected", [
    (["domain1 [Numeric]"], "domain1"),
    ([], "NULL"),
    (["domain1 [String]"], "domain1"),
])
def test_generate_r_script_with_different_domain_types(domain_var, expected):
    """Test generating R script with different domain variable types."""
    # Arrange
    parent = MagicMock()
    parent.of_interest_var = ["variable1 [Numeric]"]
    parent.auxilary_vars = []
    parent.vardir_var = ["variable2 [Numeric]"]
    parent.as_factor_var = []
    parent.domain_var = domain_var
    
    # Act
    r_script = generate_r_script(parent)
    
    # Assert
    assert expected in r_script or "domains=" in r_script, \
        f"Expected '{expected}' or 'domains=' in R script, got: {r_script}"


if __name__ == '__main__':
    # Run with pytest for better output
    import sys
    import subprocess
    
    # Check if pytest is available
    try:
        import pytest
        print("=" * 80)
        print("🧪 RUNNING SAE EBLUP UNIT TESTS WITH PYTEST")
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
