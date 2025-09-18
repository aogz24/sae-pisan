from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from service.threading.ThreadManager import get_thread_manager

class TaskQueueDialog(QDialog):
    """
    A dialog for displaying and managing the task queue
    
    This dialog shows the currently running task and all queued tasks,
    and allows the user to cancel specific tasks or clear the entire queue.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Task Queue")
        self.resize(400, 300)
        
        # Get the thread manager instance
        self.thread_manager = get_thread_manager()
        
        # Set up the UI
        self.setup_ui()
        
        # Connect signals
        self.thread_manager.queue_updated.connect(self.update_task_list)
        self.thread_manager.task_started.connect(self.update_task_list)
        self.thread_manager.task_finished.connect(self.on_task_finished)
        
        # Update task list immediately
        self.update_task_list()
        
        # Set up timer to periodically update the UI
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_task_list)
        self.update_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        """Set up the dialog UI components"""
        layout = QVBoxLayout(self)
        
        # Current task section
        current_task_layout = QVBoxLayout()
        current_task_label = QLabel("Currently Running:")
        current_task_label.setStyleSheet("font-weight: bold;")
        self.current_task_text = QLabel("None")
        
        current_task_layout.addWidget(current_task_label)
        current_task_layout.addWidget(self.current_task_text)
        
        # Add stop button for current task
        self.stop_current_button = QPushButton("Stop Current Task")
        self.stop_current_button.clicked.connect(self.stop_current_task)
        current_task_layout.addWidget(self.stop_current_button)
        
        layout.addLayout(current_task_layout)
        
        # Queue section
        queue_label = QLabel("Task Queue:")
        queue_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(queue_label)
        
        self.task_list = QListWidget()
        self.task_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.task_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_task)
        button_layout.addWidget(self.remove_button)
        
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_all_tasks)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
    
    @pyqtSlot()
    def update_task_list(self):
        """Update the displayed task list"""
        # Update current task
        running_task = self.thread_manager.get_running_task()
        if running_task:
            self.current_task_text.setText(f"{running_task.name}")
            self.stop_current_button.setEnabled(True)
        else:
            self.current_task_text.setText("None")
            self.stop_current_button.setEnabled(False)
        
        # Update queue
        self.task_list.clear()
        for task in self.thread_manager.get_queued_tasks():
            if not task.is_cancelled:
                item = QListWidgetItem(f"{task.name}")
                item.setData(Qt.ItemDataRole.UserRole, task.name)
                self.task_list.addItem(item)
        
        # Update button states
        self.remove_button.setEnabled(self.task_list.count() > 0)
        self.clear_button.setEnabled(self.task_list.count() > 0)
    
    def stop_current_task(self):
        """Stop the currently running task"""
        if self.thread_manager.is_task_running():
            reply = QMessageBox.question(
                self, 
                "Confirm Stop", 
                "Are you sure you want to stop the current task?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.thread_manager.cancel_task()
                QMessageBox.information(self, "Task Stopped", "The current task has been stopped.")
    
    def remove_selected_task(self):
        """Remove the selected task from the queue"""
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a task to remove.")
            return
        
        task_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, 
            "Confirm Remove", 
            f"Are you sure you want to remove the task '{task_name}' from the queue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.thread_manager.cancel_task(task_name=task_name)
    
    def clear_all_tasks(self):
        """Clear all tasks from the queue"""
        if self.task_list.count() == 0:
            return
            
        reply = QMessageBox.question(
            self, 
            "Confirm Clear", 
            "Are you sure you want to clear all tasks from the queue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.thread_manager.cancel_task(all_tasks=True)
    
    @pyqtSlot(str, bool)
    def on_task_finished(self, task_name, success):
        """Handle task finished signal"""
        # Update the UI
        self.update_task_list()
        
    def closeEvent(self, event):
        """Handle dialog close event"""
        self.update_timer.stop()
        super().closeEvent(event)