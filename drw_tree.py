from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
class Group:
    rootobj = None

    def __init__(self, name):
        self.name = name
        self.children = []

        # add child to root by default
        if self.rootobj is not None:
            self.rootobj.add_child(self)

    def add_child(self, child):
        if hasattr(child, 'parent') and child.parent is not None:
            child.parent.children.remove(child)

        self.children.append(child)
        child.parent = self

    @classmethod
    def addRoot(cls, name):
        # Create the root group
        if cls.rootobj is None:
            cls.rootobj = cls(name)
        return cls.rootobj

    @classmethod
    def getRoot(cls):
        return cls.rootobj

    def print_hierarchy(self, indent=0):
        print("  " * indent + self.name)
        for child in self.children:
            if isinstance(child, Group):
                child.print_hierarchy(indent + 1)
            else:
                print("  " * (indent + 1) + child.name)


class Object:
    def __init__(self, name):
        self.name = name
        self.parent = None


class MyTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()

        self.setHeaderHidden(True)

        # self.root_item = QTreeWidgetItem(["Root Item"])
        # self.addTopLevelItem(self.root_item)

    def build_hierarchy(self, root_group=None, parent_group=None, parent_item=None):
        # Clear existing items
        if root_group is not None:
            self.clear()

        if parent_group is None:
            parent_group = root_group

        item = QTreeWidgetItem([parent_group.name, 'idval'])
        item.setIcon(0, QIcon('./img/folder.png'))  # Set the icon

        if parent_item is None:
            self.addTopLevelItem(item)
        else:
            parent_item.addChild(item)

        for child in parent_group.children:
            if isinstance(child, Group):
                self.build_hierarchy(parent_group=child, parent_item=item)
            else:
                child_item = QTreeWidgetItem([child.name, str(child.line_id)])
                child_item.setIcon(0, QIcon('./img/paper.png'))  # Set the icon
                item.addChild(child_item)

        self.expandAll()

    def on_item_selection_changed(self):
       
        sel=self.selectedItems()
        if sel:
            print(sel[0].data(1,0))

    # def on_item_clicked(self, item, column):
    #     if not self.selectedItems():
    #         print("No item selected (deselected)")

    # def mouseMoveEvent(self, event):
    #     # Check if the mouse is over a QTreeWidgetItem
    #     print(event.pos())
    #     item_at_pos = self.itemAt(event.pos())
    #     if item_at_pos:
    #         print("Mouse over item:", item_at_pos.text(0))

    def mouseReleaseEvent(self ,event):
        # print(event.pos())
        item_at_pos = self.itemAt(event.pos())
        if item_at_pos:
            print("Mouse over item:", item_at_pos.text(0))
        else:
            print("blank")
            self.selectionModel().clearSelection()

        # print(self.currentItem().sizeHint(0))
        # if event.button() == Qt.MouseButton.LeftButton and not self.rect().contains(event.pos()):
   
        #     self.selectionModel().clearSelection()


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
