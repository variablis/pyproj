from dc_linedata import LineData, SceneData
from dc_text import TextData
from dc_point import Point
from df_math import *


# line segment class definition
class LineSegment:
    def __init__(self):

        self.startpoint=None
        self.endpoint=None
        self.toolstate=False
 

    def tool_active(self, checked):
        self.toolstate = checked
        if not checked:
            print('exit tool')


    def point_add(self, clicks):
        if self.toolstate:
            if not clicks %2:
                print('segment done')
                # janofikse beigu punkts tikai
                LineData.add(self.endpoint)
            else:
                # print("not end")
                pass


    def update_points(self, cx, cy, clicks):
        if clicks %2:
            LineData.livepoint(Point(cx, cy))

            distance = LineData.getLastElem().distance *SceneData.units
            angle = LineData.getLastElem().angle

            text = f'{round(distance,4):.2f} {round(angle,2):.2f}°'
            TextData.update(text, LineData.getLastElem().points, LineData.getLastElem().line_id)


    def create_points(self, cx, cy, clicks):
        if not clicks %2:
            self.startpoint = Point(cx,cy)

        self.endpoint = Point(cx,cy)

        if not clicks %2:
            # print('segment start--')
            LineData.startline(self.startpoint)

            distance = LineData.getLastElem().distance *SceneData.units
            angle = LineData.getLastElem().angle

            text = f'{round(distance,4):.2f} {round(angle,2):.2f}°'
            TextData.add(text, LineData.getLastElem().points, LineData.getLastElem().line_id)




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
    for l in LineData.getData():
        if l.drag:
            l.mousepos = Point(cx,cy)
            # d.linemove()
            # print(d.dragobj)
            l.pointmove(l.dragobj)
            # print(d.line_id)

            distance = l.distance *SceneData.units
            angle = l.angle

            # update coresponding text element
            text = f"{round(distance,4):.2f} {round(angle,2):.2f}°"
            TextData.update( text, l.points, l.line_id)


def linestopdrag(cx, cy):
    for l in LineData.getData():
        if l.drag:
            l.drag=False
            l.mousepos =  Point(cx,cy)
            print("drag end")



