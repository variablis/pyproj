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
        self.xy = [x,y]

    def __sub__(self, other_point):
        """Overloaded subtraction operator for Point instances."""
        return Point(self.x - other_point.x, self.y - other_point.y)
    
    def __add__(self, other_point):
        """Overloaded addition operator for Point instances."""
        return Point(self.x + other_point.x, self.y + other_point.y)


    def get(self):
        return [self.x, self.y]

class LineData:
    idx=0
    lines = []
    buffer = []
    # activebuffer = []

    def __init__(self, point=[], point1=0, point2=0, distance=0.0, angle=0.0, visibility=1, layer=1, color=[1,1,1,1], constraints={}):
        self.line_id = self.idx
        self.visibility = visibility
        self.layer = layer
        self.color = color
        self.point = point #masivs ar punktiem
        self.point1 = point1
        self.point2 = point2
        self.distance = distance
        self.angle = angle
        self.constraints = constraints

        self.selected=False
        self.drag=False
        self.mousepos=None
        self.prev_mousepos=None
        
        self.dragobj=-1

    def mpprint(self):
        print("inf:", self.line_id, self.mousepos.get(), self.drag)

    def linemove(self):
        actline = self.lines[self.line_id]

        p1orig = actline.point[0]
        p2orig = actline.point[1]

        # kapec p1orig nav point klasae??
        # print(p1orig)

        # Calculate the change in mouse position
        delta_x = self.mousepos.x - self.prev_mousepos.x
        delta_y = self.mousepos.y - self.prev_mousepos.y

        actline.point[0] = [p1orig[0]+delta_x, p1orig[1]+delta_y]
        actline.point[1] = [p2orig[0]+delta_x, p2orig[1]+delta_y]

        # Update the previous mouse position
        self.prev_mousepos = self.mousepos

    def pointmove(self, ptid):
        actline = self.lines[self.line_id]

        if ptid==0 or ptid==1:

            porig = actline.point[ptid]

            # Calculate the change in mouse position
            delta_x = self.mousepos.x - self.prev_mousepos.x
            delta_y = self.mousepos.y - self.prev_mousepos.y

            # print([porig[ptid]])

            # actline.point[ptid] = [ porig[0]+delta_x, porig[1]+delta_y] #tiek saglabats ofsets ko mes negroibam
            actline.point[ptid] = self.mousepos

        if ptid==2:
            p1orig = actline.point[0]
            p2orig = actline.point[1]

            # kapec p1orig nav point klasae??
            # print(p1orig)

            # Calculate the change in mouse position
            delta_x = self.mousepos.x - self.prev_mousepos.x
            delta_y = self.mousepos.y - self.prev_mousepos.y

            delta = Point(delta_x, delta_y)

            actline.point[0] = p1orig + delta
            actline.point[1] = p2orig + delta

        # Update the previous mouse position
        self.prev_mousepos = self.mousepos
    
    @classmethod
    def startline(cls, startpoint):
        cls.lines.append(cls( [startpoint, startpoint] ))
        cls.idx +=1
        # print(cls.lines)

    @classmethod
    def livepoint(cls, livepoint):
        if cls.lines:
            cls.lines[-1].point[1] = livepoint
        # pass

    @classmethod
    def add(cls, endpoint, distance=0.0, angle=0.0, visibility=1, layer=1, color=[1,1,1,1], constraints={}):

        if cls.lines:
            cls.lines[-1].point[1] = endpoint
            cls.lines[-1].color = color

            # buf = cls.buffer
            cls.buffer.append([ cls.lines[-1].point[0].xy + cls.lines[-1].color , cls.lines[-1].point[1].xy + cls.lines[-1].color ])
            # cls.buffer = buf

    @classmethod
    def getData(cls):
        return cls.lines
    

    @classmethod
    def makeBuffer(cls):
        
        tmp_list = []
        # buf = cls.buffer
        for elem in cls.lines:
            tmp_list.append([ elem.point[0].xy + elem.color , elem.point[1].xy + elem.color ])

        # cls.buffer = tmp
        # cls.activebuffer = tmp_list
        # print(tmp_list)
        return np.array(tmp_list)

    @classmethod
    def printData(cls):
        for elem in cls.lines:
            print(f"Line ID: {elem.line_id}, Point1: {elem.point[0]}, Point2: {elem.point[1]}, color: {elem.color}")

    @classmethod
    def printBuffer(cls):
        print(cls.buffer)


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
                LineData.add(Point(self.endcx, self.endcy), distance=self.distance, angle=self.degrees)
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
            LineData.livepoint(Point(cx, cy))

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
            LineData.startline(Point(self.startcx, self.startcy))
        

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

def point_on_line(mouse_pt, a_pt, b_pt, precision=0.035, endpoint_threshold=0.05):
    # Check if the mouse point is on the line segment defined by a_pt and b_pt

    # Vectors from line start to mouse point and along the line segment
    ap = np.array((mouse_pt - a_pt).xy)
    ab = np.array((b_pt - a_pt).xy)

    # Check if the mouse point is close to one of the endpoints
    dist_to_a = np.linalg.norm((a_pt - mouse_pt).xy)
    dist_to_b = np.linalg.norm((b_pt - mouse_pt).xy)


    if dist_to_a < endpoint_threshold:
        return True, 0  # Mouse point is close to the first endpoint

    if dist_to_b < endpoint_threshold:
        return True, 1  # Mouse point is close to the second endpoint

    # Dot products
    dot_ap_ab = np.dot(ap, ab)
    dot_ab_ab = np.dot(ab, ab)

    # Check if the mouse point is close enough to the line segment
    if 0 <= dot_ap_ab <= dot_ab_ab and abs(np.cross(ap, ab)) < precision:
        return True, 2  # Mouse point is on the line segment
    
    
    return False, None # Mouse point is not on the line segment


def checkpoint(mouse_pt, wsize, zf):
    sw = wsize[0]/512/zf
    sh = wsize[1]/512/zf
    cx = (mouse_pt.x*2 -1*sw+pan_tool.value[0])
    cy = (-mouse_pt.y*2 +1*sh+pan_tool.value[1])

    for d in LineData.getData():
        a_pt = d.point[0]
        b_pt = d.point[1]
        
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
        a_pt = d.point[0]
        b_pt = d.point[1]
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
        a_pt = d.point[0]
        b_pt = d.point[1]

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
