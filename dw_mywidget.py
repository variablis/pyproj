import json
from pathlib import Path

from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtWidgets import QMainWindow, QToolBar, QFileDialog, QSplitter
from PyQt6.QtGui import QAction, QCursor, QIcon
from PyQt6.QtCore import Qt, QTimer

from dw_qtmoderngl import ModernGLWidget
from dc_renderer import HelloWorld2D, PanTool

from dc_point import Point
from dw_tree import MyTreeWidget
from dc_linedata import LineData, Group
from dc_text import TextData
from df_math import *

from dc_linesegment import LineSegment, linedrag, linestopdrag, check_dr_point, checkclickedpoint, checkpoint

from pathlib import Path


bundle_dir = Path(__file__).parent
path_to_img = Path.cwd() / bundle_dir / "img"


pan_tool = PanTool()
lseg = LineSegment()

uds=None


# convert mouse screen pixel coordinates to normalized coordinates -1.0 to 1.0
def normalized_coordinates(mouse_pt, window_size, zoom_factor):
    screen_width = window_size[0] / 512 / zoom_factor
    screen_height = window_size[1] / 512 / zoom_factor
    normalized_x = mouse_pt.x * 2 - 1 * screen_width + pan_tool.value[0]
    normalized_y = -mouse_pt.y * 2 + 1 * screen_height + pan_tool.value[1]

    return normalized_x, normalized_y


