from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QFileDialog, QSplitter, QLineEdit, QLabel, QComboBox
from PyQt6.QtGui import QSurfaceFormat, QRegularExpressionValidator, QIcon, QAction
from PyQt6.QtCore import QRegularExpression

import json

from dw_mywidget import *
from dw_tree import MyTreeWidget
from dc_linedata import Group, SceneData


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setSamples(4)  # multi-sampling
        
        self.mywidget = MyWidget()
        self.mywidget.setMouseTracking(True)
        self.mywidget.setFormat(fmt)
        self.mywidget.setGeometry(0, 0, 300, 300)


        self.setGeometry(100, 100, 512, 512)
        self.setMouseTracking(True)

        # Create the layout for the central widget
        self.tree = MyTreeWidget()

        splitter = QSplitter()
        splitter.addWidget(self.tree)
        splitter.addWidget(self.mywidget)

        self.setCentralWidget(splitter)
        # Set a minimum size for the second widget
        self.tree.setMinimumWidth(100)
        self.tree.setMaximumWidth(180)

        root_group = Group.addRoot('Root')
        LineData.root = root_group
        LineData.treewidget = self.tree
        self.tree.build_hierarchy(Group.getRoot())
        self.tree.itemSelectionChanged.connect(self.mywidget.update)


        toolbar = QToolBar()
        toolbar2 = QToolBar()

        tbtn_new_file = QAction(QIcon(str(path_to_img/"paper.png")), "New", self)
        tbtn_new_file.triggered.connect(self.newFile)
        toolbar.addAction(tbtn_new_file)

        tbtn_open_file = QAction(QIcon(str(path_to_img/"folder.png")), "Open", self)
        tbtn_open_file.triggered.connect(self.openFile)
        toolbar.addAction(tbtn_open_file)

        tbtn_save_file = QAction(QIcon(str(path_to_img/"diskete.png")), "Save", self)
        tbtn_save_file.triggered.connect(self.saveFile)
        toolbar.addAction(tbtn_save_file)

        create_line = QAction("Create Line", self)
        create_line.setCheckable(True)
        create_line.toggled.connect(self.mywidget.createlinetool)
        toolbar2.addAction(create_line)


        # toggle_dimensions = QAction("Toggle dimensions", self)
        # toggle_dimensions.setCheckable(True)
        # toggle_dimensions.triggered.connect()
        # toolbar2.addAction(toggle_dimensions)

        # Create a QIntValidator to allow only integer input
        rgx = QRegularExpression("^[1-9][0-9]?$|^100$")
 

        label_grid = QLabel("Grid: ", self)
        self.input_gridsize = QLineEdit(self)
        self.input_gridsize.setMaximumWidth(28)
        self.rx = QRegularExpressionValidator(rgx, self)
        self.input_gridsize.setValidator(self.rx)
        self.input_gridsize.setText("1")
        self.input_gridsize.textChanged[str].connect(self.onChanged)

        toolbar2.addWidget(label_grid)
        toolbar2.addWidget(self.input_gridsize)


        label_units = QLabel("Scene units: ", self)
        self.input_units = QComboBox(self)
        self.input_units.addItems(["1", "10", "100", "1000"])
        self.input_units.setCurrentIndex(1)
        self.input_units.currentIndexChanged.connect(self.onUnitChaged)


        toolbar2.addWidget(label_units)
        toolbar2.addWidget(self.input_units)


        self.addToolBar(toolbar)
        self.addToolBar(toolbar2)
        

    def onChanged(self, text):
        if text:
            self.mywidget.scene.setGrid(int(text))
            self.mywidget.update()

    def onUnitChaged(self):
        selected_value = int(self.input_units.currentText())
        SceneData.units = selected_value
        TextData.rebuildAll(clear=True)
        # self.mywidget.scene.bufcl()
        self.mywidget.update()
        
        

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            # print("Delete key pressed!")

            selids=LineData.getSelectedIds()
            TextData.deleteSelected(selids)
            LineData.deleteSelected()
            
            self.mywidget.scene.bufcl()
            self.mywidget.update()
            # self.mywidget.render()
        else:
            super().keyPressEvent(event)


    def resetAll(self):
        LineData.idx=0
        LineData.lines=[]
        TextData.texts=[]
        self.mywidget.scene.bufcl()

        LineData.root.remove_root_children()
        LineData.treewidget.build_hierarchy(Group.getRoot())

        self.update()


    def newFile(self):
        self.resetAll()
        # print('new file...')


    def openFile(self):
        home_dir = str(Path.cwd())
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir)

        if fname[0]:
            f = open(fname[0], 'r')
            # data = f.read()
            data = json.load(f)

            self.resetAll()
            r=Group.createGroupFromJson(data)
            LineData.root=r
            # LineData.printData()
            TextData.rebuildAll()
            LineData.treewidget.build_hierarchy(r)


    def saveFile(self):
        home_dir = str(Path.cwd())
        fname = QFileDialog.getSaveFileName(self, 'Save file', home_dir, '*.drw')
        # print(Group.hierarchyToJson())
        
        if fname[0]:
            f = open(fname[0], 'w')
            json.dump(Group.hierarchyToJson(), f, indent=2)
            # print('saved file...')



if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("fusion")
    window = MyMainWindow()
    window.show()
    app.exec()
