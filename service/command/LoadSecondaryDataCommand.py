from PyQt6.QtGui import QUndoCommand
import polars as pl

class LoadSecondaryDataCommand(QUndoCommand):
    """
    Command class for loading secondary data to the main model.
    This command will save the old state of the model before loading and merging secondary data,
    allowing for undo and redo operations.
    """
    
    def __init__(self, model, main_data, secondary_data, merge_option):
        """
        Initializes the LoadSecondaryDataCommand with model, main data, secondary data and merge option.

        :param model: The model containing the data.
        :param main_data: The main data before merging.
        :param secondary_data: The secondary data to be merged.
        :param merge_option: The merge option (0 for horizontal, 1 for diagonal).
        """
        super().__init__()
        self.model = model
        self.main_data = main_data
        self.secondary_data = secondary_data
        self.merge_option = merge_option
        self.merged_data = self._merge_data()
        self.setText("Load Secondary Data")

    def _merge_data(self):
        """
        Merges the main data and secondary data based on the merge option.
        
        :return: The merged data.
        """
        if self.merge_option == 0:  # Horizontal
            common_cols = set(self.main_data.columns) & set(self.secondary_data.columns)
            rename_map = {col: f"{col}_duplicate" for col in common_cols}
            renamed_secondary = self.secondary_data.rename(rename_map)
            return pl.concat([self.main_data, renamed_secondary], how="horizontal")
        else:  # Diagonal
            # Try to cast columns to compatible types for diagonal merge
            for col in set(self.main_data.columns) & set(self.secondary_data.columns):
                main_dtype = self.main_data[col].dtype
                try:
                    self.secondary_data = self.secondary_data.with_columns(
                        pl.col(col).cast(main_dtype, strict=False)
                    )
                except Exception:
                    pass  # Ignore casting errors, let polars handle it during concat
            return pl.concat([self.main_data, self.secondary_data], how="diagonal")

    def undo(self):
        """
        Undo the loading of secondary data by restoring the main data.
        """
        self.model.set_data(self.main_data)

    def redo(self):
        """
        Redo the loading of secondary data by setting the merged data again.
        """
        self.model.set_data(self.merged_data)