class MyWidget(ModernGLWidget):
    def __init__(self):
        super(MyWidget, self).__init__()

        self.scene = None
        self.zoomy = 0
        self.zfakt  =1

        self.createlineactive=False
        self.clickcount=0
        self.user_drag_start=None
        self.startDragDistance=0.001

    def init(self):
        # self.resize(512, 512) shis ir qt mainwindow resizers
        self.ctx.viewport = (0, 0, 512, 512)
        self.scene = HelloWorld2D(self.ctx)


    def render(self):
        self.ctx.viewport = (0, 0, self.size().width(), self.size().height())
        self.screen.use()
        self.scene.clear()

        # self.scene.textgen(str(lseg.distance)+'...'+str(lseg.degrees), lseg.startpoint)
        
        self.scene.updateMvp(self.zfakt)

        self.scene.textrender(TextData.makeBuffer())
        self.scene.linerender(LineData.makeBuffer())
        # self.scene.circl(np.array(livecircles))
        

    def mycoord(self):
        # origin ir main windowa kreisais augsejais sturis 0,0
        # pozicija tiek nolasita pa visu ekranu!!
        local_pos = self.mapFromGlobal(QCursor.pos())
 
        mousepos = Point(local_pos.x()/ 512/self.zfakt, 
                         local_pos.y()/ 512/self.zfakt)
        return mousepos
    
    def createlinetool(self, checked):
        self.createlineactive = checked
        self.clickcount=0
        lseg.tool_active(checked)


    # def resizeEvent(self, event):
        # print("resize")
        # if self.scene:
            # self.scene.updateMvp(self.zfakt)

        
    def wheelEvent(self, event):
        self.zoomy +=event.angleDelta().y()/120
        self.zfakt=pow(1.4, self.zoomy)
        self.scene.zom(self.zfakt)

        # self.scene.updateMvp(self.zfakt)

        self.update()
        self.render()
        

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            pan_tool.start_drag(self.mycoord())
            self.scene.pan(pan_tool.value)
        
        if event.button() == Qt.MouseButton.LeftButton:
            # self.scene.chcol( random.uniform(1, 1))



            if self.createlineactive:
                lseg.create_points(self.mycoord(), self.clickcount, self.size(), pan_tool.value, self.zfakt)
                self.clickcount+=1
                lseg.point_add(self.clickcount)
            else:
                checkclickedpoint( *normalized_coordinates(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt) )

                # stulbs workarounds lai izslegtu selekcibju bez peles  kustinasanas
                checkpoint( *normalized_coordinates(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt) )
                # Store the initial mouse position for drag calculation
                global uds
                self.user_drag_start = self.mycoord()
                uds = self.user_drag_start
       
        self.update()

    def mouseMoveEvent(self, event):
        pan_tool.dragging(self.mycoord())
        self.scene.pan(pan_tool.value)

        

        if self.user_drag_start:
            # Check for ongoing drag operation
            drag_distance = points_to_distance(self.mycoord(), self.user_drag_start)
            # print(drag_distance)
            if drag_distance > self.startDragDistance:
                # Drag has started
                print("Drag Started")
                # Reset the drag start position
                check_dr_point( *normalized_coordinates(self.user_drag_start, (self.size().width(), self.size().height()), self.zfakt) )
                global uds
                self.user_drag_start = None
                uds = self.user_drag_start 

        if self.createlineactive:
            

            lseg.update_points(self.mycoord(), self.clickcount, self.size(), pan_tool.value, self.zfakt)
        else:
            checkpoint( *normalized_coordinates(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt) )
            linedrag( *normalized_coordinates(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt) )
            

        self.update()
        self.render()

    def mouseReleaseEvent(self, event):
        pan_tool.stop_drag(self.mycoord())
        self.scene.pan(pan_tool.value)

        linestopdrag( *normalized_coordinates(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt) )

        global uds
        self.user_drag_start = None
        uds = self.user_drag_start 

        self.update()


    def resetAll(self):
        # reset all
        LineData.idx=0
        LineData.lines=[]
        TextData.texts=[]
        self.scene.bufcl()

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
            TextData.rebuildAll(LineData.getData())
            LineData.treewidget.build_hierarchy(r)


    def saveFile(self):
        home_dir = str(Path.cwd())
        fname = QFileDialog.getSaveFileName(self, 'Open file', home_dir, '*.drw')

        # print(Group.hierarchyToJson())
        
        if fname[0]:
            f = open(fname[0], 'w')
            # f.write()
            # json.dump([obj.__dict__ for obj in LineData.getData()], f)
            json.dump(Group.hierarchyToJson(), f, indent=2)
            # print('saved file...')

            

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

            
        fmt = QSurfaceFormat()
        fmt.setVersion(3, 3)
        fmt.setSamples(4)  # if you want multi-sampling
        # QSurfaceFormat.setDefaultFormat(fmt)
        
        self.mywidget = MyWidget()
        self.mywidget.setMouseTracking(True)
        self.mywidget.setFormat(fmt)
        self.mywidget.setGeometry(0, 0, 300, 300)

        
        # window = MyMainWindow()
        self.setGeometry(100, 100, 512, 512)
        self.setMouseTracking(True)
        # window.setCentralWidget(mywidget)

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
        # tree.itemSelectionChanged.connect(tree.on_item_selection_changed)
        self.tree.itemSelectionChanged.connect(self.mywidget.update)
        # tree.myf=mywidget

        toolbar = QToolBar()
        toolbar2 = QToolBar()

        tbtn_new_file = QAction(QIcon(str(path_to_img/"paper.png")), "New", self)
        tbtn_new_file.triggered.connect(self.mywidget.newFile)
        toolbar.addAction(tbtn_new_file)

        tbtn_open_file = QAction(QIcon(str(path_to_img/"folder.png")), "Open", self)
        tbtn_open_file.triggered.connect(self.mywidget.openFile)
        toolbar.addAction(tbtn_open_file)

        tbtn_save_file = QAction(QIcon(str(path_to_img/"diskete.png")), "Save", self)
        tbtn_save_file.triggered.connect(self.mywidget.saveFile)
        toolbar.addAction(tbtn_save_file)

        create_line = QAction("Create Line", self)
        create_line.setCheckable(True)
        create_line.toggled.connect(self.mywidget.createlinetool)
        toolbar2.addAction(create_line)



        toggle_line = QAction("Toggle lines", self)
        # toggle_line.triggered.connect()
        toolbar2.addAction(toggle_line)


        self.addToolBar(toolbar)
        self.addToolBar(toolbar2)
        

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


