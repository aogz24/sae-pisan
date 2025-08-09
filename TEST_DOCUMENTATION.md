# Unit Test SAE EBLUP Area - Dokumentasi

## 📋 Ringkasan

File ini berisi unit test untuk modul **SAE EBLUP Area** yang telah disesuaikan dengan best practices menggunakan:

- ✅ **Pytest** sebagai testing framework
- ✅ **AAA Pattern** (Arrange-Act-Assert)
- ✅ **Descriptive test names** yang menjelaskan fungsi dan expected behavior
- ✅ **Test untuk kondisi sukses dan gagal**
- ✅ **Pesan error yang informatif**
- ✅ **Parametrized tests** untuk test multiple scenarios

## 🧪 Test Coverage

### Functions Yang Di-test:

1. `assign_of_interest()` - Assignment variabel of interest
2. `assign_auxilary()` - Assignment variabel auxiliary
3. `assign_vardir()` - Assignment variabel variance direction
4. `assign_as_factor()` - Assignment variabel as factor
5. `unassign_variable()` - Unassignment variabel dari semua kategori
6. `get_selected_variables()` - Getter untuk semua variabel terpilih
7. `generate_r_script()` - Generator R script untuk modeling
8. `show_r_script()` - Integration test untuk display R script

### Test Scenarios:

- ✅ **Success cases**: Normal operation dengan data valid
- ✅ **Failure cases**: Handling input yang tidak valid (e.g., String untuk Numeric field)
- ✅ **Edge cases**: Empty lists, multiple variables, invalid methods
- ✅ **Integration tests**: End-to-end functionality

## 📊 Test Results

```
============================= 23 passed in 6.61s =============================
```

**Total Tests**: 23
**Passed**: 23 ✅
**Failed**: 0 ❌
**Success Rate**: 100%

## 🚀 Cara Menjalankan Test

### Menggunakan pytest (Recommended):

```bash
# Install pytest jika belum ada
pip install pytest

# Jalankan test dengan output verbose
python -m pytest test/modelling/script/test_sae_eblup_area_new.py -v

# Jalankan dengan coverage report
python -m pytest test/modelling/script/test_sae_eblup_area_new.py -v --cov=service.modelling

# Jalankan test spesifik
python -m pytest test/modelling/script/test_sae_eblup_area_new.py::TestSaeEblupArea::test_assign_of_interest_with_numeric_success -v
```

### Menggunakan script PowerShell:

```powershell
# Jalankan script yang sudah disediakan
.\run_tests.ps1
```

### Menjalankan dari Python file:

```bash
# Jalankan file test langsung
python test/modelling/script/test_sae_eblup_area_new.py
```

## 🎯 Test Design Principles

### AAA Pattern Example:

```python
def test_assign_of_interest_with_numeric_success(self):
    """Test assigning numeric variable to of_interest successfully."""
    # Arrange - Setup test data
    index = MagicMock()
    index.data.return_value = "variable1 [Numeric]"
    index.row.return_value = 0
    self.parent.variables_list.selectedIndexes.return_value = [index]

    # Act - Execute the function under test
    assign_of_interest(self.parent)

    # Assert - Verify the results
    assert self.parent.of_interest_var == ["variable1 [Numeric]"], \
        f"Expected of_interest_var to be ['variable1 [Numeric]'], got {self.parent.of_interest_var}"
```

### Descriptive Test Names:

- `test_assign_of_interest_with_numeric_success()` - ✅ Clear what it tests
- `test_assign_of_interest_with_string_should_show_warning()` - ✅ Explains expected behavior
- `test_generate_r_script_with_invalid_method_should_fail()` - ✅ Describes failure scenario

## 📈 Test Output Contoh

```
test_assign_of_interest_with_numeric_success PASSED [  4%]
test_assign_of_interest_with_string_should_show_warning PASSED [  8%]
test_assign_of_interest_with_no_selection_should_do_nothing PASSED [ 13%]
test_assign_auxilary_with_numeric_success PASSED [ 17%]
test_assign_auxilary_with_string_should_be_filtered PASSED [ 21%]
test_assign_auxilary_multiple_variables_success PASSED [ 26%]
...
```

## ⚙️ Configuration Files

### pytest.ini

File konfigurasi pytest untuk konsistensi output dan behavior.

### run_tests.ps1

Script PowerShell untuk menjalankan test dengan output yang user-friendly.

## 🔧 Dependencies

```txt
pytest>=8.0.0
PyQt6
unittest.mock (built-in)
```

## 📝 Notes

- Test menggunakan **MagicMock** untuk mocking PyQt6 objects
- **Windows fatal exception** yang muncul pada beberapa test adalah karena PyQt6 QMessageBox, namun test tetap PASSED
- Test di-design untuk bisa berjalan **tanpa GUI** (headless mode)
- Semua test **independent** dan bisa dijalankan dalam order apapun

## 🎉 Benefits

1. **Maintainability**: Test yang jelas dan mudah dipahami
2. **Reliability**: Comprehensive coverage untuk success dan failure cases
3. **Documentation**: Test names berfungsi sebagai living documentation
4. **Debugging**: Error messages yang informatif memudahkan debugging
5. **CI/CD Ready**: Compatible dengan automation pipelines
