import json
import numpy as np
import pyrr
from pathlib import Path

from dc_linedata import LineData, SceneData
from dc_point import Point
from df_math import points_to_angle

# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_data = Path.cwd() / bundle_dir / "msdf"



class TextData:
    '''
    class for text data storage
    '''
    
    # open generated msdf font json file
    f = open(path_to_data / "fonts.json")
    data = json.load(f)
    f.close()

    texts = []
    angle_visible = True

    def __init__(self, str, points, lid):
        self.lineid = lid
        self.str = str
        self.pointsarr = points
        self.vtx = self.text_to_vertices()


    def text_to_vertices(self):
        '''
        return array of quad vertices for each char
        '''
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
    def add(cls, line):
        str = cls.make_text(line.distance, line.angle)
        cls.texts.append(cls(str, line.points, line.line_id))


    @classmethod
    def update(cls, line):
        str = cls.make_text(line.distance, line.angle)

        for index, text in enumerate(cls.texts):
            if text.lineid == line.line_id:
                updated_text = cls(str, line.points, line.line_id)
                cls.texts[index] = updated_text
                break


    @classmethod
    def delete_selected(cls, ids):
        tmp = [elem for elem in cls.texts if elem.lineid not in ids]
        cls.texts = tmp


    @classmethod
    def make_text(cls, distance, angle):
        '''
        convert distance and angle to string
        keep 2 decimals without rounding for distance
        '''
        distance = distance *SceneData.units
        intval, decval = str(distance).split('.')
        distance = f"{intval}.{decval[:2]}"
        angle = angle

        if TextData.angle_visible:
            return f"{distance} {angle:.2f}°"
        else:
            return f"{distance}"


    @classmethod
    def rebuild_all(cls, clear=False):
        if clear:
            cls.texts = []
        for line in LineData.get_all_lines():
            str = cls.make_text(line.distance, line.angle)
            cls.texts.append(cls(str, line.points, line.line_id))


    @classmethod
    def make_buffer(cls):
        tmp_list = []
        for elem in cls.texts:
            tmp_list.append( elem.vtx )

        if tmp_list:
            return np.vstack(tmp_list)
        else:
            return np.array([[]])


    @classmethod
    def print_buffer(cls):
        print(cls.texts)

