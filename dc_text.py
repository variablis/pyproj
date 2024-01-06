import json
import numpy as np
from pathlib import Path

from dc_linedata import LineData, SceneData
from dc_point import Point
from df_math import points_to_angle

import pyrr

# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_data = Path.cwd() / bundle_dir / "msdf"


# class for msdf generated text conversion to quad vertices
class TextData:
    
    # open generated msdf font json file
    f = open(path_to_data / "fonts.json")
    data = json.load(f)
    f.close()

    texts = []

    def __init__(self, str, points, lid):
        self.lineid = lid
        self.str = str
        self.pointsarr = points
        self.vtx = self.text_to_vertices()


    # return array of quad vertices for each char
    def text_to_vertices(self):
        zf = SceneData.zoom_factor
        image = (256, 256)
        arr=[]
        for i,s in enumerate(self.str):
            addspace = 0.0
            if s==' ':
                addspace = 0.5
            else:
                for glyph in TextData.data.get("glyphs", []):
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
                        midpoint = Point((p1.x+p2.x)/2*zf, (p1.y+p2.y)/2*zf)
                        

                        off = np.array([
                            [addspace+ midpoint.x, midpoint.y],
                            [addspace+ midpoint.x, midpoint.y],
                            [addspace+ midpoint.x, midpoint.y],
                            [addspace+ midpoint.x, midpoint.y],
                        ])

                        uv = np.array([
                            [sl, tb],
                            [sr, tb],
                            [sr, tt],
                            [sl, tt]
                        ])


                        # print(ord(s))

                        angle = points_to_angle(p1, p2)

                        # flip text when angle from 90-270
                        if angle > 90 and angle < 270:
                            angle = angle - 180
                        

                        angle = np.radians(-angle)
                        # Create a 2D rotation matrix
                        rotation_matrix = pyrr.Matrix33.from_eulers([0.0, angle, 0.0])
                        # Apply the rotation matrix to each point
                        rotated_points = np.dot(ob, rotation_matrix[:2, :2])
                        narr = np.concatenate(((rotated_points+off)/zf, uv), axis=1)
                        arr.append(narr.tolist())

        return arr


    @classmethod
    def add(cls, str, points, lid):
        cls.texts.append(cls(str, points, lid))


    @classmethod
    def update(cls, str, points, lid):
        for index, elem in enumerate(cls.texts):
            if elem.lineid == lid:
                updated_elem = cls(str, points, lid)
                cls.texts[index] = updated_elem
                break

            
    @classmethod
    def deleteSelected(cls, ids):
        tmp = [elem for elem in cls.texts if elem.lineid not in ids]
        cls.texts = tmp


    @classmethod
    def rebuildAll(cls, clear=False):
        if clear:
            cls.texts = []
        for line in LineData.getData():
            distance = line.distance *SceneData.units
            angle = line.angle

            text = f"{round(distance,4):.2f} {round(angle,2):.2f}°"
            cls.texts.append(cls(text, line.points, line.line_id))


    @classmethod
    def makeBuffer(cls):
        tmp_list = []
        for elem in cls.texts:
            tmp_list.append( elem.vtx )

        if tmp_list:
            return np.vstack(tmp_list)
        else:
            return np.array([[]])


    @classmethod
    def printBuffer(cls):
        print(cls.texts)

