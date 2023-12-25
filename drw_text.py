import numpy as np
import json
from drw_classes import Point

class TextData:
    
    # Opening JSON file
    f = open('msdf_gen/fonts.json')
    # returns JSON object as # a dictionary
    fdata = json.load(f)
    # Closing file
    f.close()

    texts = []

    def __init__(self, str, offset, lid):
        self.lineid = lid
        self.str = str
        self.offset = offset
        self.vtx = self.txt2vtx()

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
                        

                        if not self.offset:
                            self.offset = Point(0,0)
                        # xy uv
                        ob = [
                            # -0.5, -0.5, 0.0, 1.0,
                            # 0.5, -0.5, 1.0, 1.0, 
                            # 0.5, 0.5,  1.0, 0.0, 
                            # -0.5, 0.5, 0.0, 0.0, 

                            xl +addspace+ self.offset.x, yb + self.offset.y, sl, tb,
                            xr +addspace+ self.offset.x, yb + self.offset.y, sr, tb, 
                            xr +addspace+ self.offset.x, yt + self.offset.y, sr, tt, 
                            xl +addspace+ self.offset.x, yt + self.offset.y, sl, tt, 
                        ]

                        # print(offset.xy)
                        # print(ob)
                        # print(ord(s))

                        arr.append(ob)
        return arr

    @classmethod
    def add(cls, str, offset, lid):
        cls.texts.append(cls(str, offset, lid))
        # print(cls.texts)

    @classmethod
    def update(cls, str, offset, lid):
        # print(lid)
        # if cls.texts:
        #     cls.texts[lid] = cls(str, offset, lid)

        for index, elem in enumerate(cls.texts):
            if elem.lineid == lid:
                updated_elem = cls(str, offset, lid)
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
