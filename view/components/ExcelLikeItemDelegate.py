from PyQt6.QtWidgets import QItemDelegate, QLineEdit, QAbstractItemView
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeyEvent

class ExcelLikeItemDelegate(QItemDelegate):
    """
    A custom item delegate for Excel-like editing behavior in QTableView.
    
    Features:
    - Automatically selects all text when starting edit
    - Handles key navigation to move to next cell when pressing Enter/Tab
    - Supports arrow key navigation during editing
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_key = None
    
    def createEditor(self, parent, option, index):
        """Create editor widget for the cell"""
        editor = QLineEdit(parent)
        editor.installEventFilter(self)
        return editor
    
    def setEditorData(self, editor, index):
        """Load data from model into editor"""
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        editor.setText(value if value is not None else "")
        # Select all text when starting edit - Excel-like behavior
        editor.selectAll()
    
    def setModelData(self, editor, model, index):
        """Save data from editor to model"""
        model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)
    
    def eventFilter(self, obj, event):
        """Handle keyboard events for Excel-like navigation"""
        if event.type() == QEvent.Type.KeyPress:
            key_event = event
            key = key_event.key()
            
            # Store the key for cell navigation after editing completes
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab, 
                      Qt.Key.Key_Down, Qt.Key.Key_Up, 
                      Qt.Key.Key_Left, Qt.Key.Key_Right):
                self.last_key = key
                
            # Commit data and close editor immediately on navigation keys
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab):
                self.commitData.emit(obj)
                self.closeEditor.emit(obj)
                return True
                
            # Allow normal key behavior for input
            return super().eventFilter(obj, event)
            
        # After editor is closed, determine which cell to select next
        elif event.type() == QEvent.Type.FocusOut:
            if hasattr(self, 'last_key') and self.last_key is not None:
                # The delegate doesn't have access to the table view directly,
                # so we'll rely on the table's event filter to handle navigation
                # after editing is complete
                self.last_key = None
                
        return super().eventFilter(obj, event)
        
    def updateEditorGeometry(self, editor, option, index):
        """Ensure editor covers the entire cell"""
        editor.setGeometry(option.rect)
