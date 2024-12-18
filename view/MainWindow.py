from PyQt6 import QtWidgets, QtGui
from model.TabelModel import TableModel
import pandas as pd

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.table = QtWidgets.QTableView()

        data = pd.DataFrame([[""]], columns=["Column1"])

        self.model = TableModel(data)
        self.table.setModel(self.model)

        self.setCentralWidget(self.table)
        screen = QtGui.QGuiApplication.primaryScreen()
        screen_size = screen.availableGeometry()
        self.setGeometry(screen_size)
    
    def setData(self, data):
        self.data = data