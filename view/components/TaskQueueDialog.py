from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QSizePolicy, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QIcon
from service.threading.ThreadManager import get_thread_manager

class TaskQueueDialog(QDialog):
    """
    A dialog for displaying and managing the task queue
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Task Queue")
        self.resize(420, 340)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border: 1px solid #BFBEBE;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel {
                color: #5A5759;
                padding: 5px 0;
            }
            QPushButton {
                background-color: #95C843;
                color: #FFFFFF;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #BFBEBE;
                color: #EAEAEA;
            }
            QPushButton:hover {
                background-color: #7AB432;
            }
            QPushButton:pressed {
                background-color: #5E8E2B;
            }
            QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #EAEAEA;
                color: #5A5759;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #A1D9F3;
                color: #FFFFFF;
            }
            QGroupBox {
                border: 1px solid #EAEAEA;
                border-radius: 8px;
                margin-top: 10px;
                padding: 8px;
                font-weight: bold;
                background-color: #F8F8F8;
                color: #5A5759;
            }
        """)
        self.thread_manager = get_thread_manager()
        self.setup_ui()
        self.thread_manager.queue_updated.connect(self.update_task_list)
        self.thread_manager.task_started.connect(self.update_task_list)
        self.thread_manager.task_finished.connect(self.on_task_finished)
        self.update_task_list()
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_task_list)
        self.update_timer.start(1000)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Current task section
        current_group = QGroupBox("Currently Running")
        current_layout = QVBoxLayout()
        self.current_task_text = QLabel("None")
        self.current_task_text.setStyleSheet("font-weight: bold; color: #2BA3E2;")
        current_layout.addWidget(self.current_task_text)

        self.stop_current_button = QPushButton(QIcon.fromTheme("media-playback-stop"), "Stop Current Task")
        self.stop_current_button.clicked.connect(self.stop_current_task)
        current_layout.addWidget(self.stop_current_button)
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        # Queue section
        queue_group = QGroupBox("Task Queue")
        queue_layout = QVBoxLayout()
        self.task_list = QListWidget()
        self.task_list.setAlternatingRowColors(True)
        self.task_list.setStyleSheet("alternate-background-color: #EAEAEA;")
        self.task_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        queue_layout.addWidget(self.task_list)
        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.remove_button = QPushButton(QIcon.fromTheme("edit-delete"), "Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_task)
        button_layout.addWidget(self.remove_button)

        self.clear_button = QPushButton(QIcon.fromTheme("edit-clear"), "Clear All")
        self.clear_button.clicked.connect(self.clear_all_tasks)
        button_layout.addWidget(self.clear_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Close button
        close_button = QPushButton(QIcon.fromTheme("window-close"), "Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

    @pyqtSlot()
    def update_task_list(self):
        running_task = self.thread_manager.get_running_task()
        if running_task:
            self.current_task_text.setText(f"{running_task.name}")
            self.stop_current_button.setEnabled(True)
        else:
            self.current_task_text.setText("None")
            self.stop_current_button.setEnabled(False)

        self.task_list.clear()
        for task in self.thread_manager.get_queued_tasks():
            if not task.is_cancelled:
                item = QListWidgetItem(f"{task.name}")
                item.setData(Qt.ItemDataRole.UserRole, task.name)
                self.task_list.addItem(item)

        self.remove_button.setEnabled(self.task_list.count() > 0)
        self.clear_button.setEnabled(self.task_list.count() > 0)

    def stop_current_task(self):
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
        self.update_task_list()

    def closeEvent(self, event):
        self.update_timer.stop()
        super().closeEvent(event)