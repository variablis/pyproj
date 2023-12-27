import numpy as np
import json
from pathlib import Path

from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QFileDialog, QVBoxLayout, QWidget,QLabel, QHBoxLayout, QSplitter, QSizePolicy
from PyQt6.QtGui import QAction, QCursor, QIcon
from PyQt6.QtCore import Qt, QTimer

from qtmoderngl import ModernGLWidget
from renderer_example import HelloWorld2D, PanTool

from drw_classes import Point
from drw_tree import MyTreeWidget
from drw_linedata import LineData, Group
from drw_text import TextData
from drw_math_func import *


from pathlib import Path
bundle_dir = Path(__file__).parent
path_to_img = Path.cwd() / bundle_dir / "img"


class LineSegment:
    def __init__(self):

        self.startpoint=None
        self.endpoint=None
        
        self.startcx=None
        self.startcy=None

        self.endcx=None
        self.endcy=None

        # self.myvert = np.array([[]])
        # self.mycircle =[]

        self.toolstate=False
        self.distance=0.0
        self.degrees=0.0

    def toolactive(self, checked):
        self.toolstate = checked
        if not checked:
            print('exit tool')

            # global circles
            # global livecircles
            # livecircles = circles

    def pointadd(self, clicks):
        # global verts
        # global circles

        if self.toolstate:
            if not clicks %2:
                # print("end")
                print('segment done')
                # LineData.add([self.startcx, self.startcy], [self.endcx, self.endcy], distance=self.distance, angle=self.degrees)
                # janofikse beigu punkts tikai
                LineData.add(self.endpoint, distance=self.distance, angle=self.degrees)
                # verts = np.concatenate((verts, self.myvert), axis=0)
            else:
                # print("not end")
                pass
            # circles.append(self.mycircle)

    def updatepoints(self, mp, clicks, window, pan, zfakt):
        sw=window.width()/512/zfakt
        sh=window.height()/512/zfakt
        cx = (mp.x*2 -1*sw+pan[0])
        cy =(-mp.y*2 +1*sh+pan[1])

        if clicks %2:
            LineData.livepoint(Point(cx, cy))

            TextData.update(f'{round(self.distance,4):.4f} {round(self.degrees,2):.2f}°', Point(cx, cy), LineData.getLastElem().line_id)

            p1=self.startpoint
            p2=Point(cx, cy)
            self.distance = distance2points(p1, p2)
            self.degrees = angle2points(p1, p2)

    def createpoints(self, mp, clicks, window, pan, zfakt):
        # global verts
        # global liveverts

        # global circles
        # global livecircles

        sw=window.width()/512/zfakt
        sh=window.height()/512/zfakt
        cx = (mp.x*2 -1*sw+pan[0])
        cy =(-mp.y*2 +1*sh+pan[1])


        if not clicks %2:
            self.startpoint = Point(cx,cy)
            # self.startcx=cx
            # self.startcy=cy

        self.endpoint = Point(cx,cy)
        # self.endcx=cx
        # self.endcy=cy
    
        # self.mycircle = drawCircle(0.015, cx, cy)

        # self.myvert = np.array([
        #     [self.startcx, self.startcy, 1,1,1,1],
        #     [cx, cy, 1,1,1,1]
        # ])
        # liveverts = np.concatenate((verts, self.myvert), axis=0)

        if not clicks %2:
            # print('segment start--')
            LineData.startline(self.startpoint)

            TextData.add(f'{round(self.distance,4):.4f}', self.startpoint, LineData.getLastElem().line_id)

            # TextData.printBuffer()
            # TextData.makeBuffer()
        

        # livecircles = circles + [self.mycircle]


def tempf(mouse_pt, wsize, zf):
    sw = wsize[0]/512/zf
    sh = wsize[1]/512/zf
    cx = (mouse_pt.x*2 -1*sw+pan_tool.value[0])
    cy = (-mouse_pt.y*2 +1*sh+pan_tool.value[1])

    return cx, cy


def checkpoint(mouse_pt, wsize, zf):
    cx, cy = tempf(mouse_pt, wsize, zf)

    for d in LineData.getData():
        a_pt = d.points[0]
        b_pt = d.points[1]
        
        if not d.selected:
            d.color = [1,1,1,1]

        test = point_on_line(Point(cx,cy), a_pt, b_pt)

        if test[0]:
            if not d.selected:
                d.color = [1,0,1,1]

uds=None
def checkclickedpoint(mouse_pt, wsize, zf):
    cx, cy = tempf(mouse_pt, wsize, zf)

    for d in LineData.getData():
        a_pt = d.points[0]
        b_pt = d.points[1]
        # d.color = [1,1,1,1]

        test = point_on_line(Point(cx,cy), a_pt, b_pt)
        if test[0]:
            d.color = [0,1,.3,1]
            d.selected=True
        else:
            d.selected=False
 

