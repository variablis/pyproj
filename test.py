import numpy as np
import random
import math

from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QVBoxLayout, QWidget,QLabel
from PyQt6.QtGui import QAction, QCursor, QIcon
from PyQt6.QtCore import Qt, QTimer

from qtmoderngl import ModernGLWidget
from renderer_example import HelloWorld2D, PanTool



# geoobjects={
# "segments": [
#     {"id":1, "type": "line", "visibility":1, "layer":1, "color":[1,1,1,1], "point1": [0.1, 0.3], "point2": [0.33, -1.23], "distance": 22.5, "angle": 23.6, 
#      "constraints":{"vertical": False, "horizontal": False, "perpendicular_to_line_id": None, "paralel_to_line_id": None, 
#         "point1_conected":[None, None], "point2_conected":[None, None], "point1_on_line_id":None, "point2_on_line_id":None}
#     },
# ]
# }

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get(self):
        return [self.x, self.y]

class LineData:
    idx=0
    lines = []
    buffer = []
    newbuffer = []

    def __init__(self, point1, point2, distance=0.0, angle=0.0, visibility=1, layer=1, color=[1,1,1,1], constraints={}):
        self.line_id = self.idx
        self.visibility = visibility
        self.layer = layer
        self.color = color
        self.point1 = point1
        self.point2 = point2
        self.distance = distance
        self.angle = angle
        self.constraints = constraints

        self.selected=False
        self.drag=False
        self.mousepos=None
        self.prev_mousepos=None

    def mpprint(self):
        print("inf:", self.line_id, self.mousepos.get(), self.drag)

    def linemove(self):
        actline = self.lines[self.line_id]

        p1orig = Point(actline.point1[0], actline.point1[1])
        p2orig = Point(actline.point2[0], actline.point2[1])

        # Calculate the change in mouse position
        delta_x = self.mousepos.x - self.prev_mousepos.x
        delta_y = self.mousepos.y - self.prev_mousepos.y

        actline.point1[0] = p1orig.x+delta_x
        actline.point1[1] = p1orig.y+delta_y

        actline.point2[0] = p2orig.x+delta_x
        actline.point2[1] = p2orig.y+delta_y

        # Update the previous mouse position
        self.prev_mousepos = self.mousepos

    
    @classmethod
    def startline(cls, startpoint):
        cls.lines.append(cls(startpoint, startpoint))
        cls.idx +=1
        # print(cls.lines)

    @classmethod
    def livepoint(cls, livepoint):
        if cls.lines:
            cls.lines[-1].point2 = livepoint
        # pass

    @classmethod
    def add(cls, endpoint, distance=0.0, angle=0.0, visibility=1, layer=1, color=[1,1,1,1], constraints={}):
    # def add(cls, point1, point2, distance=0.0, angle=0.0, visibility=1, layer=1, color=[1,1,1,1], constraints={}):
        # cls.lines.append(cls(point1, point2, distance, angle, visibility, layer, color, constraints))

        if cls.lines:
            cls.lines[-1].point2 = endpoint
            cls.lines[-1].color = color

            # buf = cls.buffer
            cls.buffer.append([ cls.lines[-1].point1 + cls.lines[-1].color , cls.lines[-1].point2 + cls.lines[-1].color ])
            # cls.buffer = buf

    @classmethod
    def getData(cls):
        return cls.lines
    
    # @classmethod
    # def updateBuffer(cls):
    #     tmp_list = []
    #     for elem in cls.lines:
    #         tmp_list.append([ elem.point1 + elem.color , elem.point2 + elem.color ])

    #     print(cls.buffer)
    #     cls.buffer=tmp_list 

    @classmethod
    def makeBuffer(cls):
        
        tmp_list = []
        # buf = cls.buffer
        for elem in cls.lines:
            tmp_list.append([ elem.point1 + elem.color , elem.point2 + elem.color ])

        # cls.buffer = tmp
        cls.newbuffer = tmp_list
        # print(tmp_list)
        return np.array(cls.newbuffer)

    @classmethod
    def printData(cls):
        for elem in cls.lines:
            print(f"Line ID: {elem.line_id}, Point1: {elem.point1}, Point2: {elem.point2}, color: {elem.color}")

    @classmethod
    def printNewBuffer(cls):
        print(cls.newbuffer)


