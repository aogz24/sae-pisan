from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, QObject, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QIcon, QAction
import os

from view.components.TutorialOverlay import TutorialOverlay

class TutorialStep:
    """
    Represents a single step in the tutorial sequence.
    
    Attributes:
        target (str): The object name of the target widget or action
        message (str): The instruction message for this step
        target_type (str): The type of target ('widget', 'menu', 'toolbar', 'tab')
        action (str, optional): An optional action to perform before showing this step
        delay (int, optional): Delay in milliseconds before showing this step
    """
    def __init__(self, target, message, target_type="widget", action=None, delay=0):
        self.target = target
        self.message = message
        self.target_type = target_type
        self.action = action
        self.delay = delay
        
class TutorialManager(QObject):
    """
    Manages the interactive tutorial system for the application.
    
    This class is responsible for coordinating tutorial steps, finding target widgets,
    displaying the overlay, and handling user navigation through the tutorial.
    
    Attributes:
        tutorial_completed (pyqtSignal): Signal emitted when the entire tutorial is completed
        tutorial_skipped (pyqtSignal): Signal emitted when the tutorial is skipped
        tutorial_step_changed (pyqtSignal): Signal emitted when the tutorial step changes
    """
    tutorial_completed = pyqtSignal()
    tutorial_skipped = pyqtSignal()
    tutorial_step_changed = pyqtSignal(int)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.overlay = None
        self.steps = []
        self.current_step_index = -1
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._show_current_step)
        
        # Setup tutorial steps
        self._init_tutorial_steps()
        
    def _init_tutorial_steps(self):
        """Initialize the tutorial steps for the application"""
        # Welcome step
        self.steps.append(TutorialStep(
            target="",  # Empty target means center of screen
            message="Welcome to saePisan! This tutorial will guide you through the main features of the application. Click 'Next' to continue.",
            target_type="center"
        ))
        
        # File menu
        self.steps.append(TutorialStep(
            target="File",
            message="The File menu allows you to open data files, save your work, and export results. The Open File option lets you import data from various formats like CSV and Excel.",
            target_type="menu_text"
        ))
        
        # Data Editor tab
        self.steps.append(TutorialStep(
            target="tab1",
            message="The Data Editor is where you can view and edit your data. You can add, remove, or modify rows and columns. Right-click on cells for more options.",
            target_type="tab",
            action="activate_tab_0"
        ))
        
        # Data Output tab
        self.steps.append(TutorialStep(
            target="tab2",
            message="The Data Output tab displays the results of your statistical analysis. These results can be saved or exported for use in reports.",
            target_type="tab",
            action="activate_tab_1"
        ))
        
        # Output tab
        self.steps.append(TutorialStep(
            target="tab3",
            message="The Output tab shows detailed information, scripts, and visualizations from your analyses. You can save these outputs to PDF.",
            target_type="tab",
            action="activate_tab_2"
        ))
        
        # Exploration menu
        self.steps.append(TutorialStep(
            target="Exploration",
            message="The Exploration menu provides tools for initial data analysis, including summary statistics and normality tests.",
            target_type="menu_text",
            action="activate_tab_0"
        ))

        # Pre-Modeling menu
        self.steps.append(TutorialStep(
            target="Pre-Modeling",
            message="The Pre-Modeling menu provides tools to prepare data before modeling, such as correlation analysis, multicollinearity checks, and variable selection.",
            target_type="menu_text",
            action="activate_tab_0"
        ))
        
        # Graph menu
        self.steps.append(TutorialStep(
            target="Graph",
            message="The Graph menu offers various visualization options like scatter plots, box plots, line plots, and histograms to help you understand your data patterns.",
            target_type="menu_text"
        ))
        
        # Model menu
        self.steps.append(TutorialStep(
            target="Model", # Gunakan teks menu langsung untuk menu yang tidak tersedia sebagai atribut
            message="The Model menu contains different Small Area Estimation methods including Area Level models (EBLUP, HB Beta), Unit Level models, Pseudo, and Projection Estimation.",
            target_type="menu_text"  # Gunakan tipe target khusus
        ))
        
        # Compute menu
        self.steps.append(TutorialStep(
            target="Compute",
            message="The Compute menu allows you to perform calculations and create new variables based on existing data.",
            target_type="menu_text"
        ))
        
        # Settings menu
        self.steps.append(TutorialStep(
            target="Settings",
            message="The Settings menu provides options to customize the application according to your preferences.",
            target_type="menu_text"
        ))
        
        # About menu
        self.steps.append(TutorialStep(
            target="About",
            message="The About menu contains information about the application, documentation, and help resources.",
            target_type="menu_text"
        ))
        
        # Toolbar
        self.steps.append(TutorialStep(
            target="toolBar",
            message="The toolbar provides quick access to common functions. You can open files, save data, undo/redo changes, and compute new variables using these buttons.",
            target_type="toolbar"
        ))
        
        # Final step
        self.steps.append(TutorialStep(
            target="",
            message="Congratulations! You've completed the saePisan tutorial. You can now start using the application to analyze your data. If you need help, check the 'About' menu.",
            target_type="center"
        ))
        
    def start_tutorial(self):
        """Start the tutorial from the beginning"""
        # Ensure the main window is fully initialized
        if not self.main_window.isVisible():
            QTimer.singleShot(1000, self.start_tutorial)
            return
            
        if not self.overlay:
            self.overlay = TutorialOverlay(self.main_window)
            self.overlay.next_clicked.connect(self.next_step)
            self.overlay.prev_clicked.connect(self.previous_step)
            self.overlay.skip_clicked.connect(self.skip_tutorial)
            
        self.current_step_index = -1
        self.next_step()
        
    def next_step(self):
        """Advance to the next tutorial step"""
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            self._handle_step_action()
            self.timer.start(self.steps[self.current_step_index].delay)
        else:
            # Tutorial completed
            self._end_tutorial()
            self.tutorial_completed.emit()
            
    def previous_step(self):
        """Go back to the previous tutorial step"""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self._handle_step_action()
            self.timer.start(self.steps[self.current_step_index].delay)
            
    def skip_tutorial(self):
        """Skip the rest of the tutorial"""
        self._end_tutorial()
        self.tutorial_skipped.emit()
        
    def _end_tutorial(self):
        """Clean up and end the tutorial"""
        if self.overlay:
            self.overlay.hide_animated()
            
    def _handle_step_action(self):
        """Handle any actions required for the current step"""
        current_step = self.steps[self.current_step_index]
        if current_step.action:
            if current_step.action.startswith("activate_tab_"):
                tab_index = int(current_step.action.split("_")[-1])
                self.main_window.tab_widget.setCurrentIndex(tab_index)
                
    def _show_current_step(self):
        """Show the current tutorial step"""
        try:
            if 0 <= self.current_step_index < len(self.steps):
                step = self.steps[self.current_step_index]
                target_rect, show_arrow, arrow_start, arrow_end = self._get_target_rect(step)
                
                # Show the overlay with the appropriate highlighting
                if not self.overlay.isVisible():
                    self.overlay.resize(self.main_window.size())
                    self.overlay.show_animated()
                
                self.overlay.set_highlight(
                    target_rect, 
                    step.message, 
                    self.current_step_index + 1, 
                    len(self.steps),
                    show_arrow,
                    arrow_start,
                    arrow_end
                )
                
                # Emit the step changed signal
                self.tutorial_step_changed.emit(self.current_step_index)
        except Exception as e:
            print(f"Error showing tutorial step: {e}")
            # If there's an error, try to skip to the next step
            if self.current_step_index < len(self.steps) - 1:
                self.current_step_index += 1
                QTimer.singleShot(500, self._show_current_step)
            else:
                self._end_tutorial()
            
    def _get_target_rect(self, step):
        """
        Get the rectangle coordinates of the target widget or UI element
        
        Args:
            step (TutorialStep): The current tutorial step
            
        Returns:
            tuple: (QRect, show_arrow, arrow_start, arrow_end)
        """
        show_arrow = False
        arrow_start = None
        arrow_end = None
        
        # Center of screen for welcome and final steps
        if step.target_type == "center" or not step.target:
            center_x = self.main_window.width() // 2
            center_y = self.main_window.height() // 2
            return QRect(center_x - 100, center_y - 100, 200, 200), show_arrow, arrow_start, arrow_end
            
        # Menu targeting based on attribute name
        elif step.target_type == "menu":
            # Coba dapatkan menu dari atribut main_window
            menu = getattr(self.main_window, step.target, None)
        
        # Menu targeting based on menu text
        elif step.target_type == "menu_text":
            try:
                menu_bar = self.main_window.menu_bar
                menu = None
                for action in menu_bar.actions():
                    if action.text() == step.target:
                        menu = action
                        break
                if menu is None:
                    print(f"Menu with text '{step.target}' not found")
                    # Default to center of screen
                    center_x = self.main_window.width() // 2
                    center_y = self.main_window.height() // 2
                    return QRect(center_x - 100, center_y - 100, 200, 200), show_arrow, arrow_start, arrow_end
            except Exception as e:
                print(f"Error finding menu by text: {e}")
                # Default to center of screen
                center_x = self.main_window.width() // 2
                center_y = self.main_window.height() // 2
                return QRect(center_x - 100, center_y - 100, 200, 200), show_arrow, arrow_start, arrow_end
            
            if menu:
                try:
                    # Dapatkan aksi menu
                    if hasattr(menu, 'menuAction'):
                        action = menu.menuAction()
                    else:
                        action = menu  # Jika menu sudah berupa QAction
                    
                    # Dapatkan geometri menu bar
                    rect = self.main_window.menu_bar.actionGeometry(action)
                    
                    # Perbaiki ukuran highlight untuk menu (pastikan mengambil seluruh menu)
                    rect = QRect(
                        rect.x(), 
                        rect.y(), 
                        rect.width(), 
                        rect.height() + 5  # Tambahkan sedikit ruang ke bawah
                    )
                    
                    # Konversi ke koordinat global dan kemudian lokal
                    global_rect = QRect(
                        self.main_window.menu_bar.mapToGlobal(rect.topLeft()),
                        rect.size()
                    )
                    local_rect = QRect(
                        self.main_window.mapFromGlobal(global_rect.topLeft()),
                        global_rect.size()
                    )
                    
                    # Tambahkan highlight ke seluruh menu bar untuk menu aktif
                    menu_bar_height = self.main_window.menu_bar.height()
                    extended_rect = QRect(
                        local_rect.x() - 5,  # Sedikit lebih lebar di kiri
                        0,                   # Mulai dari atas window
                        local_rect.width() + 10,  # Sedikit lebih lebar di kanan
                        menu_bar_height     # Tinggi seluruh menu bar
                    )
                    
                    return extended_rect, show_arrow, arrow_start, arrow_end
                except Exception as e:
                    print(f"Error targeting menu: {e}")
                    # Fallback to default menu targeting
                    action = menu.menuAction()
                    rect = self.main_window.menu_bar.actionGeometry(action)
                    global_rect = QRect(
                        self.main_window.menu_bar.mapToGlobal(rect.topLeft()),
                        rect.size()
                    )
                    local_rect = QRect(
                        self.main_window.mapFromGlobal(global_rect.topLeft()),
                        global_rect.size()
                    )
                    return local_rect, show_arrow, arrow_start, arrow_end
                
        # Tab targeting
        elif step.target_type == "tab":
            tab_widget = self.main_window.tab_widget
            tab_index = -1
            
            # Find the tab index by object name
            for i in range(tab_widget.count()):
                if tab_widget.widget(i).objectName() == step.target or step.target == f"tab{i+1}":
                    tab_index = i
                    break
                    
            if tab_index >= 0:
                rect = tab_widget.tabBar().tabRect(tab_index)
                global_pos = tab_widget.tabBar().mapToGlobal(rect.topLeft())
                local_pos = self.main_window.mapFromGlobal(global_pos)
                return QRect(local_pos, rect.size()), show_arrow, arrow_start, arrow_end
                
        # Toolbar targeting
        elif step.target_type == "toolbar":
            toolbar = getattr(self.main_window, step.target, None)
            if toolbar:
                rect = toolbar.geometry()
                return rect, show_arrow, arrow_start, arrow_end
                
        # Widget targeting (default)
        else:
            widget = self.main_window.findChild(QWidget, step.target)
            if widget:
                global_pos = widget.mapToGlobal(widget.rect().topLeft())
                local_pos = self.main_window.mapFromGlobal(global_pos)
                return QRect(local_pos, widget.size()), show_arrow, arrow_start, arrow_end
                
        # Default to center if target not found
        center_x = self.main_window.width() // 2
        center_y = self.main_window.height() // 2
        return QRect(center_x - 100, center_y - 100, 200, 200), show_arrow, arrow_start, arrow_end
        
    def resize_overlay(self):
        """Resize the overlay to match the main window size"""
        if self.overlay and self.overlay.isVisible():
            self.overlay.resize(self.main_window.size())
            # Re-show the current step to update positions
            self._show_current_step()
