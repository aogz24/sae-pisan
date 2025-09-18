import sys
import traceback
sys.path.insert(0, '.')
print("Path set up")

try:
    print("Importing QObject...")
    from PyQt6.QtCore import QObject
    print("QObject imported successfully")
    
    print("Creating simple QObject...")
    obj = QObject()
    print("QObject created successfully")
    
    print("Importing ThreadManager...")
    from service.threading.ThreadManager import get_thread_manager
    print("ThreadManager imported successfully")
    
    print("Getting ThreadManager instance...")
    tm = get_thread_manager()
    print("Successfully got ThreadManager instance")
    
    print("ThreadManager instance ID:", id(tm))
    
    print("Getting another ThreadManager instance...")
    tm2 = get_thread_manager()
    print("Successfully got second ThreadManager instance")
    
    print("Second ThreadManager instance ID:", id(tm2))
    print("Same instance:", tm is tm2)
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    traceback.print_exc()