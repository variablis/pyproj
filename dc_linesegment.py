
from dc_linedata import LineData, Group
from dc_text import TextData
from dc_point import Point
from df_math import *

# line segment class definition
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

    def tool_active(self, checked):
        self.toolstate = checked
        if not checked:
            print('exit tool')

            # global circles
            # global livecircles
            # livecircles = circles

    def point_add(self, clicks):
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

    def update_points(self, mp, clicks, window, pan, zfakt):
        sw=window.width()/512/zfakt
        sh=window.height()/512/zfakt
        cx = (mp.x*2 -1*sw+pan[0])
        cy =(-mp.y*2 +1*sh+pan[1])

        if clicks %2:
            LineData.livepoint(Point(cx, cy))

            TextData.update(f'{round(self.distance,4):.4f} {round(self.degrees,2):.2f}°', Point(cx, cy), LineData.getLastElem().line_id)

            p1=self.startpoint
            p2=Point(cx, cy)
            self.distance = points_to_distance(p1, p2)
            self.degrees = points_to_angle(p1, p2)

    def create_points(self, mp, clicks, window, pan, zfakt):
        sw=window.width()/512/zfakt
        sh=window.height()/512/zfakt
        cx = (mp.x*2 -1*sw+pan[0])
        cy =(-mp.y*2 +1*sh+pan[1])


        if not clicks %2:
            self.startpoint = Point(cx,cy)
            # self.startcx=cx
            # self.startcy=cy

        self.endpoint = Point(cx,cy)


        if not clicks %2:
            # print('segment start--')
            LineData.startline(self.startpoint)

            TextData.add(f'{round(self.distance,4):.4f}', self.startpoint, LineData.getLastElem().line_id)

            # TextData.printBuffer()
            # TextData.makeBuffer()


def checkpoint(cx, cy):
    for d in LineData.getData():
        a_pt = d.points[0]
        b_pt = d.points[1]
        
        if not d.selected:
            d.color = [1,1,1,1]

        test = point_on_line(Point(cx,cy), a_pt, b_pt)

        if test[0]:
            if not d.selected:
                d.color = [1,0,1,1]



def checkclickedpoint(cx, cy):
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
 
def check_dr_point(cx, cy):
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
                

def linedrag(cx, cy):
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

           

def linestopdrag(cx, cy):
    for d in LineData.getData():
        if d.drag:
            d.drag=False
            d.mousepos =  Point(cx,cy)
            # d.mpprint()
            print("drag end")
    # LineData.updateBuffer()
