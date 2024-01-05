from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal

from pathlib import Path

from dc_linedata import LineData, Group


# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_img = Path.cwd() / bundle_dir / "img"


# qt treewidget class extension
class MyTreeWidget(QTreeWidget):
    itemSelectionChanged = pyqtSignal()
    aaa= pyqtSignal()
    

    def __init__(self):
        super().__init__()

        self.setHeaderHidden(True)
        # self.myf=None
        # pyqtSignal(object)

        # self.root_item = QTreeWidgetItem(["Root Item"])
        # self.addTopLevelItem(self.root_item)

    def build_hierarchy(self, root_group=None, parent_group=None, parent_item=None):
        # Clear existing items
        if root_group is not None:
            self.clear()

        if parent_group is None:
            parent_group = root_group

        item = QTreeWidgetItem([parent_group.name, '-1'])
        item.setIcon(0, QIcon(str(path_to_img/'folder.png')))  # Set the icon

        if parent_item is None:
            self.addTopLevelItem(item)
        else:
            parent_item.addChild(item)

        for child in parent_group.children:
            if isinstance(child, Group):
                self.build_hierarchy(parent_group=child, parent_item=item)
            else:
                child_item = QTreeWidgetItem([child.name, str(child.line_id)])
                child_item.setIcon(0, QIcon(str(path_to_img/'paper.png')))  # Set the icon
                item.addChild(child_item)

        self.expandAll()

    # def on_item_selection_changed(self):
        # print("called")
        # pass
        # sel=self.selectedItems()
        # if sel:
        #     print(int(sel[0].data(1,0)))
        #     sl=LineData.getOneData(int(sel[0].data(1,0)))
        #     sl.color=[1,1,0,1]
        #     sl.selected=True
            # LineData.makeBuffer()
        
 
    # def keyPressEvent(self, event):
    #     if event.key()==Qt.Key.Key_Control:
    #         print('ctrl')


    def mouseReleaseEvent(self ,event):
        ctrl_pressed = QApplication.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier
        # print(self.itemAt(event.pos()))
        # print(event.pos())
        item_at_pos = self.itemAt(event.pos())
        if item_at_pos:
            if ctrl_pressed is False:
                self.selectionModel().clearSelection()
                LineData.deselectAll()
                # self.itemSelectionChanged.emit()
                # self.myf.update()
                # item_at_pos.setSelected(True)
                self.itemSelectionChanged.emit()
         
            
            # item_at_pos.setSelected(True)

            id=int(item_at_pos.data(1,0))
            if id>-1:
                # LineData.deselectAll()
                sl=LineData.getOneData(id)
                sl.color=[1,1,0,1]
                sl.selected=True
                self.itemSelectionChanged.emit()

            item_at_pos.setSelected(True)  
            self.itemSelectionChanged.emit()

            # print("Mouse over item:", item_at_pos.text(0))
        else:
            # print("blank")
            self.selectionModel().clearSelection()
            LineData.deselectAll()

            self.itemSelectionChanged.emit()
            # self.myf.update()




# root_group = Group.addRoot('Root')

# for i in range(0,6):
#     obj = Object("Object "+str(i))
#     root_group.add_child(obj)


# # Create a child group
# child_group = Group("Child Group")
# child_group2 = Group("Child Group 2")
# child_group3 = Group("Child Group 3")

# for i in range(0,20):
#     obj = Object("Object "+str(i))
#     child_group2.add_child(obj)

# # Add the child group to the root group
# # root_group.add_child(child_group)
# # root_group.add_child(child_group2)

# child_group2.add_child(child_group3)

# object3 = Object("Object 3")
# # Add an object to the child group
# child_group.add_child(object3)


# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Hierarchy Viewer")
#         self.setGeometry(100, 100, 800, 600)

#         self.central_widget = QWidget(self)
#         self.setCentralWidget(self.central_widget)

#         self.layout = QVBoxLayout(self.central_widget)

#         # Create the tree widget
#         self.tree_widget = MyTreeWidget()
#         self.layout.addWidget(self.tree_widget)

#         # Build the hierarchy in the tree widget
#         self.tree_widget.build_hierarchy(Group.getRoot())

#         # Expand all items
#         self.tree_widget.expandAll()

#         # self.root_group.print_hierarchy()


# if __name__ == "__main__":
#     app = QApplication([])
#     window = MainWindow()
#     window.show()
#     app.exec()
