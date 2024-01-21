from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal

from pathlib import Path

from dc_linedata import LineData, Group


# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_img = Path.cwd() / bundle_dir / "img"


class MyTreeWidget(QTreeWidget):
    '''
    qt treewidget class extension
    '''
    itemSelectionChanged = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)


    def build_hierarchy(self, root_group=None, parent_group=None, parent_item=None):
        '''
        build tree hierarchy from Group items
        '''

        # Clear existing items
        if root_group != None:
            self.clear()

        if parent_group == None:
            parent_group = root_group

        item = QTreeWidgetItem([parent_group.name, '-1'])
        item.setIcon(0, QIcon(str(path_to_img/'folder.png')))

        if parent_item == None:
            self.addTopLevelItem(item)
        else:
            parent_item.addChild(item)

        for child in parent_group.children:
            if isinstance(child, Group):
                self.build_hierarchy(parent_group=child, parent_item=item)
            else:
                child_item = QTreeWidgetItem([child.name, str(child.line_id)])
                child_item.setIcon(0, QIcon(str(path_to_img/'paper.png')))
                item.addChild(child_item)

        self.expandAll()


    def mouseReleaseEvent(self, event):

        ctrl_pressed = QApplication.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier
        item_at_pos = self.itemAt(event.pos())

        if item_at_pos:
            if ctrl_pressed == False:
                self.selectionModel().clearSelection()
                LineData.deselect_all()
                self.itemSelectionChanged.emit()

            id = int(item_at_pos.data(1,0))
            if id > -1:
                line = LineData.get_line_data(id)
                line.color = [1,1,0,1]
                line.selected = True
                self.itemSelectionChanged.emit()

            item_at_pos.setSelected(True)  
            self.itemSelectionChanged.emit()

        else:
            self.selectionModel().clearSelection()
            LineData.deselect_all()
            self.itemSelectionChanged.emit()
