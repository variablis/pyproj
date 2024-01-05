import json
import numpy as np
from pathlib import Path

from dc_point import Point
from df_math import points_to_distance, points_to_angle

import pyrr
import math

# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_dat = Path.cwd() / bundle_dir / "msdf"


# class for msdf generated text conversion to quad vertices
class TextData:
    
    # open generated msdf font json file
    f = open(path_to_dat / "fonts.json")
    fdata = json.load(f)
    f.close()

    texts = []

    def __init__(self, str, points, lid):
        self.lineid = lid
        self.str = str
        self.pointsarr = points
        self.vtx = self.txt2vtx()
    

    # return array of quad vertices for each char
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
                        

                        if not self.pointsarr:
                            self.pointsarr = [Point(0,0),Point(0,0)]
                            

                        #   [xl +addspace+ self.offset.x, yb + self.offset.y, sl, tb],
                        #     [xr +addspace+ self.offset.x, yb + self.offset.y, sr, tb],
                        #     [xr +addspace+ self.offset.x, yt + self.offset.y, sr, tt], 
                        #     [xl +addspace+ self.offset.x, yt + self.offset.y, sl, tt], 
                        
                        offs=0.05
                        # 4x4 matrix for 4 vertices and 4 uv coordinates (x,y,u,v)
                        ob = np.array([
                            # -0.5, -0.5, 0.0, 1.0,
                            # 0.5, -0.5, 1.0, 1.0, 
                            # 0.5, 0.5,  1.0, 0.0, 
                            # -0.5, 0.5, 0.0, 0.0, 

                            [xl, yb+offs],
                            [xr, yb+offs],
                            [xr, yt+offs], 
                            [xl, yt+offs], 
                        ])

                        p1=self.pointsarr[0]
                        p2=self.pointsarr[1]
                        midpoint = Point((p1.x+p2.x)/2, (p1.y+p2.y)/2)
                        

                        off = np.array([
                            [addspace+ midpoint.x, midpoint.y],
                            [addspace+ midpoint.x, midpoint.y],
                            [addspace+ midpoint.x, midpoint.y],
                            [addspace+ midpoint.x, midpoint.y],
                        ])

                        uv=np.array([
                            [sl, tb],
                            [sr, tb],
                            [sr, tt],
                            [sl, tt]
                        ])


                        # print(offset.xy)
                        # print(ob)
                        # print(ord(s))

                        angle = points_to_angle(p1, p2)

                        # flip text when angle from 90-270
                        if angle > 90 and angle < 270:
                            angle = angle - 180
                        
                        # Define the angle of rotation in radians
                        angle = np.radians(-angle)

                        # Create a 2D rotation matrix
                        rotation_matrix = pyrr.Matrix33.from_eulers([0.0, angle, 0.0])

                        # Apply the rotation matrix to each point
                        rotated_points = np.dot(ob, rotation_matrix[:2, :2])

                        narr = np.concatenate((rotated_points+off, uv), axis=1)
                        # print(narr)

                        arr.append(narr.tolist())

        return arr


    @classmethod
    def add(cls, str, points, lid):
        cls.texts.append(cls(str, points, lid))
        # print(cls.texts)

    @classmethod
    def update(cls, str, points, lid):
        # print(lid)
        # if cls.texts:
        #     cls.texts[lid] = cls(str, offset, lid)

        for index, elem in enumerate(cls.texts):
            if elem.lineid == lid:
                updated_elem = cls(str, points, lid)
                cls.texts[index] = updated_elem
                break


    # @classmethod
    # def getElem(cls, idx):
    #     return cls.texts[idx]
            
    @classmethod
    def deleteSelected(cls, ids):
        tmp = [elem for elem in cls.texts if elem.lineid not in ids]
        cls.texts = tmp
        print(cls.texts)


    @classmethod
    def rebuildAll(cls, linelist):
        # print(linelist)
        for line in linelist:
            p1 = line.points[0]
            p2 = line.points[1]
            distance = points_to_distance(p1, p2)
            degrees = points_to_angle(p1, p2)

            text = f"{round(distance,4):.4f} {round(degrees,2):.2f}°"
            cls.texts.append(cls(text, line.points, line.line_id))


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
        print(cls.texts)

