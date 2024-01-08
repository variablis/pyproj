from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QFileDialog, QSplitter, QLineEdit, QLabel, QComboBox
from PyQt6.QtGui import QSurfaceFormat, QRegularExpressionValidator, QIcon, QAction
from PyQt6.QtCore import Qt, QRegularExpression

import json
from pathlib import Path

from dw_mywidget import MyWidget
from dw_tree import MyTreeWidget
from dc_linedata import LineData, Group, SceneData
from dc_text import TextData


# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_img = Path.cwd() / bundle_dir / "img"


class MyMainWindow(QMainWindow):
    '''
    main window
    '''
    def __init__(self):
        super().__init__()

        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setSamples(4) # multi-sampling
        
        self.mywidget = MyWidget()
        self.mywidget.setMouseTracking(True)
        self.mywidget.setFormat(fmt)
        self.mywidget.setGeometry(0, 0, 300, 300)

        self.setGeometry(100, 100, 512, 512)
        self.setMouseTracking(True)

        self.tree = MyTreeWidget()

        splitter = QSplitter()
        splitter.addWidget(self.tree)
        splitter.addWidget(self.mywidget)

        self.setCentralWidget(splitter)
        # Set a minimum size for the second widget
        self.tree.setMinimumWidth(100)
        self.tree.setMaximumWidth(180)

        self.root_group = Group('Root')
        LineData.root = self.root_group
        LineData.treewidget = self.tree
        self.tree.build_hierarchy(self.root_group)
        self.tree.itemSelectionChanged.connect(self.mywidget.update)

        toolbar = QToolBar()
        toolbar2 = QToolBar()

        tbtn_new_file = QAction(QIcon(str(path_to_img/"paper.png")), "New", self)
        tbtn_new_file.triggered.connect(self.new_file)
        toolbar.addAction(tbtn_new_file)

        tbtn_open_file = QAction(QIcon(str(path_to_img/"folder.png")), "Open", self)
        tbtn_open_file.triggered.connect(self.open_file)
        toolbar.addAction(tbtn_open_file)

        tbtn_save_file = QAction(QIcon(str(path_to_img/"diskete.png")), "Save", self)
        tbtn_save_file.triggered.connect(self.save_file)
        toolbar.addAction(tbtn_save_file)

        create_line = QAction(QIcon(str(path_to_img/"line.png")), "Create line", self)
        create_line.setCheckable(True)
        create_line.toggled.connect(self.mywidget.create_line_tool)
        toolbar2.addAction(create_line)

        # TODO:
        # toggle_dimensions = QAction("Toggle dimensions", self)
        # toggle_dimensions.setCheckable(True)
        # toggle_dimensions.triggered.connect()
        # toolbar2.addAction(toggle_dimensions)

        # allow only integer input 1-25
        rgx = QRegularExpression("[1-9]|1[0-9]|2[0-5]")

        label_grid = QLabel("Grid: ", self)
        self.input_gridsize = QLineEdit(self)
        self.input_gridsize.setMaximumWidth(28)
        self.rx = QRegularExpressionValidator(rgx, self)
        self.input_gridsize.setValidator(self.rx)
        self.input_gridsize.setText("1")
        self.input_gridsize.textChanged[str].connect(self.grid_changed)

        toolbar2.addWidget(label_grid)
        toolbar2.addWidget(self.input_gridsize)

        label_units = QLabel("Scene units: ", self)
        self.input_units = QComboBox(self)
        self.input_units.addItems(["1", "10", "100", "1000"])
        self.input_units.setCurrentIndex(1)
        self.input_units.currentIndexChanged.connect(self.unit_changed)

        toolbar2.addWidget(label_units)
        toolbar2.addWidget(self.input_units)

        self.addToolBar(toolbar)
        self.addToolBar(toolbar2)
        

    def grid_changed(self, text):
        if text:
            self.mywidget.scene.set_grid(int(text))
            self.mywidget.update()


    def unit_changed(self):
        selected_value = int(self.input_units.currentText())
        SceneData.units = selected_value
        TextData.rebuild_all(True)
        self.mywidget.update()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            ids = LineData.get_selected_ids()
            TextData.delete_selected(ids)
            LineData.delete_selected()

            self.mywidget.scene.clear_buffers()
            self.mywidget.update()

        else:
            super().keyPressEvent(event)


    def reset_all(self):
        LineData.g_index = 0
        LineData.lines=[]
        TextData.texts=[]

        self.mywidget.scene.clear_buffers()
        self.mywidget.update()


    def new_file(self):
        self.reset_all()

        self.root_group = Group('Root')
        LineData.root = self.root_group
        self.tree.build_hierarchy(self.root_group)


    def open_file(self):
        home_dir = str(Path.cwd())
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir)

        if fname[0]:
            f = open(fname[0], 'r')
            data = json.load(f)

            self.reset_all()

            self.root_group = Group.json_to_hierarchy(data)
            LineData.root = self.root_group
            self.tree.build_hierarchy(self.root_group)

            TextData.rebuild_all()
            

    def save_file(self):
        home_dir = str(Path.cwd())
        fname = QFileDialog.getSaveFileName(self, 'Save file', home_dir, '*.drw')

        # print(self.root_group.hierarchy_to_json())
        
        if fname[0]:
            f = open(fname[0], 'w')
            json.dump(self.root_group.hierarchy_to_json(), f, indent=2)



if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("fusion")
    window = MyMainWindow()
    window.show()
    app.exec()
