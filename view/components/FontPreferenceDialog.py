import os
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, 
    QPushButton, QHBoxLayout, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal

class FontPreferenceDialog(QDialog):
    """
    Dialog for selecting font size preference when the application is first run.
    This dialog presents font size options for the user to choose from,
    and provides a preview of how the selected font size will look.
    """
    
    font_size_selected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Font Size Preference")
        self.setMinimumWidth(300)
        # In PyQt6, we use WindowType.ContextHelpButtonHint instead of WindowContextHelpButtonHint
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # Ensure dialog is modal
        self.setModal(True)
        
        # Available font sizes
        self.sizes = {
            "Small": 10,
            "Medium": 12,
            "Large": 16,
            "Extra Large": 20
        }
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI elements"""
        layout = QVBoxLayout(self)
        
        # Welcome text
        welcome_label = QLabel("Welcome to saePisan!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(welcome_label)
        
        # Instruction text
        instruction_label = QLabel(
            "Please select your preferred font size for the application. "
            "You can change this setting later in the Settings menu."
        )
        instruction_label.setWordWrap(True)
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instruction_label)
        
        # Font size selector
        layout.addSpacing(15)
        selector_label = QLabel("Select Font Size:")
        layout.addWidget(selector_label)
        
        self.combo_box = QComboBox()
        self.combo_box.addItems(self.sizes.keys())
        self.combo_box.setCurrentText("Medium")  # Default to Medium
        layout.addWidget(self.combo_box)
        
        # Preview area
        layout.addSpacing(15)
        preview_label = QLabel("Preview:")
        layout.addWidget(preview_label)
        
        self.preview_widget = QWidget()
        preview_layout = QVBoxLayout(self.preview_widget)
        
        self.preview_text = QLabel("AaBbCc 123")
        self.preview_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_text.setStyleSheet(f"font-size: {self.sizes['Medium']}px;")
        preview_layout.addWidget(self.preview_text)
        
        self.preview_widget.setLayout(preview_layout)
        self.preview_widget.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 10px;")
        layout.addWidget(self.preview_widget)
        
        # Button area
        layout.addSpacing(15)
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Confirm")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)
        
        # Connect signals
        self.combo_box.currentTextChanged.connect(self.update_preview)
        
        self.setLayout(layout)
    
    def update_preview(self):
        """Update the preview text based on the selected font size"""
        selected_size = self.combo_box.currentText()
        self.preview_text.setStyleSheet(f"font-size: {self.sizes[selected_size]}px;")
    
    def get_selected_font_size(self):
        """Return the selected font size value"""
        selected_text = self.combo_box.currentText()
        return self.sizes[selected_text]
    
    def accept(self):
        """Handle dialog acceptance and emit the selected font size"""
        self.font_size_selected.emit(self.get_selected_font_size())
        super().accept()

def save_font_preference(font_size):
    """
    Save the selected font size preference to a settings file.
    
    Args:
        font_size (int): The font size to save
    """
    try:
        app_data_dir = os.path.join(os.getenv("APPDATA"), "saePisan")
        os.makedirs(app_data_dir, exist_ok=True)
        
        settings_file = os.path.join(app_data_dir, 'settings.json')
        
        # Load existing settings if file exists
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        else:
            settings = {}
        
        # Update font size setting
        settings['font_size'] = font_size
        
        # Save settings
        with open(settings_file, 'w') as f:
            json.dump(settings, f)
            
    except Exception as e:
        print(f"Error saving font preference: {e}")

def load_font_preference():
    """
    Load the saved font size preference from the settings file.
    
    Returns:
        int: The saved font size, or 12 (Medium) if not found
    """
    try:
        app_data_dir = os.path.join(os.getenv("APPDATA"), "saePisan")
        settings_file = os.path.join(app_data_dir, 'settings.json')
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                return settings.get('font_size', 12)  # Default to 12 if not found
        
        return 12  # Default font size (Medium)
    
    except Exception as e:
        print(f"Error loading font preference: {e}")
        return 12  # Default to Medium on error
