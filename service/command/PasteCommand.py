from PyQt6.QtGui import QUndoCommand
from PyQt6.QtCore import Qt

class PasteCommand(QUndoCommand):
    """
    Command to paste multiple cells at once.
    This command is used to paste clipboard data into multiple cells in a model.
    It supports undo and redo operations to revert or reapply all changes at once.
    
    Attributes:
        model: The model containing the data to be edited.
        start_row: The starting row index for the paste operation.
        start_col: The starting column index for the paste operation.
        data: The 2D array of data to be pasted.
        old_values: The original values of the cells before the paste.
    """
    
    def __init__(self, model, start_row, start_col, data):
        super().__init__()
        self.model = model
        self.start_row = start_row
        self.start_col = start_col
        self.data = data
        self.old_values = []
        
        # Store old values
        for i, row in enumerate(data):
            row_values = []
            for j, _ in enumerate(row):
                if (self.start_row + i < self.model.rowCount(None) and 
                    self.start_col + j < self.model.columnCount(None)):
                    row_values.append(self.model._data[self.start_row + i, self.start_col + j])
                else:
                    # Handle the case when pasting outside the existing bounds
                    row_values.append(None)
            self.old_values.append(row_values)
        
        self.setText(f"Paste multiple cells starting at ({start_row}, {start_col})")

    def undo(self):
        """Revert all cells to their original values at once"""
        import polars as pl
        
        for i, row in enumerate(self.old_values):
            for j, old_value in enumerate(row):
                if (self.start_row + i < self.model.rowCount(None) and 
                    self.start_col + j < self.model.columnCount(None)):
                    # Get column name for accessing the data
                    column_name = self.model._data.columns[self.start_col + j]
                    
                    # Set the data directly in the model using a safer approach
                    try:
                        self.model._data = self.model._data.with_row_count("__temp_row_idx")
                        mask = self.model._data["__temp_row_idx"] == self.start_row + i
                        self.model._data = self.model._data.with_columns(
                            pl.when(mask).then(pl.lit(old_value)).otherwise(pl.col(column_name)).alias(column_name)
                        )
                        self.model._data = self.model._data.drop("__temp_row_idx")
                    except Exception as e:
                        print(f"Error restoring value at {self.start_row + i}, {self.start_col + j}: {e}")
        
        # Emit dataChanged for the entire range
        top_left = self.model.createIndex(self.start_row, self.start_col)
        bottom_right = self.model.createIndex(
            min(self.start_row + len(self.old_values) - 1, self.model.rowCount(None) - 1),
            min(self.start_col + max(len(row) for row in self.old_values) - 1, self.model.columnCount(None) - 1)
        )
        self.model.dataChanged.emit(top_left, bottom_right)

    def redo(self):
        """Apply all new values at once"""
        import polars as pl
        from PyQt6 import QtWidgets
        
        for i, row in enumerate(self.data):
            for j, value in enumerate(row):
                if (self.start_row + i < self.model.rowCount(None) and 
                    self.start_col + j < self.model.columnCount(None)):
                    # Get column name and data type for validation
                    column_name = self.model._data.columns[self.start_col + j]
                    dtype = self.model._data[column_name].dtype
                    
                    # Process value based on dtype (similar to what setData would do)
                    processed_value = value
                    
                    # Handle null dtype - need to cast the column to an appropriate type first
                    if dtype == pl.Null:
                        if isinstance(value, str):
                            val_strip = value.strip() if value else ""
                            val_dot = val_strip.replace(',', '.')
                            try:
                                float_val = float(val_dot)
                                if '.' in val_dot:
                                    new_dtype = pl.Float64
                                    processed_value = float_val
                                else:
                                    new_dtype = pl.Int64
                                    processed_value = int(float_val)
                            except ValueError:
                                new_dtype = pl.Utf8
                        elif isinstance(value, float):
                            new_dtype = pl.Float64
                        elif isinstance(value, int):
                            new_dtype = pl.Int64
                        else:
                            new_dtype = pl.Utf8
                        
                        # Cast the column to the appropriate type
                        self.model._data = self.model._data.with_columns([pl.col(column_name).cast(new_dtype)])
                        # Update dtype to the new type
                        dtype = new_dtype
                    
                    # For numeric types, try to convert the value
                    if dtype == pl.Float64:
                        try:
                            if isinstance(value, str):
                                if value and value.count(',') == 1 and value.replace(',', '').isdigit():
                                    processed_value = value.replace(',', '.')
                                processed_value = float(processed_value) if processed_value else None
                        except ValueError:
                            # Keep as string if conversion fails
                            self.model._data = self.model._data.with_columns([pl.col(column_name).cast(pl.Utf8)])
                            processed_value = value
                    elif dtype == pl.Int64:
                        try:
                            if isinstance(value, str):
                                processed_value = int(float(processed_value)) if processed_value else None
                        except ValueError:
                            # Keep as string if conversion fails
                            self.model._data = self.model._data.with_columns([pl.col(column_name).cast(pl.Utf8)])
                            processed_value = value
                    
                    # Set the data directly in the model - using loc to avoid the null dtype issue
                    try:
                        self.model._data = self.model._data.with_row_count("__temp_row_idx")
                        mask = self.model._data["__temp_row_idx"] == self.start_row + i
                        self.model._data = self.model._data.with_columns(
                            pl.when(mask).then(pl.lit(processed_value)).otherwise(pl.col(column_name)).alias(column_name)
                        )
                        self.model._data = self.model._data.drop("__temp_row_idx")
                    except Exception as e:
                        print(f"Error setting value at {self.start_row + i}, {self.start_col + j}: {e}")
        
        # Emit dataChanged for the entire range
        top_left = self.model.createIndex(self.start_row, self.start_col)
        bottom_right = self.model.createIndex(
            min(self.start_row + len(self.data) - 1, self.model.rowCount(None) - 1),
            min(self.start_col + max(len(row) for row in self.data) - 1, self.model.columnCount(None) - 1)
        )
        self.model.dataChanged.emit(top_left, bottom_right)
                    
        # Emit dataChanged for the entire range
        top_left = self.model.createIndex(self.start_row, self.start_col)
        bottom_right = self.model.createIndex(
            min(self.start_row + len(self.data) - 1, self.model.rowCount(None) - 1),
            min(self.start_col + max(len(row) for row in self.data) - 1, self.model.columnCount(None) - 1)
        )
        self.model.dataChanged.emit(top_left, bottom_right)
