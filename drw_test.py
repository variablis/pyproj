import typing
from PyQt6 import QtGui
import numpy as np
import random
import math

from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QFileDialog, QVBoxLayout, QWidget,QLabel, QHBoxLayout, QSplitter, QSizePolicy
from PyQt6.QtGui import QAction, QCursor, QIcon
from PyQt6.QtCore import Qt, QTimer

from qtmoderngl import ModernGLWidget
from renderer_example import HelloWorld2D, PanTool

from drw_classes import Point
import json
from pathlib import Path

from drw_tree import MyTreeWidget, Group, Object

# geoobjects={
# "segments": [
#     {"id":1, "type": "line", "visibility":1, "layer":1, "color":[1,1,1,1], "point1": [0.1, 0.3], "point2": [0.33, -1.23], "distance": 22.5, "angle": 23.6, 
#      "constraints":{"vertical": False, "horizontal": False, "perpendicular_to_line_id": None, "paralel_to_line_id": None, 
#         "point1_conected":[None, None], "point2_conected":[None, None], "point1_on_line_id":None, "point2_on_line_id":None}
#     },
# ]
# }



class LineData(Object):
    idx=0
    lines = []
    # buffer = []
    root=None
    treewidget=None

    def __init__(self, points=[], distance=0.011, angle=0.0, visibility=1, layer=1, color=[1,1,1,1], constraints={}, name=''):
        Object.__init__(self, name)

        self.line_id = self.idx
        self.visibility = visibility
        self.layer = layer
        self.color = color
        self.points = points #masivs ar punktiem
        # self.point1 = point1
        # self.point2 = point2
        self.distance = distance
        self.angle = angle
        self.constraints = constraints


        self.selected=False
        self.drag=False
        self.mousepos=None
        self.prev_mousepos=None
        
        self.dragobj=-1

        
        self.name=name

    def mpprint(self):
        print("inf:", self.line_id, self.mousepos.get(), self.drag)

    def linemove(self):
        actline = self.lines[self.line_id]

        p1orig = actline.points[0]
        p2orig = actline.points[1]

        # kapec p1orig nav point klasae??
        # print(p1orig)

        # Calculate the change in mouse position
        delta_x = self.mousepos.x - self.prev_mousepos.x
        delta_y = self.mousepos.y - self.prev_mousepos.y

        actline.points[0] = [p1orig[0]+delta_x, p1orig[1]+delta_y]
        actline.points[1] = [p2orig[0]+delta_x, p2orig[1]+delta_y]

        # Update the previous mouse position
        self.prev_mousepos = self.mousepos

    def pointmove(self, ptid):
        actline = self.lines[self.line_id]

        actline.distance = distance2points(actline.points[0], actline.points[1])
        actline.degrees = angle2points(actline.points[0], actline.points[1])

        if ptid==0 or ptid==1:

            porig = actline.points[ptid]

            # Calculate the change in mouse position
            delta_x = self.mousepos.x - self.prev_mousepos.x
            delta_y = self.mousepos.y - self.prev_mousepos.y

            # print([porig[ptid]])

            # actline.point[ptid] = [ porig[0]+delta_x, porig[1]+delta_y] #tiek saglabats ofsets ko mes negroibam
            actline.points[ptid] = self.mousepos

        if ptid==2:
            p1orig = actline.points[0]
            p2orig = actline.points[1]

            # kapec p1orig nav point klasae??
            # print(p1orig)

            # Calculate the change in mouse position
            delta_x = self.mousepos.x - self.prev_mousepos.x
            delta_y = self.mousepos.y - self.prev_mousepos.y

            delta = Point(delta_x, delta_y)

            actline.points[0] = p1orig + delta
            actline.points[1] = p2orig + delta

        # Update the previous mouse position
        self.prev_mousepos = self.mousepos
    
    @classmethod
    def startline(cls, startpoint):
        cls.lines.append(cls( points=[startpoint, startpoint] ))
        cls.idx +=1
        # print(cls.lines)

    @classmethod
    def livepoint(cls, livepoint):
        if cls.lines:
            cls.lines[-1].points[1] = livepoint
        # pass

    @classmethod
    def add(cls, endpoint, distance=0.0, angle=0.0, visibility=1, layer=1, color=[1,1,1,1], constraints={}):

        if cls.lines:
            cls.lines[-1].points[1] = endpoint
            cls.lines[-1].color = color

            cls.lines[-1].name=str(cls.lines[-1].line_id) + ' - line'
            cls.root.add_child(cls.lines[-1])
            # cls.root.print_hierarchy()

            cls.treewidget.build_hierarchy(cls.root)
  

    @classmethod
    def getData(cls):
        return cls.lines
    

    @classmethod
    def makeBuffer(cls):
        
        tmp_list = []
        for elem in cls.lines:
            tmp_list.append([ 
                elem.points[0].xy + elem.color,
                elem.points[1].xy + elem.color
            ])

        # print(tmp_list)
        return np.array(tmp_list)

    @classmethod
    def printData(cls):
        for elem in cls.lines:
            print(f"Line ID: {elem.line_id}, Point1: {elem.points[0]}, Point2: {elem.points[1]}, color: {elem.color}")

    # @classmethod
    # def printBuffer(cls):
    #     print(cls.buffer)


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

            TextData.update(f'{round(self.distance,4):.4f} {round(self.degrees,2):.2f}°', Point(cx, cy))

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

            TextData.add(f'{round(self.distance,4):.4f}', self.startpoint)

            # TextData.printBuffer()
            # TextData.makeBuffer()
        

        # livecircles = circles + [self.mycircle]