class LineSegment:
    def __init__(self):
        
        self.startcx=None
        self.startcy=None

        self.endcx=None
        self.endcy=None

        self.myvert = np.array([[]])
        self.mycircle =[]

        self.toolstate=False
        self.distance=0.0
        self.degrees=0.0

    def toolactive(self, checked):
        self.toolstate = checked
        if not checked:
            print('exit tool')

            global circles
            global livecircles
            livecircles = circles

    def pointadd(self, clicks):
        global verts
        global circles

        if self.toolstate:
            if not clicks %2:
                # print("end")
                print('segment done')
                # LineData.add([self.startcx, self.startcy], [self.endcx, self.endcy], distance=self.distance, angle=self.degrees)
                # janofikse beigu punkts tikai
                LineData.add([self.endcx, self.endcy], distance=self.distance, angle=self.degrees)
                # verts = np.concatenate((verts, self.myvert), axis=0)
            else:
                # print("not end")
                pass
            circles.append(self.mycircle)

    def updatepoints(self, mp, clicks, window, pan, zfakt):
        sw=window.width()/512/zfakt
        sh=window.height()/512/zfakt
        cx = (mp.x*2 -1*sw+pan[0])
        cy =(-mp.y*2 +1*sh+pan[1])

        if clicks %2:
            LineData.livepoint([cx, cy])

            p1=Point(self.startcx, self.startcy)
            p2=Point(cx, cy)
            self.distance = distance2points(p1, p2)
            self.degrees = angle2points(p1, p2)

    def createpoints(self, mp, clicks, window, pan, zfakt):
        global verts
        global liveverts

        global circles
        global livecircles

        sw=window.width()/512/zfakt
        sh=window.height()/512/zfakt
        cx = (mp.x*2 -1*sw+pan[0])
        cy =(-mp.y*2 +1*sh+pan[1])


        if not clicks %2:
            self.startcx=cx
            self.startcy=cy

        self.endcx=cx
        self.endcy=cy
    
        self.mycircle = drawCircle(0.015, cx, cy)

        # self.myvert = np.array([
        #     [self.startcx, self.startcy, 1,1,1,1],
        #     [cx, cy, 1,1,1,1]
        # ])
        # liveverts = np.concatenate((verts, self.myvert), axis=0)

        if not clicks %2:
            LineData.startline([self.startcx, self.startcy])
        

        livecircles = circles + [self.mycircle]

def distance2points(p1, p2):
    point1 = np.array([p1.x, p1.y])
    point2 = np.array([p2.x, p2.y])
    vector = point2 - point1
    # Calculate the Euclidean distance between the two points
    return np.linalg.norm(vector)

def angle2points(p1, p2):
    point1 = np.array([p1.x, p1.y])
    point2 = np.array([p2.x, p2.y])
    vector = point2 - point1
    # Calculate the angle in radians
    angle_rad = np.arctan2(vector[1], vector[0])
    # Convert the angle to degrees if needed
    angle_deg = np.degrees(angle_rad)
    # Ensure the angle is in the range [0, 360) degrees
    return (angle_deg + 360) % 360

def point_on_line(mouse_pt, a_pt, b_pt, precision=0.035):
    # Check if the mouse point is on the line segment defined by a_pt and b_pt

    # Vectors from line start to mouse point and along the line segment
    ap = np.array([mouse_pt.x - a_pt[0], mouse_pt.y - a_pt[1]])
    ab = np.array([b_pt[0] - a_pt[0], b_pt[1] - a_pt[1]])

    # Dot products
    dot_ap_ab = np.dot(ap, ab)
    dot_ab_ab = np.dot(ab, ab)

    # Check if the mouse point is close enough to the line segment
    if 0 <= dot_ap_ab <= dot_ab_ab and abs(np.cross(ap, ab)) < precision:
        return True  # Mouse point is on the line segment
    else:
        return False  # Mouse point is not on the line segment

def checkpoint(mouse_pt, wsize, zf):
    sw = wsize[0]/512/zf
    sh = wsize[1]/512/zf
    cx = (mouse_pt.x*2 -1*sw+pan_tool.value[0])
    cy = (-mouse_pt.y*2 +1*sh+pan_tool.value[1])

    for d in LineData.getData():
        a_pt = d.point1
        b_pt = d.point2
        
        if not d.selected:
            d.color = [1,1,1,1]

        if point_on_line(Point(cx,cy), a_pt, b_pt):
            if not d.selected:
                d.color = [1,0,1,1]
            # print(d.line_id)

