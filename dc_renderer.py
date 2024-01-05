import moderngl
import numpy as np
from PIL import Image
from pyrr import Matrix44
from pathlib import Path

# import os
# import json
# import math
# from drw_classes import Point


# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_sh = Path.cwd() / bundle_dir / "shaders"
path_to_msdf = Path.cwd() / bundle_dir / "msdf"




class Renderer:
    def __init__(self, ctx, reserve='4MB'):

        self.ppp=(0,0)
        self.zomf=1

        self.ctx = ctx

        # LINES
        self.prog = self.ctx.program(
            vertex_shader=(path_to_sh/'hello.vert').read_text(),
            geometry_shader=(path_to_sh/'hello.geom').read_text(),
            fragment_shader=(path_to_sh/'hello.frag').read_text()
        )
        self.vbo = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao = ctx.vertex_array(self.prog, [(self.vbo, '2f 4f', 'in_vert', 'in_color')])
        self.mvp1 = self.prog['mvp']
        self.viewport = self.prog['viewportsize']
        # rectangle_pattern = np.array([0, 1, 2,  1, 2, 3], dtype='i4')
        # self.ibo2 = self.ctx.buffer(rectangle_pattern)
        # self.vao = ctx.vertex_array(self.prog, [(self.vbo, '2f 2f 2f 4f', 'in_vert', 'in_vert2', 'inluv', 'in_color')], self.ibo2)
        # print("Shader Program Log:", self.prog.log)

        # CIRCLES
        self.prog2 = self.ctx.program(
            # vertex_shader=Path(path_to_sh/'triangle.vert').read_text(),
            # fragment_shader=Path(path_to_sh/'triangle.frag').read_text()
            vertex_shader=Path(path_to_sh/'circle.vert').read_text(),
            geometry_shader=Path(path_to_sh/'circle.geom').read_text(),
            fragment_shader=Path(path_to_sh/'circle.frag').read_text()
        )
        self.vbo2 = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao2 = ctx.vertex_array(self.prog2, self.vbo2, 'in_vert','in_color')
        self.mvp2 = self.prog2['mvp']

        # GRID
        self.prog4 = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform mat4 mvp;

                in vec3 in_vert;

                void main() {
                    gl_Position = mvp * vec4(in_vert, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                uniform float gridopacity;
                out vec4 f_color;

                void main() {
                    f_color = vec4(0.0, 1, 0.3, .2*gridopacity);
                }
            ''',
        )

        
        # self.vbo4 = ctx.buffer(self.grid(100, 2500).astype('f4'))
        self.vbo4 = ctx.buffer(reserve='4MB', dynamic=True)
        self.vbo4.write(self.grid(100, 25*100).astype('f4'))

        # self.vbo4 = ctx.buffer(np.array([[[-1,-1],[0,0]],[[-1,-2],[1,1]]]).astype('f4'))
        self.vao4 = ctx.vertex_array(self.prog4, self.vbo4, 'in_vert')
        self.mvp4 = self.prog4['mvp']
        self.gridop = self.prog4['gridopacity']

        # MSDF TEXT
        # Shaders & Program
        self.prog3 = self.ctx.program(
            vertex_shader=Path(path_to_sh/'text.vert').read_text(),
            fragment_shader=Path(path_to_sh/'text.frag').read_text()
        )
        self.mvp3 = self.prog3['mvp']

        # vertices = np.array([ 
        #     -0.5, -0.5, 0.0, 1.0,
        #     0.5, -0.5, 1.0, 1.0, 
        #     0.5, 0.5,  1.0, 0.0, 
        #     -0.5, 0.5, 0.0, 0.0, 
        # ])
        # self.vbo3 = self.ctx.buffer(vertices.astype('f4'))
        # self.vbo3 = ctx.buffer(reserve='4MB', dynamic=True)

        # Put everything together

        # Indices pattern for a single rectangle
        # rectangle_pattern = np.array([0, 1, 2,  0, 2, 3], dtype='i4')

        # Repeat the pattern for the specified number of rectangles
        # indices = np.tile(rectangle_pattern, vertices.size//16 ) + np.repeat(np.arange(0, vertices.size//16  * 4, 4), 6)

        # n=5
        # rectangle_pattern += np.arange(n, dtype=np.uint32).reshape(n,1)
        # print(rectangle_pattern)
        
        # print(indices)

        # Indices are given to specify the order of drawing
        # indices = np.array([0,1,2, 0,2,3, 4,5,6, 4,6,7])
        # self.ibo = ctx.buffer(reserve='4MB', dynamic=True)
        # self.ibo = self.ctx.buffer(indices)
        # self.vao3 = self.ctx.vertex_array(self.prog3, [(self.vbo3, '2f 2f', 'in_vert', 'tex_coord')], self.ibo)


        # self.vao3 = ctx.vertex_array(self.prog2, self.vbo3, 'in_vert')
        # Texture

        img = Image.open(path_to_msdf / "fonts.bmp").convert('RGB')
        self.tex0 = self.ctx.texture(img.size, 3, img.tobytes())

        self.s1 = self.ctx.sampler()
        self.s1.texture = self.tex0

        # Opening the binary file in binary mode as rb(read binary)
        # f = open('msdf_gen/fonts.binfloat', mode="rb")
        # img = f.read()
        # f.close()
        # texture = ctx.texture((148,148), 4, img, dtype='f4')
        # texture.use()
            # text render
        
        self.vbo3 = ctx.buffer(reserve='4MB', dynamic=True)
    
    def grid(self, size, steps):
        u = np.repeat(np.linspace(-size, size, steps), 2)
        v = np.tile([-size, size], steps)
        w = np.zeros(steps * 2)
        return np.concatenate([np.dstack([u, v, w]), np.dstack([v, u, w])])
    
    def setGrid(self, step):
        newgrid = self.grid(100, step*100).astype('f4')
        self.vbo4.clear()
        self.vbo4.write(newgrid)

        # self.vao4.render(moderngl.LINES)
        
    
    def textrender(self, pts):
        # pass
        if pts.size:
            self.s1.use()
            # self.tex0.use()
            # print(pts)

            
            data = pts.astype('f4').tobytes()
            self.vbo3.orphan()
            self.vbo3.write(data)
            # vbo3 = self.ctx.buffer(data)

            # print(pts.size)
            rectangle_pattern = np.array([0, 1, 2,  0, 2, 3], dtype='i4')
            indices = np.tile(rectangle_pattern, pts.size//16 ) + np.repeat(np.arange(0, pts.size//16  * 4, 4), 6)
            # print(indices)
            
            # self.ibo.orphan()
            ibox = self.ctx.buffer(indices.tobytes()) 

            vaox = self.ctx.vertex_array(self.prog3, [(self.vbo3, '2f 2f', 'in_vert', 'tex_coord')], ibox)


            # self.vao3.transform(self.vbo2)

         
            vaox.render()

    # clear line and text buffer
    def bufcl(self):
        self.vbo.clear()
        self.vbo2.clear()

        self.vbo3.clear()

    def linerender(self, pts):

        # print(pts.tolist())
        
        data = pts.astype('f4').tobytes()
        # print(pts.astype('f4'))
        self.vbo.orphan()
        self.vbo.write(data)
        # self.ctx.line_width = 6.0
        # self.ctx.point_size = 5.0
        # self.vao.render(moderngl.LINES)
     
        self.vao.render(moderngl.LINES)
        # for i in range(0, len(pts)):
        #     self.vbo.orphan()
        #     self.vbo.write(data)

        #     self.vao.render(moderngl.TRIANGLE_STRIP, first=i*4, vertices=4)
        
        # print(pts)

        # circle shader test
        self.vbo2.orphan()
        self.vbo2.write(data)
        self.vao2.render(moderngl.POINTS)


        self.vao4.render(moderngl.LINES)


    def clamp(self, n, min, max): 
        if n < min: 
            return min
        elif n > max: 
            return max
        else: 
            return n 

    def updateMvp(self, zf):

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

        self.mvp1.write((proj * lookat).astype('f4'))
        self.mvp2.write((proj * lookat).astype('f4'))
        self.mvp3.write((proj * lookat).astype('f4'))
        self.mvp4.write((proj * lookat).astype('f4'))

        self.viewport.write(np.array([windw, windh]).astype('f4'))

        # print(zf)
        self.gridop.write(np.array(self.clamp(zf,0,1)).astype('f4'))



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

    def start_drag(self, point):
        self.start_x = point.x
        self.start_y = point.y
        self.drag = True

    def dragging(self, point):
        if self.drag:
            self.delta_x = (point.x - self.start_x) * 2.0
            self.delta_y = (point.y - self.start_y) * 2.0

    def stop_drag(self, point):
        if self.drag:
            self.dragging(point)
            self.total_x -= self.delta_x
            self.total_y += self.delta_y
            self.delta_x = 0.0
            self.delta_y = 0.0
            self.drag = False

    @property
    def value(self):
        return (self.total_x - self.delta_x, self.total_y + self.delta_y)