def check_dr_point(mouse_pt, wsize, zf):
    cx, cy = tempf(mouse_pt, wsize, zf)

    for d in LineData.getData():
        a_pt = d.points[0]
        b_pt = d.points[1]

        test = point_on_line(Point(cx,cy), a_pt, b_pt)

        if test[0]==True:
            d.drag=True
            d.mousepos = d.prev_mousepos = Point(cx,cy)

            if test[1] == 0:
                d.dragobj=0

            elif test[1] == 1:
                # print('vienns')
                d.dragobj=1

            elif test[1] == 2:
                d.dragobj=2
        else:
            d.dragobj=-1
                


def linedrag(mouse_pt, wsize, zf):
    cx, cy = tempf(mouse_pt, wsize, zf)

    for d in LineData.getData():
        
        if d.drag:
            d.mousepos = Point(cx,cy)
            # d.mpprint()
            # d.linemove()
            # print(d.dragobj)
            d.pointmove(d.dragobj)
            # print(d.line_id)

            # update coresponding text element
            text = f'{round(d.distance,4):.4f} {round(d.angle,2):.2f}°'
            TextData.update( text, d.mousepos, d.line_id)

           


def linestopdrag(mouse_pt, wsize, zf):
    sw = wsize[0]/512/zf
    sh = wsize[1]/512/zf
    cx = (mouse_pt.x*2 -1*sw+pan_tool.value[0])
    cy = (-mouse_pt.y*2 +1*sh+pan_tool.value[1])

    for d in LineData.getData():
        if d.drag:
            d.drag=False
            d.mousepos =  Point(cx,cy)
            # d.mpprint()
            print("drag end")
    # LineData.updateBuffer()


pan_tool = PanTool()
lseg = LineSegment()



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
        lseg.toolactive(checked)


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
                lseg.createpoints(self.mycoord(), self.clickcount, self.size(), pan_tool.value, self.zfakt)
                self.clickcount+=1
                lseg.pointadd(self.clickcount)
            else:
                checkclickedpoint(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt)

                # stulbs workarounds lai izslegtu selekcibju bez peles  kustinasanas
                checkpoint(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt)
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
            drag_distance = distance2points(self.mycoord(), self.user_drag_start)
            # print(drag_distance)
            if drag_distance > self.startDragDistance:
                # Drag has started
                print("Drag Started")
                # Reset the drag start position
                check_dr_point(self.user_drag_start, (self.size().width(), self.size().height()), self.zfakt)
                global uds
                self.user_drag_start = None
                uds = self.user_drag_start 

        if self.createlineactive:
            

            lseg.updatepoints(self.mycoord(), self.clickcount, self.size(), pan_tool.value, self.zfakt)
        else:
            checkpoint(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt)
            linedrag(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt)
            

        self.update()
        self.render()

    def mouseReleaseEvent(self, event):
        pan_tool.stop_drag(self.mycoord())
        self.scene.pan(pan_tool.value)

        linestopdrag(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt)

        global uds
        self.user_drag_start = None
        uds = self.user_drag_start 

        self.update()



    # def keyPressEvent(self, event):
    #     print(event.key())
    #     if event.key() == Qt.Key.Key_Delete:
    #         print("Delete key pressed!")

    #         # LineData.deleteData()
    #     else:
    #         super().keyPressEvent(event)


    def newFile(self):
        LineData.lines=[]
        TextData.texts=[]
        self.scene.bufcl()

  
        LineData.root.remove_root_children()
        LineData.treewidget.build_hierarchy(Group.getRoot())

    
        self.update()
        # self.render()
        print('new file...')

    def openFile(self):
        home_dir = str(Path.cwd())
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir)

        if fname[0]:
            f = open(fname[0], 'r')
            # data = f.read()
            data = json.load(f)

            r=Group.createGroupFromJson(data)
            LineData.root=r
            # LineData.printData()
            LineData.treewidget.build_hierarchy(r)

    def saveFile(self):
        home_dir = str(Path.cwd())
        fname = QFileDialog.getSaveFileName(self, 'Open file', home_dir, '*.drw')

        # print(Group.hierarchyToJson())
        # append somwhere doc global data
        # "filename": 'xx', "preferences": {"zoom": 1, "units": 10}, 
        
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

        join_dots = QAction("Join Dots", self)
        # join_dots.triggered.connect()
        toolbar2.addAction(join_dots)

        toggle_line = QAction("Toggle lines", self)
        # toggle_line.triggered.connect()
        toolbar2.addAction(toggle_line)

        drag_action = QAction( "Drag", self)
        drag_action.setCheckable(True)
        # drag_action.triggered.connect()
        toolbar2.addAction(drag_action)

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