uds=None
def checkclickedpoint(mouse_pt, wsize, zf):
    sw = wsize[0]/512/zf
    sh = wsize[1]/512/zf
    cx = (mouse_pt.x*2 -1*sw+pan_tool.value[0])
    cy = (-mouse_pt.y*2 +1*sh+pan_tool.value[1])

    for d in LineData.getData():
        a_pt = d.point1
        b_pt = d.point2
        # d.color = [1,1,1,1]

        if point_on_line(Point(cx,cy), a_pt, b_pt):
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
        a_pt = d.point1
        b_pt = d.point2

        if point_on_line(Point(cx,cy), a_pt, b_pt):
            # d.color = [.5,.5,.1,1]
            print("line drag start")
            d.drag=True
            d.mousepos = d.prev_mousepos = Point(cx,cy)


def linedrag(mouse_pt, wsize, zf):
    sw = wsize[0]/512/zf
    sh = wsize[1]/512/zf
    cx = (mouse_pt.x*2 -1*sw+pan_tool.value[0])
    cy = (-mouse_pt.y*2 +1*sh+pan_tool.value[1])

    for d in LineData.getData():
        if d.drag:
            d.mousepos =  Point(cx,cy)
            # d.mpprint()
            d.linemove()
    # LineData.updateBuffer()


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



verts = np.array([[0,0, 1,1,1,1],[0,0, 1,1,1,1]])
liveverts =np.array([[0,0, 1,1,1,1],[0,0, 1,1,1,1]]) #verts+create line aktivais

pan_tool = PanTool()
lseg = LineSegment()

circles = []
livecircles =[]

def drawCircle( radius,  x1,  y1):
    circle_dots = []  # Array to store dots for the current circle

    for angle in range(0, 360, 60):
    # for(double i = 0; i < 2 * M_PI; i += 2 * M_PI / NUMBER_OF_VERTICES):
        rad_angle = angle * 3.14 / 180
        circle_dots.append([x1+radius*math.sin(rad_angle), y1+radius*math.cos(rad_angle), 1,1,1,1])
        # print(circle_dots)

    return circle_dots

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

        self.scene.distancetext(str(lseg.distance)+'...'+str(lseg.degrees))
        self.scene.linerender(LineData.makeBuffer(), self.zfakt)
        self.scene.circl(np.array(livecircles))

    def mycoord(self):
        # origin ir main windowa kreisais augsejais sturis 0,0
        # pozicija tiek nolasita pa visu ekranu!!
        local_pos = self.mapFromGlobal(QCursor.pos())
        # wsize=[
        #     local_pos.x()/ 512/self.zfakt, #self.size().width(),
        #     local_pos.y()/ 512/self.zfakt #self.size().height()
        # ]
        mousepos = Point(local_pos.x()/ 512/self.zfakt, 
                         local_pos.y()/ 512/self.zfakt)
        return mousepos
    
    def createlinetool(self, checked):
        self.createlineactive = checked
        self.clickcount=0
        lseg.toolactive(checked)

        
    def wheelEvent(self, event):
        self.zoomy +=event.angleDelta().y()/120
        self.zfakt=pow(1.4, self.zoomy)
        self.scene.zom(self.zfakt)
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
            # l.createpoints(self.mycoord(), self.clickcount, self.size(), pan_tool.value, self.zfakt)
            lseg.updatepoints(self.mycoord(), self.clickcount, self.size(), pan_tool.value, self.zfakt)
        else:
            checkpoint(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt)
            linedrag(self.mycoord(), (self.size().width(), self.size().height()), self.zfakt)
            

        # LineData.updateBuffer()
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


def run_app():
    app = QApplication([])

    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setSamples(4)  # if you want multi-sampling
    # QSurfaceFormat.setDefaultFormat(fmt)
    
    mywidget = MyWidget()
    mywidget.setMouseTracking(True)
    mywidget.setFormat(fmt)
    
    window = QMainWindow()
    window.setMouseTracking(True)
    window.setCentralWidget(mywidget)
    window.setGeometry(100, 100, 512, 512)

    toolbar = QToolBar()
    window.addToolBar(toolbar)

    create_line = QAction("Create Line", window)
    create_line.setCheckable(True)
    create_line.toggled.connect(mywidget.createlinetool)
    toolbar.addAction(create_line)

    join_dots = QAction("Join Dots", window)
    # join_dots.triggered.connect()
    toolbar.addAction(join_dots)

    toggle_line = QAction("Toggle lines", window)
    # toggle_line.triggered.connect()
    toolbar.addAction(toggle_line)

    drag_action = QAction(QIcon("msdf_gen/fonts.bmp"),"Drag", window)
    drag_action.setCheckable(True)
    # drag_action.triggered.connect()
    toolbar.addAction(drag_action)

    window.show()
    app.exec()


if __name__ == "__main__":
    run_app()
