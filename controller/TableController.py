class TableController:
    def __init__(self, window, data):
        self.window = window
        self.data = data

    def setData(self, window, data):
        self.window.setData(data)