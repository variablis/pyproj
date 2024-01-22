from dc_linedata import LineData, SceneData
from dc_text import TextData
from dc_point import Point
from df_math import point_on_line, points_to_distance, points_to_angle_abs


class Group:
    '''
    group class definition for hierarchical grouping
    '''
    root = None
    tree_widget = None

    def __init__(self, name):
        self.name = name
        self.children = []


    def add_child(self, child):
        '''
        add child to parent, if child already has parent, change it to new parent
        '''
        if hasattr(child, 'parent') and child.parent != None:
            child.parent.children.remove(child)

        self.children.append(child)
        child.parent = self

        if Group.tree_widget:
            Group.tree_widget.build_hierarchy(Group.root)

    def delete_child(self, child):
        '''
        delete child if exists
        '''
        if child in self.children:
            self.children.remove(child)
            child.parent = None

        if Group.tree_widget:
            Group.tree_widget.build_hierarchy(Group.root)

    def hierarchy_to_json(self, parent=None):
        '''
        create json from group hierarchy
        '''
        if parent == None:
            parent = self
        result = {"name": parent.name, "children": []}
        for child in parent.children:
            if isinstance(child, Group):
                result["children"].append(child.hierarchy_to_json())
                # print('iekseja grupa')
            else:
                result["children"].append({"name": child.name, "data": child.data_to_json()})
        return result
    
    def print_hierarchy(self, indent=0):
        '''
        print hierarchy on screen
        '''
        print("  " * indent + self.name)
        for child in self.children:
            if isinstance(child, Group):
                child.print_hierarchy(indent + 1)
            else:
                print("  " * (indent + 1), child.name)

    @classmethod
    def json_to_hierarchy(cls, json, parent=None):
        '''
        create group hierarchy from json data
        '''
        group_name = json["name"]
        new_group = cls(group_name)

        if parent != None:
            parent.add_child(new_group)

        for elem in json.get("children", []):
            if "data" in elem:
                # Create a leaf node
                ch_name = elem["name"]
                ch_data = elem["data"]
                pt_a, pt_b = ch_data["points"]

                line = LineSegment(ch_data["id"], [Point(pt_a[0], pt_a[1]), Point(pt_b[0], pt_b[1])], ch_data["distance"],ch_data["angle"], ch_data["color"], ch_name)
                LineData.add_line(line)
                new_group.add_child(line)

            else:
                # Recursively create a group
                cls.json_to_hierarchy(elem, parent=new_group)

        return new_group
    

class Object:
    '''
    object class definition
    '''
    def __init__(self):
        self.parent = None