class TextData:
    
    # Opening JSON file
    f = open('msdf_gen/fonts.json')
    # returns JSON object as # a dictionary
    fdata = json.load(f)
    # Closing file
    f.close()

    texts = []

    def __init__(self, str, offset):
        self.str=str
        self.offset=offset
        self.vtx=self.txt2vtx()

    def txt2vtx(self):
        image = (256, 256)
        arr=[]
        for i,s in enumerate(self.str):
            addspace = 0.0
            if s==' ':
                addspace = 0.5
            else:
                for glyph in self.fdata.get("glyphs", []):
                    if glyph.get("unicode") == ord(s):
                        dd = glyph.get("atlasBounds", {})
                        pb = glyph.get("planeBounds", {})

                        sc = 0.06

                        xl=(pb['left']+i*.5)*sc
                        xr=(pb['right']+i*.5)*sc
                        yt=pb['top']*sc
                        yb=pb['bottom']*sc

                        sl=dd['left']/image[0]
                        sr=dd['right']/image[0]
                        tt=1-dd['top']/image[1]
                        tb=1-dd['bottom']/image[1]
                        

                        if not self.offset:
                            self.offset = Point(0,0)
                        # xy uv
                        ob = [
                            # -0.5, -0.5, 0.0, 1.0,
                            # 0.5, -0.5, 1.0, 1.0, 
                            # 0.5, 0.5,  1.0, 0.0, 
                            # -0.5, 0.5, 0.0, 0.0, 

                            xl +addspace+ self.offset.x, yb + self.offset.y, sl, tb,
                            xr +addspace+ self.offset.x, yb + self.offset.y, sr, tb, 
                            xr +addspace+ self.offset.x, yt + self.offset.y, sr, tt, 
                            xl +addspace+ self.offset.x, yt + self.offset.y, sl, tt, 
                        ]

                        # print(offset.xy)
                        # print(ob)
                        # print(ord(s))

                        arr.append(ob)
        return arr

    @classmethod
    def add(cls, str, offset):
        cls.texts.append(cls(str, offset))
        # print(cls.texts)

    @classmethod
    def update(cls, str, offset, idx=-1):
        if cls.texts:
            cls.texts[idx] = cls(str, offset)

    # @classmethod
    # def getElem(cls, idx):
    #     return cls.texts[idx]

    @classmethod
    def makeBuffer(cls):

        tmp_list = []
        for elem in cls.texts:
            tmp_list.append( elem.vtx )

            # print('eee')
            # print(elem.offset.xy)

        # print(np.vstack(tmp_list))
        # return np.array(tmp_list)
        if tmp_list:
            return np.vstack(tmp_list)
        else:
            return np.array([[]])

    @classmethod
    def printBuffer(cls):
        for elem in cls.texts:
            print(elem.str)


