from PyQt6.QtCore import QMimeData
from PyQt6.QtWidgets import QListView, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDrag

class DragDropListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if self.parent and hasattr(self.parent, "handle_drop"):
            items = []
            if event.mimeData().hasUrls():
                for url in event.mimeData().urls():
                    items.append(url.toLocalFile())
            if event.mimeData().hasText():
                items = event.mimeData().text().split('\n')
            self.parent.handle_drop(self, [i for i in items if i])
            event.accept()
        else:
            super().dropEvent(event)

    def startDrag(self, supportedActions):
        selected = self.selectedIndexes()
        if not selected:
            return
        data = '\n'.join([self.model().data(i) for i in selected])
        mime = QMimeData()
        mime.setText(data)
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.MoveAction)