class LineSegment(Object):
    '''
    line segment class definition
    '''
    def __init__(self, line_id=None, points: list=[], distance=0.0, angle=0.0, color=[1,1,1,1], name=''):
        Object.__init__(self)

        self.line_id = line_id
        self.color = color
        self.points = points
        self.distance = distance
        self.angle = angle
        self.name = name

        self.selected = False
        self.hovered = False
        self.drag = False

        self.mousepos = None
        self.prev_mousepos = None 
        self.dragtype = None

        # self.visibility = visibility TODO:
        # self.layer = layer TODO:
        # self.constraints = constraints TODO:


    def update_point_data(self, pt_id):
        '''
        update points postion based on its id.
        0, 1 = endpoints, 2 = both endpoints (line)
        '''
        self.distance = points_to_distance(self.points[0], self.points[1])
        self.angle = points_to_angle_abs(self.points[0], self.points[1])
        
        # one of the line end points moving
        if pt_id==0 or pt_id==1:
            self.points[pt_id] = self.mousepos

        # both line points moving = whole line is moved
        if pt_id==2:
            # Calculate the change in mouse position
            delta_x = self.mousepos.x - self.prev_mousepos.x
            delta_y = self.mousepos.y - self.prev_mousepos.y
            delta = Point(delta_x, delta_y)

            p1_orig = self.points[0]
            p2_orig = self.points[1]

            self.points[0] = p1_orig + delta
            self.points[1] = p2_orig + delta

        # Update the previous mouse position
        self.prev_mousepos = self.mousepos


    def start_line(self, mouse_pt):
        '''
        start new line, starting new line segment
        '''
        newline = LineSegment(line_id=LineData.g_index, points=[mouse_pt, mouse_pt])
        LineData.add_new_line(newline)

        line = LineData.get_last_line()
        text = TextData.make_text(line.distance, line.angle)
        TextData.add(text, line.points, line.line_id)


    def end_line(self, mouse_pt):
        '''
        line segment complete - end line, update values
        '''
        lastline = LineData.get_last_line()
        lastline.points[1] = mouse_pt
        lastline.distance = points_to_distance(lastline.points[0], lastline.points[1])
        lastline.angle = points_to_angle_abs(lastline.points[0], lastline.points[1])
        lastline.name = 'line - ' + str(lastline.line_id +1) 
        
        Group.root.add_child(lastline)
        
        # update text after user creates line endpoint
        text = TextData.make_text(lastline.distance, lastline.angle)
        TextData.update(text, lastline.points, lastline.line_id)

        # print('segment done')


    def update_live_point(self, mouse_pt):
        '''
        update live endpoint when line creation tool is active 
        '''
        line = LineData.get_last_line()
        line.mousepos = mouse_pt
        line.update_point_data(1)

        text = TextData.make_text(line.distance, line.angle)
        TextData.update(text, line.points, line.line_id)


    def check_point(self, mouse_pt):
        '''
        checks all lines against mouse point to detect if mouse hovers any of them
        '''
        for line in LineData.get_all_lines():
            a_pt = line.points[0]
            b_pt = line.points[1]

            test, _ = point_on_line(mouse_pt, a_pt, b_pt, 0.035 /SceneData.zoom_factor, 0.05 /SceneData.zoom_factor)

            if test == True:
                line.hovered = True

                if line.selected:
                    # line.color = [1,1,0,1]
                    pass
                else:
                    line.color = [1,0,1,1]
            else:
                line.hovered = False

                if line.selected:
                    # line.color = [1,1,0,1]
                    pass
                else:
                    line.color = [1,1,1,1]


    def check_clicked_point(self, mouse_pt):
        '''
        checks all lines against mouse point to detect if user has clicked on any of them
        '''
        for line in LineData.get_all_lines():
            a_pt = line.points[0]
            b_pt = line.points[1]

            test, _ = point_on_line(mouse_pt, a_pt, b_pt, 0.035 /SceneData.zoom_factor, 0.05 /SceneData.zoom_factor)
            
            if test == True:
                line.selected = True
                line.color = [0,1,.3,1]
            else:
                line.selected = False


    def check_drag_point(self, mouse_pt):
        '''
        checks all lines against mouse point to detect if user drags any of them
        '''
        for line in LineData.get_all_lines():
            a_pt = line.points[0]
            b_pt = line.points[1]

            test, dragtype = point_on_line(mouse_pt, a_pt, b_pt, 0.035 /SceneData.zoom_factor, 0.05 /SceneData.zoom_factor)

            if test == True:
                line.drag = True
                line.mousepos = line.prev_mousepos = mouse_pt
                line.dragtype = dragtype
            else:
                line.dragtype = None


    def line_drag(self, mouse_pt):
        '''
        checks all lines for drag and dragtype attribute, if any is draggable, update its position
        '''
        for line in LineData.get_all_lines():
            if line.drag:
                line.mousepos = mouse_pt
                line.update_point_data(line.dragtype)

                text = TextData.make_text(line.distance, line.angle)
                TextData.update(text, line.points, line.line_id)


    def line_stop_drag(self, mouse_pt):
        '''
        drag ends. resetset all draggable line drag attribute
        '''
        for line in LineData.get_all_lines():
            if line.drag:
                line.drag = False
                line.mousepos = mouse_pt
                # print("drag end")


    def data_to_json(self):
        '''
        return line as json
        '''
        return {
                'id': self.line_id,
                'distance': self.distance,
                'angle': self.angle,
                'color': self.color,
                'points' : [self.points[0].xy, self.points[1].xy]
            }