def distance2points(p1, p2):
    point1 = np.array(p1.xy)
    point2 = np.array(p2.xy)
    vector = point2 - point1
    # Calculate the Euclidean distance between the two points

    return math.dist(p2.xy, p1.xy)
    # return np.linalg.norm(vector)


def angle2points(p1, p2):
    # point1 = np.array(p1.xy)
    # point2 = np.array(p2.xy)
    # vector = point2 - point1
    # # Calculate the angle in radians
    # angle_rad = np.arctan2(vector[1], vector[0])
    # # Convert the angle to degrees if needed
    # angle_deg = np.degrees(angle_rad)
    # # Ensure the angle is in the range [0, 360) degrees
    # return (angle_deg + 360) % 360

    vector = p2-p1
    rad = math.atan2(vector.y, vector.x)

    return math.degrees(rad)%360

def point_on_line(mouse_pt, a_pt, b_pt, precision=0.035, endpoint_threshold=0.05):
    # Check if the mouse point is on the line segment defined by a_pt and b_pt

    # Check if the mouse point is close to one of the endpoints
    # dist_to_a = np.linalg.norm((a_pt - mouse_pt).xy)
    # dist_to_b = np.linalg.norm((b_pt - mouse_pt).xy)

    dist_to_a = math.dist(a_pt.xy, mouse_pt.xy)
    dist_to_b = math.dist(b_pt.xy, mouse_pt.xy)


    if dist_to_a < endpoint_threshold:
        return True, 0  # Mouse point is close to the first endpoint

    if dist_to_b < endpoint_threshold:
        return True, 1  # Mouse point is close to the second endpoint

    # Vectors from line start to mouse point and along the line segment
    # ap = np.array((mouse_pt - a_pt).xy)
    # ab = np.array((b_pt - a_pt).xy)
    ap = mouse_pt - a_pt
    ab = b_pt - a_pt
    # Dot products
    # dot_ap_ab = np.dot(ap, ab)
    # dot_ab_ab = np.dot(ab, ab)
    dot_ap_ab = ap.dot2d(ab)
    dot_ab_ab = ab.dot2d(ab)

    # Check if the mouse point is close enough to the line segment
    if 0 <= dot_ap_ab <= dot_ab_ab and abs(ap.cross2d(ab)) < precision:
        return True, 2  # Mouse point is on the line segment
    
    
    return False, None # Mouse point is not on the line segment


def checkpoint(mouse_pt, wsize, zf):
    sw = wsize[0]/512/zf
    sh = wsize[1]/512/zf
    cx = (mouse_pt.x*2 -1*sw+pan_tool.value[0])
    cy = (-mouse_pt.y*2 +1*sh+pan_tool.value[1])

    for d in LineData.getData():
        a_pt = d.points[0]
        b_pt = d.points[1]
        
        if not d.selected:
            d.color = [1,1,1,1]

        test = point_on_line(Point(cx,cy), a_pt, b_pt)

        if test[0]:
            if not d.selected:
                d.color = [1,0,1,1]
            # if test[1] == 0:
            #     # print('nulle')
            #     pass

            # elif test[1] == 1:
            #     # print('vienns')
            #     pass

            # elif test[1] == 2:
            #     if not d.selected:
            #         d.color = [1,0,1,1]
                # print(d.line_id)

uds=None
def checkclickedpoint(mouse_pt, wsize, zf):
    sw = wsize[0]/512/zf
    sh = wsize[1]/512/zf
    cx = (mouse_pt.x*2 -1*sw+pan_tool.value[0])
    cy = (-mouse_pt.y*2 +1*sh+pan_tool.value[1])

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
 

def check_dr_point(drag_start_pt, wsize, zf):
    sw = wsize[0]/512/zf
    sh = wsize[1]/512/zf
    cx = (drag_start_pt.x*2 -1*sw+pan_tool.value[0])
    cy = (-drag_start_pt.y*2 +1*sh+pan_tool.value[1])

    for d in LineData.getData():
        a_pt = d.points[0]
        b_pt = d.points[1]

        test = point_on_line(Point(cx,cy), a_pt, b_pt)

        # if point_on_line(Point(cx,cy), a_pt, b_pt):
        #     # print("line drag start")
        #     d.drag=True
        #     d.mousepos = d.prev_mousepos = Point(cx,cy)

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
    sw = wsize[0]/512/zf
    sh = wsize[1]/512/zf
    cx = (mouse_pt.x*2 -1*sw+pan_tool.value[0])
    cy = (-mouse_pt.y*2 +1*sh+pan_tool.value[1])

    for d in LineData.getData():
        if d.drag:
            d.mousepos =  Point(cx,cy)
            # d.mpprint()
            # d.linemove()
            # print(d.dragobj)
            d.pointmove(d.dragobj)

            # update coresponding text element
            TextData.update( f'{round(d.distance,4):.4f} {round(d.degrees,2):.2f}°', d.mousepos, d.line_id)

           


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

