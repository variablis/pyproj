# renderer_example.py

import moderngl

import os
from PIL import Image
import numpy as np
import json
from pathlib import Path

from pyrr import Matrix44
import math


def grid(size, steps):
    u = np.repeat(np.linspace(-size, size, steps), 2)
    v = np.tile([-size, size], steps)
    w = np.zeros(steps * 2)
    return np.concatenate([np.dstack([u, v, w]), np.dstack([v, u, w])])


class HelloWorld2D:
    def __init__(self, ctx, reserve='4MB'):

        self.ppp=(0,0)
        self.zomf=1

        self.ctx = ctx

        self.prog = self.ctx.program(
            vertex_shader=Path('shaders/hello.vert').read_text(),
            fragment_shader=Path('shaders/hello.frag').read_text()
        )

        self.mvp1 = self.prog['Mvp']
        self.vbo = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao = ctx.vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')

        self.vbo2 = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao2 = ctx.vertex_array(self.prog, self.vbo2, 'in_vert', 'in_color')

        self.prog4 = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform mat4 Mvp;

                in vec3 in_vert;

                void main() {
                    gl_Position = Mvp * vec4(in_vert, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                out vec4 f_color;

                void main() {
                    f_color = vec4(0.0, 1, 0.3, .2);
                }
            ''',
        )

        self.mvp = self.prog4['Mvp']
        self.vbo4 = ctx.buffer(grid(100, 2500).astype('f4'))
        # self.vbo4 = ctx.buffer(np.array([[[-1,-1],[0,0]],[[-1,-2],[1,1]]]).astype('f4'))
        self.vao4 = ctx.vertex_array(self.prog4, self.vbo4, 'in_vert')

        # Shaders & Program

        self.prog2 = self.ctx.program(
            vertex_shader=Path('shaders/text.vert').read_text(),
            fragment_shader=Path('shaders/text.frag').read_text()
        )

    def distancetext(self, stri):
        # Opening JSON file
        f = open('msdf_gen/fonts.json')
        # returns JSON object as # a dictionary
        fdata = json.load(f)
        # Closing file
        f.close()

        def txt2vtx(str):
            wi = he = 256
            arr=[]
            for i,s in enumerate(str):
                for glyph in fdata.get("glyphs", []):
                    if glyph.get("unicode") == ord(s):
                        dd = glyph.get("atlasBounds", {})
                        pb = glyph.get("planeBounds", {})

                        xl=pb['left']
                        xr=pb['right']
                        yt=pb['top']
                        yb=pb['bottom']

                        sl=dd['left']/wi
                        sr=dd['right']/wi
                        tt=dd['top']/he
                        tb=dd['bottom']/he
            
                        sc = 0.07

                        ob = [
                            # -0.5, -0.5, 0.0, 1.0,
                            # 0.5, -0.5, 1.0, 1.0, 
                            # 0.5, 0.5,  1.0, 0.0, 
                            # -0.5, 0.5, 0.0, 0.0, 

                            (xl+i*.5)*sc, yb*sc, sl, 1-tb,
                            (xr+i*.5)*sc, yb*sc, sr, 1-tb, 
                            (xr+i*.5)*sc, yt*sc, sr, 1-tt, 
                            (xl+i*.5)*sc, yt*sc, sl, 1-tt, 
                        ]

                        # print(ob)
                        # print(ord(s))

                        arr.append(ob)
            return arr

        vertices = np.array([ txt2vtx(stri) ])
        
        self.vbo3 = self.ctx.buffer(vertices.astype('f4'))

        # Put everything together

        # Indices pattern for a single rectangle
        rectangle_pattern = np.array([0, 1, 2,  0, 2, 3], dtype='i4')

        # Repeat the pattern for the specified number of rectangles
        indices = np.tile(rectangle_pattern, vertices.size//16 ) + np.repeat(np.arange(0, vertices.size//16  * 4, 4), 6)
        # print(indices)

        # Indices are given to specify the order of drawing
        # indices = np.array([0,1,2, 0,2,3, 4,5,6, 4,6,7])
        self.ibo = self.ctx.buffer(indices.astype('i4'))


        self.vao3 = self.ctx.vertex_array(self.prog2, [(self.vbo3, '2f 2f', 'in_vert', 'tex_coord')], self.ibo)


        # self.vao3 = ctx.vertex_array(self.prog2, self.vbo3, 'in_vert')

        # Texture

        img = Image.open(os.path.join(os.path.dirname(__file__), 'msdf_gen/fonts.bmp')).convert('RGB')
        texture = self.ctx.texture(img.size, 3, img.tobytes())
        texture.use()

        # Opening the binary file in binary mode as rb(read binary)
        # f = open('msdf_gen/fonts.binfloat', mode="rb")
        # img = f.read()
        # f.close()
        # texture = ctx.texture((148,148), 4, img, dtype='f4')
        # texture.use()
        self.vao3.render()


    def linerender(self, pts, zf):
        
        data = pts.astype('f4').tobytes()
        self.vbo.orphan()
        self.vbo.write(data)
        self.ctx.line_width = 4
        # self.ctx.point_size = 5.0
        self.vao.render(moderngl.LINES)
        
        # print(date)


        windw=self.ctx.viewport[2]
        windh=self.ctx.viewport[3]
        f5=512*zf #self.zomf

        proj = Matrix44.orthogonal_projection(-windw/f5, windw/f5, windh/f5, -windh/f5, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            (self.ppp[0], self.ppp[1], -1.0),
            (self.ppp[0], self.ppp[1], 0.0),
            (0.0, -1.0, 0),
        )
        # print(self.zomf)

        self.mvp.write((proj * lookat).astype('f4'))
        self.mvp1.write((proj * lookat).astype('f4'))
        self.vao4.render(moderngl.LINES)

    def circl(self, pts):
        data2 = pts.astype('f4').tobytes()
        # self.vbo2.orphan()

        for i in range(0, len(pts)):
            self.vbo2.orphan()
            self.vbo2.write(data2)

            self.vao2.render(moderngl.TRIANGLE_FAN, first=i*6, vertices=6)

        # print(len(pts))

    def zom(self, z):
        # self.prog['Zoo'].value = z
        self.zomf=z
        # pass

    def mp(self, po):
        # self.prog['mp'].value = po
        pass
    
    def pan(self, pos):
        # self.prog['Pan'].value = pos
        self.ppp=pos
        # pass

    def clear(self, color=(0.0, .1, 0.1, 0)):
        # fbo1 = self.ctx.framebuffer(self.ctx.renderbuffer((512, 512), samples=4))
        # fbo1.use()
        
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)

        self.ctx.clear(*color)


class PanTool:
    def __init__(self):
        self.total_x = 0.0
        self.total_y = 0.0
        self.start_x = 0.0
        self.start_y = 0.0
        self.delta_x = 0.0
        self.delta_y = 0.0
        self.drag = False

    def start_drag(self, x, y):
        self.start_x = x
        self.start_y = y
        self.drag = True

    def dragging(self, x, y):
        if self.drag:
            self.delta_x = (x - self.start_x) * 2.0
            self.delta_y = (y - self.start_y) * 2.0

    def stop_drag(self, x, y):
        if self.drag:
            self.dragging(x, y)
            self.total_x -= self.delta_x
            self.total_y += self.delta_y
            self.delta_x = 0.0
            self.delta_y = 0.0
            self.drag = False

    @property
    def value(self):
        return (self.total_x - self.delta_x, self.total_y + self.delta_y)
