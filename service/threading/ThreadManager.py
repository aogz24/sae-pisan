import threading
import queue
import time
from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QWaitCondition

class ModelTask:
    """
    A class representing a modelling task to be executed.
    
    Attributes:
        dialog: The dialog initiating the task
        run_func: The function to run
        name: The name of the task
        args: Arguments for the run function
        kwargs: Keyword arguments for the run function
        on_complete: Function to call when task completes
        on_error: Function to call when task errors
    """
    def __init__(self, dialog, run_func, name, *args, on_complete=None, on_error=None, **kwargs):
        self.dialog = dialog
        self.run_func = run_func
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.on_complete = on_complete
        self.on_error = on_error
        self.is_cancelled = False
        
    def cancel(self):
        """Mark the task as cancelled"""
        self.is_cancelled = True
        
    def __str__(self):
        return f"ModelTask({self.name})"

# Global instance and lock
_thread_manager_instance = None
_thread_manager_lock = threading.Lock()

def get_thread_manager():
    """Get the singleton thread manager instance"""
    global _thread_manager_instance
    if _thread_manager_instance is None:
        with _thread_manager_lock:
            if _thread_manager_instance is None:
                _thread_manager_instance = ThreadManager()
    return _thread_manager_instance

class ThreadManager(QObject):
    """
    Manager for handling modelling threads and task queue.
    
    This class implements a queue system for modelling tasks with only 
    one modelling task running at a time. It provides a main thread for
    the UI and a dedicated thread for running modelling tasks.
    
    Signals:
        task_started: Emitted when a task starts (task_name)
        task_finished: Emitted when a task finishes (task_name, success)
        queue_updated: Emitted when the queue is updated
    """
    # Signals
    task_started = pyqtSignal(str)
    task_finished = pyqtSignal(str, bool)
    queue_updated = pyqtSignal()
    
    def __init__(self):
        """Initialize the thread manager"""
        super().__init__()  # Initialize QObject
        
        self.task_queue = queue.Queue()
        self.running_task = None
        self.active_threads = {}
        self.is_modelling_running = False
        self.stop_requested = False
        self.modelling_thread = None
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        
        # Start the modelling thread
        self._start_modelling_thread()
    
    def _start_modelling_thread(self):
        """Start the modelling thread that processes tasks from the queue"""
        if self.modelling_thread is None or not self.modelling_thread.is_alive():
            self.stop_requested = False
            self.modelling_thread = threading.Thread(target=self._process_modelling_tasks, name="ModellingThread", daemon=True)
            self.modelling_thread.start()
    
    def _process_modelling_tasks(self):
        """Process tasks from the queue one at a time"""
        while not self.stop_requested:
            try:
                # Wait for a task to be available
                task = self.task_queue.get(block=True, timeout=0.5)
                
                if task.is_cancelled:
                    self.task_queue.task_done()
                    self.queue_updated.emit()
                    continue
                
                self.mutex.lock()
                self.running_task = task
                self.is_modelling_running = True
                self.mutex.unlock()
                
                self.task_started.emit(task.name)
                
                # Execute the task
                try:
                    if not task.is_cancelled:
                        result = task.run_func(*task.args, **task.kwargs)
                        if task.on_complete and not task.is_cancelled:
                            task.on_complete(result)
                        self.task_finished.emit(task.name, True)
                except Exception as e:
                    if task.on_error and not task.is_cancelled:
                        task.on_error(e)
                    self.task_finished.emit(task.name, False)
                finally:
                    self.mutex.lock()
                    self.running_task = None
                    self.is_modelling_running = False
                    self.mutex.unlock()
                    self.task_queue.task_done()
                    self.queue_updated.emit()
            
            except queue.Empty:
                # No tasks in the queue, continue waiting
                pass
    
    def add_task(self, task):
        """
        Add a task to the queue
        
        Args:
            task: ModelTask instance to add to the queue
        
        Returns:
            Position in queue (0 = running now)
        """
        position = self.get_queue_size()
        if self.is_modelling_running:
            position += 1
            
        self.task_queue.put(task)
        self.queue_updated.emit()
        
        # Ensure modelling thread is running
        self._start_modelling_thread()
        
        return position
    
    def cancel_task(self, task_name=None, all_tasks=False):
        """
        Cancel a specific task or all tasks in the queue
        
        Args:
            task_name: Name of the task to cancel (if None and all_tasks is False, cancels running task)
            all_tasks: If True, cancels all tasks including the running one
        
        Returns:
            bool: True if any task was cancelled, False otherwise
        """
        cancelled = False
        
        # Handle running task
        self.mutex.lock()
        running_task = self.running_task
        self.mutex.unlock()
        
        if running_task:
            if all_tasks or task_name is None or running_task.name == task_name:
                running_task.cancel()
                if hasattr(running_task.dialog, 'stop_thread'):
                    running_task.dialog.stop_thread.set()
                cancelled = True
        
        # Handle queued tasks
        if all_tasks or task_name is not None:
            # We can't remove items from a queue directly, so we'll mark them as cancelled
            # and they'll be skipped when processed
            self.mutex.lock()
            try:
                queue_items = list(self.task_queue.queue)
                for task in queue_items:
                    if all_tasks or task.name == task_name:
                        task.cancel()
                        cancelled = True
            finally:
                self.mutex.unlock()
        
        if cancelled:
            self.queue_updated.emit()
        
        return cancelled
    
    def get_queue_size(self):
        """Get the current size of the task queue"""
        return self.task_queue.qsize()
    
    def get_queued_tasks(self):
        """Get a list of all tasks in the queue (not including running task)"""
        self.mutex.lock()
        try:
            return list(self.task_queue.queue)
        finally:
            self.mutex.unlock()
    
    def get_running_task(self):
        """Get the currently running task, if any"""
        self.mutex.lock()
        try:
            return self.running_task
        finally:
            self.mutex.unlock()
    
    def is_task_running(self, task_name=None):
        """
        Check if a specific task is running or any task if task_name is None
        
        Args:
            task_name: Name of the task to check
            
        Returns:
            bool: True if the task is running, False otherwise
        """
        self.mutex.lock()
        try:
            if not self.running_task:
                return False
            if task_name is None:
                return True
            return self.running_task.name == task_name
        finally:
            self.mutex.unlock()
    
    def shutdown(self):
        """Shut down the thread manager and stop all tasks"""
        self.stop_requested = True
        self.cancel_task(all_tasks=True)
        
        # Wait for the modelling thread to finish
        if self.modelling_thread and self.modelling_thread.is_alive():
            self.modelling_thread.join(timeout=2.0)