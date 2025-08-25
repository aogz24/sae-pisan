from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QPen, QFont, QPixmap

class TutorialOverlay(QWidget):
    """
    A customizable overlay widget for highlighting UI elements during a tutorial.
    
    This widget creates a semi-transparent overlay with a cutout around the target element
    to highlight it to the user. It also displays instructional text and navigation buttons.
    
    Attributes:
        next_clicked (pyqtSignal): Signal emitted when the next button is clicked
        prev_clicked (pyqtSignal): Signal emitted when the previous button is clicked
        skip_clicked (pyqtSignal): Signal emitted when the skip button is clicked
    """
    next_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()
    skip_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up widget properties
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        
        # Initialize properties
        self.highlight_rect = QRect()
        self.message = ""
        self.arrow_start = QPoint()
        self.arrow_end = QPoint()
        self.show_arrow = False
        self.highlight_margin = 15  # Increased margin
        self.corner_radius = 10  # Increased corner radius
        self.current_step = 0
        self.total_steps = 0
        
        # Set up layout
        self.init_ui()
        
        # Set up animations
        self.highlight_animation = QPropertyAnimation(self, b"geometry")
        self.highlight_animation.setDuration(500)
        self.highlight_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Set up opacity effect and animation for smooth appearance
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(400)
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(0.95)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def init_ui(self):
        """Initialize the user interface components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Message container
        self.message_container = QWidget(self)
        self.message_container.setObjectName("messageContainer")
        self.message_container.setStyleSheet("""
            QWidget#messageContainer {
                background-color: #2196F3;
                border-radius: 10px;
                border: 1px solid #1976D2;
            }
        """)
        self.message_container.setMinimumWidth(500)  # Increased width
        
        message_layout = QVBoxLayout(self.message_container)
        message_layout.setContentsMargins(16, 16, 16, 16)
        message_layout.setSpacing(12)
        
        # Message label
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.message_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: normal;
            margin: 0px;
            padding: 0px;
            line-height: 150%;
        """)
        self.message_label.setMinimumWidth(450)
        self.message_label.setMinimumHeight(80)
        message_layout.addWidget(self.message_label)
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(12)
        
        # Skip button
        self.skip_button = QPushButton("Skip Tutorial")
        self.skip_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 1px solid white;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                min-width: 100px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.skip_button.clicked.connect(self.skip_clicked)
        button_layout.addWidget(self.skip_button)
        
        # Spacer
        button_layout.addStretch()
        
        # Step indicator
        self.step_label = QLabel()
        self.step_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            font-weight: bold;
            margin-right: 10px;
        """)
        button_layout.addWidget(self.step_label)
        
        # Previous button
        self.prev_button = QPushButton("Previous")
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                min-width: 100px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        self.prev_button.clicked.connect(self.prev_clicked)
        button_layout.addWidget(self.prev_button)
        
        # Next button
        self.next_button = QPushButton("Next")
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                min-width: 100px;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #43A047;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        self.next_button.clicked.connect(self.next_clicked)
        button_layout.addWidget(self.next_button)
        
        message_layout.addLayout(button_layout)
        
        # Add message container to main layout
        main_layout.addStretch()
        main_layout.addWidget(self.message_container)
        self.message_container.setVisible(False)
        
    def set_highlight(self, rect, message, step=0, total=0, show_arrow=False, arrow_start=None, arrow_end=None):
        """
        Set the highlight area and related properties
        
        Args:
            rect (QRect): Rectangle area to highlight
            message (str): Instruction message to display
            step (int): Current step in the tutorial sequence
            total (int): Total number of steps in the tutorial
            show_arrow (bool): Whether to show a guiding arrow
            arrow_start (QPoint): Starting point of the arrow
            arrow_end (QPoint): Ending point of the arrow
        """
        # Expand the highlight rectangle by the margin
        expanded_rect = QRect(
            rect.x() - self.highlight_margin,
            rect.y() - self.highlight_margin,
            rect.width() + (self.highlight_margin * 2),
            rect.height() + (self.highlight_margin * 2)
        )
        
        self.highlight_rect = expanded_rect
        self.message = message
        self.current_step = step
        self.total_steps = total
        self.show_arrow = show_arrow
        
        if arrow_start and arrow_end:
            self.arrow_start = arrow_start
            self.arrow_end = arrow_end
        
        # Update message label and step indicator
        # Format message with HTML for better display
        formatted_message = f"<div style='font-size:15px; line-height:150%; padding:5px; font-family:Arial,sans-serif; color:white;'>{message}</div>"
        self.message_label.setText(formatted_message)
        
        # Apply word wrapping and ensure proper text formatting
        self.message_label.adjustSize()
        
        # Ensure minimum size for message container
        self.message_container.setMinimumWidth(550)
        self.message_label.setMinimumHeight(100)
        
        if total > 0:
            self.step_label.setText(f"Step {step} of {total}")
            self.step_label.setVisible(True)
        else:
            self.step_label.setVisible(False)
        
        # Show/hide previous button based on current step
        self.prev_button.setVisible(step > 1)
        
        # Update next button text for last step
        if step == total:
            self.next_button.setText("Finish")
        else:
            self.next_button.setText("Next")
            
        # Position the message container based on the highlight rectangle
        self.position_message_container()
        
        # Make the message container visible
        self.message_container.setVisible(True)
        
        # Update the widget
        self.update()
        
    def position_message_container(self):
        """Position the message container relative to the highlighted area"""
        # Get parent size
        parent_size = self.parentWidget().size()
        
        # Force the message container to calculate its correct size
        self.message_container.adjustSize()
        
        # Get message container size (with a little extra margin for safety)
        message_width = max(550, self.message_container.sizeHint().width() + 30)
        message_height = self.message_container.sizeHint().height() + 30
        
        # Default position (below the highlight area)
        x = self.highlight_rect.x() + (self.highlight_rect.width() - message_width) // 2
        y = self.highlight_rect.y() + self.highlight_rect.height() + 30
        
        # Ensure the message is fully visible
        if x < 30:
            x = 30
        if x + message_width > parent_size.width() - 30:
            x = parent_size.width() - message_width - 30
            
        # If message would be outside the bottom, position it above the highlight area
        if y + message_height > parent_size.height() - 30:
            y = self.highlight_rect.y() - message_height - 30
            if y < 30:
                # If still not fitting, position to the right or left of the highlight area
                if self.highlight_rect.right() + message_width + 30 < parent_size.width():
                    x = self.highlight_rect.right() + 30
                    y = max(30, self.highlight_rect.y())
                else:
                    x = max(30, self.highlight_rect.x() - message_width - 30)
                    y = max(30, self.highlight_rect.y())
        
        # Move the message container
        self.message_container.setFixedWidth(message_width)
        self.message_container.move(x, y)
        
        # Apply size for better text display
        self.message_label.setMinimumHeight(70)
        self.message_label.update()
        
    def show_animated(self):
        """Show the overlay with a smooth animation"""
        # Ensure we're visible first
        self.show()
        
        # Start opacity animation
        self.opacity_animation.setDirection(QPropertyAnimation.Direction.Forward)
        self.opacity_animation.start()
        
    def hide_animated(self):
        """Hide the overlay with a smooth animation"""
        # Start opacity animation in reverse
        self.opacity_animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.opacity_animation.finished.connect(self._hide_complete)
        self.opacity_animation.start()
        
    def _hide_complete(self):
        """Complete the hide operation when animation finishes"""
        if self.opacity_effect.opacity() == 0:
            self.hide()
            # Disconnect to prevent multiple connections
            try:
                self.opacity_animation.finished.disconnect(self._hide_complete)
            except:
                pass
        
    def paintEvent(self, event):
        """Custom paint event to render the overlay with a cutout for the highlighted area"""
        if not self.isVisible():
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create a path for the entire overlay
        overlay_path = QPainterPath()
        rect = self.rect()
        overlay_path.addRect(float(rect.x()), float(rect.y()), float(rect.width()), float(rect.height()))
        
        # Create a path for the cutout
        cutout_path = QPainterPath()
        cutout_path.addRoundedRect(
            float(self.highlight_rect.x()), 
            float(self.highlight_rect.y()), 
            float(self.highlight_rect.width()), 
            float(self.highlight_rect.height()), 
            float(self.corner_radius), 
            float(self.corner_radius)
        )
        
        # Subtract the cutout from the overlay
        final_path = overlay_path.subtracted(cutout_path)
        
        # Draw the overlay with semi-transparency
        overlay_color = QColor(0, 0, 0, 140)  # Slightly darker overlay
        painter.fillPath(final_path, overlay_color)
        
        # Check if highlighting is near the top (likely a menu)
        is_menu = self.highlight_rect.y() < 50  # Assume it's a menu if near the top
        
        if is_menu:
            # For menus, use a more pronounced highlight with less rounded corners
            menu_glow_pen = QPen(QColor(255, 255, 255, 200), 3)
            painter.setPen(menu_glow_pen)
            
            # Draw outer glow
            painter.drawRect(
                self.highlight_rect.x() - 1, 
                self.highlight_rect.y() - 1,
                self.highlight_rect.width() + 2, 
                self.highlight_rect.height() + 2
            )
            
            # Draw inner highlight with different color
            inner_highlight = QPen(QColor(46, 144, 255, 255), 3)  # Bright blue, fully opaque
            painter.setPen(inner_highlight)
            painter.drawRect(self.highlight_rect)
            
            # Add a semi-transparent fill for the menu item to make it more visible
            painter.fillRect(self.highlight_rect, QColor(46, 144, 255, 40))
        else:
            # Standard highlight for non-menu items
            glow_pen = QPen(QColor(46, 144, 255, 230), 3)  # Thicker, more visible border
            painter.setPen(glow_pen)
            painter.drawRoundedRect(self.highlight_rect, self.corner_radius, self.corner_radius)
        
        # Draw an arrow if requested
        if self.show_arrow and self.arrow_start and self.arrow_end:
            try:
                arrow_pen = QPen(QColor(255, 255, 255, 200), 2)
                painter.setPen(arrow_pen)
                painter.drawLine(self.arrow_start, self.arrow_end)
                
                # Calculate arrow head
                line_length = ((self.arrow_end.x() - self.arrow_start.x()) ** 2 + 
                              (self.arrow_end.y() - self.arrow_start.y()) ** 2) ** 0.5
                
                if line_length > 0:
                    arrow_head_length = 10
                    
                    dx = (self.arrow_end.x() - self.arrow_start.x()) / line_length
                    dy = (self.arrow_end.y() - self.arrow_start.y()) / line_length
                    
                    # Arrow head points
                    arrow_head1 = QPoint(
                        int(self.arrow_end.x() - arrow_head_length * (dx + dy/2)),
                        int(self.arrow_end.y() - arrow_head_length * (dy - dx/2))
                    )
                    
                    arrow_head2 = QPoint(
                        int(self.arrow_end.x() - arrow_head_length * (dx - dy/2)),
                        int(self.arrow_end.y() - arrow_head_length * (dy + dx/2))
                    )
                    
                    # Draw arrow head
                    painter_path = QPainterPath()
                    painter_path.moveTo(self.arrow_end)
                    painter_path.lineTo(arrow_head1)
                    painter_path.lineTo(arrow_head2)
                    painter_path.lineTo(self.arrow_end)
                    
                    painter.fillPath(painter_path, QColor(255, 255, 255, 200))
            except Exception as e:
                print(f"Error drawing arrow: {e}")
