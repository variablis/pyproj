import numpy as np
from df_math import points_to_distance, points_to_angle_abs
from dc_point import Point


class SceneData():
    '''
    global scene data storage class
    '''
    # filename = 'untitled' TODO:
    units = 10
    grid = 1
    zoom_factor = 1.0
    # saved = False TODO:


class Group:
    '''
    group class definition for hierarchical grouping
    '''

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


    def delete_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None
        else:
            print("Child not found in the group.")


    def print_hierarchy(self, indent=0):
        print("  " * indent + self.name)
        for child in self.children:
            if isinstance(child, Group):
                child.print_hierarchy(indent + 1)
            else:
                print("  " * (indent + 1), child.name)


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
                ch_data= elem["data"]

                LineData.json_to_data(ch_data["points"], ch_data["id"], ch_data["distance"],ch_data["angle"], ch_data["color"], ch_name)
                new_group.add_child(LineData.get_one_data(ch_data["id"]))
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


class LineData(Object):
    '''
    line data storage class
    '''
    g_index = 0 # global line index
    lines = []
    root = None
    treewidget = None

    def __init__(self, line_id, points: list=[], distance=0.0, angle=0.0, color=[1,1,1,1], name=''):
        Object.__init__(self)

        self.line_id = line_id
        self.color = color
        self.points = points
        self.distance = distance
        self.angle = angle
        self.name = name

        # self.visibility = visibility TODO:
        # self.layer = layer TODO:
        # self.constraints = constraints TODO:

        self.selected = False
        self.hovered = False

        self.drag = False
        self.mousepos = None
        self.prev_mousepos = None 
        self.dragtype = None


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
    
    @classmethod
    def add_startpoint(cls, startpoint):
        '''
        add line starting point to array and increase global index
        '''
        cls.lines.append(cls( line_id=cls.g_index, points=[startpoint, startpoint] ))
        cls.g_index += 1
        # print(cls.lines)

    @classmethod
    def add_endpoint(cls, endpoint, color=[1,1,1,1], group=None):
        '''
        add line endpoint, add it to group (currently only root), refresh tree widget structure 
        '''
        if cls.lines:
            lastline = cls.lines[-1]
            lastline.points[1] = endpoint
            lastline.color = color
            lastline.distance = points_to_distance(lastline.points[0], lastline.points[1])
            lastline.angle = points_to_angle_abs(lastline.points[0], lastline.points[1])
            lastline.name = 'line - ' + str(lastline.line_id +1) 
            
            if group:
                group.add_child(lastline)
            else:
                cls.root.add_child(lastline)

            cls.treewidget.build_hierarchy(cls.root)
  
    @classmethod
    def deselect_all(cls):
        for elem in cls.lines:
            elem.color=[1,1,1,1]
            elem.selected=False
    
    @classmethod
    def get_all_lines(cls):
        return cls.lines
    
    @classmethod
    def get_last_elem(cls):
        if cls.lines:
            return cls.lines[-1]
    
    @classmethod
    def get_one_data(cls, id):
        for elem in cls.lines:
            if elem.line_id==id:
                return elem
        return None

    @classmethod
    def get_selected_ids(cls):
        tmp = [elem.line_id for elem in cls.lines if elem.selected]
        return tmp

    @classmethod
    def delete_selected(cls):
        tmp2 = [elem for elem in cls.lines if elem.selected]
        for elem in tmp2:
            cls.root.delete_child(elem)
        cls.treewidget.build_hierarchy(cls.root)
    
        tmp = [elem for elem in cls.lines if not elem.selected]
        cls.lines = tmp
        # print(cls.lines)
    
    @classmethod
    def make_buffer(cls):
        tmp_list = []
        for elem in cls.lines:
            tmp_list.append([ 
                elem.points[0].xy + elem.color,
                elem.points[1].xy + elem.color
            ])
        # print(tmp_list)
        return np.array(tmp_list)

    @classmethod
    def print_data(cls):
        print(len(cls.lines))
        for elem in cls.lines:
            print(f"Line ID: {elem.line_id}, Point1: {elem.points[0].xy}, Point2: {elem.points[1].xy}, color: {elem.color}")

    def data_to_json(self):
        return {
                'id': self.line_id,
                'distance': self.distance,
                'angle': self.angle,
                'color': self.color,
                'points' : [self.points[0].xy, self.points[1].xy]
            }
    
    @classmethod
    def json_to_data(cls, points, line_id, distance, angle, color, name):
        cls.lines.append(
            cls(
                line_id = line_id,
                distance = distance,
                angle = angle,
                color = color,
                points = [Point(points[0][0], points[0][1]), Point(points[1][0], points[1][1])],
                name = name
            )
        )
