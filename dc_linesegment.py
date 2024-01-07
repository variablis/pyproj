from dc_linedata import LineData, SceneData
from dc_text import TextData
# from dc_point import Point
from df_math import *


class LineSegment:
    '''
    line segment class definition
    '''
    def __init__(self):

        self.startpoint=None
        self.endpoint=None
        self.toolstate=False
 

    def tool_active(self, checked):
        self.toolstate = checked
        if not checked:
            # print('exit tool')
            pass


    def point_add(self, clicks):
        if self.toolstate:
            if not clicks %2:
                # print('segment done')
                # janofikse beigu punkts tikai
                LineData.add(self.endpoint)
            else:
                # print("not end")
                pass


    def update_points(self, mouse_pt, clicks):
        if clicks %2:
            LineData.livepoint(mouse_pt)

            distance = LineData.getLastElem().distance *SceneData.units
            angle = LineData.getLastElem().angle

            text = f'{round(distance,4):.2f} {round(angle,2):.2f}°'
            TextData.update(text, LineData.getLastElem().points, LineData.getLastElem().line_id)


    def create_points(self, mouse_pt, clicks):
        if not clicks %2:
            self.startpoint = mouse_pt

        self.endpoint = mouse_pt

        if not clicks %2:
            # print('segment start--')
            LineData.startline(self.startpoint)

            distance = LineData.getLastElem().distance *SceneData.units
            angle = LineData.getLastElem().angle

            text = f'{round(distance,4):.2f} {round(angle,2):.2f}°'
            TextData.add(text, LineData.getLastElem().points, LineData.getLastElem().line_id)



def check_point(mouse_pt):
    '''
    checks all lines against mouse point to detect if mouse hovers any of them
    '''
    for line in LineData.getAllLines():
        a_pt = line.points[0]
        b_pt = line.points[1]
        
        if not line.selected:
            line.color = [1,1,1,1]

        test = point_on_line(mouse_pt, a_pt, b_pt)

        if test[0]:
            if not line.selected:
                line.color = [1,0,1,1]


def check_clicked_point(mouse_pt):
    '''
    checks all lines against mouse point to detect if user has clicked on any of them
    '''
    for d in LineData.getAllLines():
        a_pt = d.points[0]
        b_pt = d.points[1]
        # d.color = [1,1,1,1]

        test = point_on_line(mouse_pt, a_pt, b_pt)
        if test[0]:
            d.color = [0,1,.3,1]
            d.selected=True
        else:
            d.selected=False


def check_drag_point(mouse_pt):
    for d in LineData.getAllLines():
        a_pt = d.points[0]
        b_pt = d.points[1]

        test = point_on_line(mouse_pt, a_pt, b_pt)

        if test[0]==True:
            d.drag=True
            d.mousepos = d.prev_mousepos = mouse_pt

            if test[1] == 0:
                d.dragtype=0

            elif test[1] == 1:
                d.dragtype=1

            elif test[1] == 2:
                d.dragtype=2
        else:
            d.dragtype= None


def line_drag(mouse_pt):
    for l in LineData.getAllLines():
        if l.drag:
            l.mousepos = mouse_pt
            l.update_point_data(l.dragtype)
            # print(d.line_id)

            distance = l.distance *SceneData.units
            angle = l.angle

            # update coresponding text element
            text = f"{round(distance,4):.2f} {round(angle,2):.2f}°"
            TextData.update( text, l.points, l.line_id)


def line_stop_drag(mouse_pt):
    for l in LineData.getAllLines():
        if l.drag:
            l.drag=False
            l.mousepos =  mouse_pt
            # print("drag end")