# circles = []
# livecircles =[]

# def drawCircle( radius,  x1,  y1):
#     circle_dots = []  # Array to store dots for the current circle

#     for angle in range(0, 360, 60):
#     # for(double i = 0; i < 2 * M_PI; i += 2 * M_PI / NUMBER_OF_VERTICES):
#         rad_angle = angle * 3.14 / 180
#         circle_dots.append([x1+radius*math.sin(rad_angle), y1+radius*math.cos(rad_angle), 1,1,1,1])
#         # print(circle_dots)

#     return circle_dots

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


    def newFile(self):
        LineData.lines=[]
        TextData.texts=[]
        print('new file...')

    def showFileDialog(self):
        home_dir = str(Path.cwd())
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir)

        if fname[0]:
            f = open(fname[0], 'r')
            data = f.read()
            # self.textEdit.setText(data)
            print(data)

    def saveFile(self):
        home_dir = str(Path.cwd())
        fname = QFileDialog.getSaveFileName(self, 'Open file', home_dir, '*.drw')

        if fname[0]:
            f = open(fname[0], 'w')
            f.write('faila saturs te')
            print('save file...')



def run_app():
    app = QApplication([])

    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setSamples(4)  # if you want multi-sampling
    # QSurfaceFormat.setDefaultFormat(fmt)
    
    mywidget = MyWidget()
    mywidget.setMouseTracking(True)
    mywidget.setFormat(fmt)
    mywidget.setGeometry(0, 0, 300, 300)

    
    window = QMainWindow()
    window.setGeometry(100, 100, 512, 512)
    window.setMouseTracking(True)
    # window.setCentralWidget(mywidget)

    # Create the layout for the central widget
    tree = MyTreeWidget()

    splitter = QSplitter()
    splitter.addWidget(tree)
    splitter.addWidget(mywidget)

    window.setCentralWidget(splitter)
    # Set a minimum size for the second widget
    tree.setMinimumWidth(100)
    tree.setMaximumWidth(180)

    root_group = Group.addRoot('Root')
    LineData.root = root_group
    LineData.treewidget = tree
    tree.build_hierarchy(Group.getRoot())
    tree.itemSelectionChanged.connect(tree.on_item_selection_changed)
 

    toolbar = QToolBar()
    toolbar2 = QToolBar()

    tbtn_new_file = QAction(QIcon("img/paper.png"), "New", window)
    tbtn_new_file.triggered.connect(mywidget.newFile)
    toolbar.addAction(tbtn_new_file)

    tbtn_open_file = QAction(QIcon("img/folder.png"), "Open", window)
    tbtn_open_file.triggered.connect(mywidget.showFileDialog)
    toolbar.addAction(tbtn_open_file)

    tbtn_save_file = QAction(QIcon("img/diskete.png"), "Save", window)
    tbtn_save_file.triggered.connect(mywidget.saveFile)
    toolbar.addAction(tbtn_save_file)

    create_line = QAction("Create Line", window)
    create_line.setCheckable(True)
    create_line.toggled.connect(mywidget.createlinetool)
    toolbar2.addAction(create_line)

    join_dots = QAction("Join Dots", window)
    # join_dots.triggered.connect()
    toolbar2.addAction(join_dots)

    toggle_line = QAction("Toggle lines", window)
    # toggle_line.triggered.connect()
    toolbar2.addAction(toggle_line)

    drag_action = QAction( "Drag", window)
    drag_action.setCheckable(True)
    # drag_action.triggered.connect()
    toolbar2.addAction(drag_action)

    window.addToolBar(toolbar)
    window.addToolBar(toolbar2)

    window.show()
    app.exec()


if __name__ == "__main__":
    run_app()
