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

    atlas = data["atlas"]
    glyphs = data["glyphs"]

    texts = []
    angle_visible = True

    def __init__(self, str, points, lid):
        self.image_w = TextData.atlas['width']
        self.image_h = TextData.atlas['height']
        self.lineid = lid
        self.str = str
        self.pointsarr = points
        self.vtx = self.text_to_vertices()



    def text_to_vertices(self):
        '''
        return array of quad vertices for each char
        '''
        arr=[]
        zf = SceneData.zoom_factor

        for i,s in enumerate(self.str):
            for glyph in TextData.glyphs:
                if glyph["unicode"] == ord(s):

                    ofs = glyph["advance"] # glyph spacing
                    pb = glyph.get("planeBounds") # glyph plane bounds
                    dd = glyph.get("atlasBounds") # glyph coords in generated texture

                    if not pb:
                        pb = dd = {'left':0, 'right':0, 'top':0, 'bottom':0}

                    sc = 0.065

                    xl = (pb['left']+i*ofs)*sc
                    xr = (pb['right']+i*ofs)*sc
                    yt = pb['top']*sc
                    yb = pb['bottom']*sc

                    sl = dd['left'] /self.image_w
                    sr = dd['right'] /self.image_w
                    tt = 1-dd['top'] /self.image_h
                    tb = 1-dd['bottom'] /self.image_h
                    
 
                    # 4x4 matrix for 4 vertices and 4 uv coordinates (x,y,u,v)
                    ob = np.array([
                        [xl, yb],
                        [xr, yb],
                        [xr, yt], 
                        [xl, yt],
                    ])

                    if not self.pointsarr:
                        self.pointsarr = [Point(0,0),Point(0,0)]

                    p1 = self.pointsarr[0]
                    p2 = self.pointsarr[1]
                    midpoint = Point((p1.x +p2.x) /2 *zf, (p1.y +p2.y) /2 *zf)
                    
                    yoffs = 0.05
                    off = np.array([
                        [ midpoint.x, midpoint.y +yoffs],
                        [ midpoint.x, midpoint.y +yoffs],
                        [ midpoint.x, midpoint.y +yoffs],
                        [ midpoint.x, midpoint.y +yoffs],
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
        '''
        add text to array
        '''
        cls.texts.append(cls(str, points, lid))


    @classmethod
    def update(cls, str, points, lid):
        '''
        update text by line id
        '''
        for index, elem in enumerate(cls.texts):
            if elem.lineid == lid:
                updated_elem = cls(str, points, lid)
                cls.texts[index] = updated_elem
                break


    @classmethod
    def delete_selected(cls, ids):
        '''
        remove text from array based on line id
        '''
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
        '''
        rebuild all text from line data
        '''
        if clear:
            cls.texts = []
        for line in LineData.get_all_lines():
            str = cls.make_text(line.distance, line.angle)
            cls.texts.append(cls(str, line.points, line.line_id))


    @classmethod
    def make_buffer(cls):
        '''
        return vertex array for render buffer
        '''
        tmp_list = []
        for elem in cls.texts:
            tmp_list.append( elem.vtx )

        if tmp_list:
            return np.vstack(tmp_list)
        else:
            return np.array([[]])


