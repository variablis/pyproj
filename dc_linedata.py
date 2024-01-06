import numpy as np
from df_math import *


# global scene data class
class SceneData():
    # filename = 'untitled'
    units = 10
    grid = 1
    zoom_factor = 1.0
    # saved = False

# group class definition for hierarchical grouping
class Group:
    rootobj = None

    def __init__(self, name):
        self.name = name
        self.children = []

        # add child to root by default
        if self.rootobj is not None:
            self.rootobj.add_child(self)

    def add_child(self, child):
        if hasattr(child, 'parent') and child.parent is not None:
            child.parent.children.remove(child)

        self.children.append(child)
        child.parent = self


    def delete_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None
        else:
            print("Child not found in the group.")

    @classmethod
    def remove_root_children(cls):
        cls.rootobj.children=[]

    @classmethod
    def addRoot(cls, name):
        # Create the root group
        if cls.rootobj is None:
            cls.rootobj = cls(name)
        return cls.rootobj

    @classmethod
    def getRoot(cls):
        return cls.rootobj
    
    @classmethod
    def printAll(cls):
        return cls.rootobj.print_hierarchy()

    def print_hierarchy(self, indent=0):
        print("  " * indent + self.name)
        for child in self.children:
            if isinstance(child, Group):
                child.print_hierarchy(indent + 1)
            else:
                print("  " * (indent + 1), child.name)


    @classmethod
    def hierarchyToJson(cls, parent=None):

        result = {"name": cls.rootobj.name, "children": []}
        for child in cls.rootobj.children:
            if isinstance(child, Group):
                result["children"].append(child.hierarchyToJson())
                print('xxx')
            else:
                result["children"].append({"name": child.name, "data": child.dataToJson()})
        return result


    @classmethod
    def createGroupFromJson(cls, json_data, parent=None):
        group_name = json_data["name"]
        new_group = cls(group_name)

        if parent is not None:
            parent.add_child(new_group)

        for elem in json_data.get("children", []):
            if "data" in elem:
                # Create a leaf node
                ch_name = elem["name"]
                ch_data= elem["data"]

                # new_child = Object(ch_name)  # You may need to replace Object with the appropriate class
                # new_group.add_child(new_child)

                LineData.jsonToData(ch_data["points"], ch_data["id"], ch_data["distance"],ch_data["angle"], ch_data["color"], ch_name)
                # ld = LineData(line_id=ch_data["id"], name=ch_name)
                new_group.add_child(LineData.getOneData(ch_data["id"]))
                
            else:
                # Recursively create a group
                cls.createGroupFromJson(elem, parent=new_group)

        return new_group


# object class definition
class Object:
    def __init__(self, name):
        self.name = name
        self.parent = None


# line data storage class
class LineData(Object):
    idx=0
    lines = []
    root=None
    treewidget=None

    def __init__(self, line_id, points=[], distance=0.0, angle=0.0, visibility=1, layer=1, color=[1,1,1,1], constraints={}, name=''):
        Object.__init__(self, name)

        self.line_id = line_id
        self.visibility = visibility
        self.layer = layer
        self.color = color
        self.points = points #masivs ar punktiem
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

        # kapec p1orig nav point klasee??
        # print(p1orig)

        # Calculate the change in mouse position
        delta_x = self.mousepos.x - self.prev_mousepos.x
        delta_y = self.mousepos.y - self.prev_mousepos.y

        actline.points[0] = [p1orig[0]+delta_x, p1orig[1]+delta_y]
        actline.points[1] = [p2orig[0]+delta_x, p2orig[1]+delta_y]

        # Update the previous mouse position
        self.prev_mousepos = self.mousepos

    def pointmove(self, ptid):
        # actline = self.lines[self.line_id]
        actline=self

        actline.distance = points_to_distance(actline.points[0], actline.points[1])
        actline.angle = points_to_angle(actline.points[0], actline.points[1])

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
        cls.lines.append(cls( line_id=cls.idx, points=[startpoint, startpoint] ))
        cls.idx +=1
        
        # print(cls.lines)

    @classmethod
    def livepoint(cls, livepoint):
        if cls.lines:
            lastline = cls.lines[-1]
            lastline.points[1] = livepoint

            lastline.distance = points_to_distance(lastline.points[0], lastline.points[1])
            lastline.angle = points_to_angle(lastline.points[0], lastline.points[1])
        # pass

    @classmethod
    def add(cls, endpoint, color=[1,1,1,1]):

        if cls.lines:
            lastline = cls.lines[-1]
            lastline.points[1] = endpoint
            lastline.color = color

            lastline.distance = points_to_distance(lastline.points[0], lastline.points[1])
            lastline.angle = points_to_angle(lastline.points[0], lastline.points[1])


            lastline.name = str(lastline.line_id) + ' - line'
            
            cls.root.add_child(lastline)
            cls.treewidget.build_hierarchy(cls.root)
  
    @classmethod
    def deselectAll(cls):
        for elem in cls.lines:
            elem.color=[1,1,1,1]
            elem.selected=False
    
    @classmethod
    def getData(cls):
        return cls.lines
    
    @classmethod
    def getLastElem(cls):
        if cls.lines:
            return cls.lines[-1]
    
    @classmethod
    def getOneData(cls, id):
        for elem in cls.lines:
            if elem.line_id==id:
                return elem
        return None
            
        # return next(x for x in cls.lines if x.line_id == id )
    

    @classmethod
    def getSelectedIds(cls):
        tmp = [elem.line_id for elem in cls.lines if elem.selected]
        return tmp

    @classmethod
    def deleteSelected(cls):
        tmp2 = [elem for elem in cls.lines if elem.selected]
        for elem in tmp2:
            cls.root.delete_child(elem)
        cls.treewidget.build_hierarchy(cls.root)
    
        tmp = [elem for elem in cls.lines if not elem.selected]
        cls.lines = tmp

        # print(cls.lines)
    

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
        print(len(cls.lines))
        for elem in cls.lines:
            print(f"Line ID: {elem.line_id}, Point1: {elem.points[0].xy}, Point2: {elem.points[1].xy}, color: {elem.color}")


    def dataToJson(self):
        return {
                'id': self.line_id,
                'distance': self.distance,
                'angle': self.angle,
                'color': self.color,
                'points' : [self.points[0].xy, self.points[1].xy]
            }
    
    @classmethod
    def jsonToData(cls, points, line_id, distance, angle, color, name):
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
