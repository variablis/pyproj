import moderngl
import numpy as np
from PIL import Image
from pyrr import Matrix44
from pathlib import Path


# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_sh = Path.cwd() / bundle_dir / "shaders"
path_to_msdf = Path.cwd() / bundle_dir / "msdf"



class Renderer:
    def __init__(self, ctx, reserve='4MB'):
        self.ctx = ctx
        self.ppp=(0,0)
        self.zomf=1


        # lines shaders
        self.prog = self.ctx.program(
            vertex_shader=(path_to_sh/'lines.vert').read_text(),
            geometry_shader=(path_to_sh/'lines.geom').read_text(),
            fragment_shader=(path_to_sh/'lines.frag').read_text()
        )
        self.vbo = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao = ctx.vertex_array(self.prog, [(self.vbo, '2f 4f', 'in_vert', 'in_color')])
        self.mvp1 = self.prog['mvp']
        self.viewport = self.prog['viewportsize']


        # circles shaders
        self.prog2 = self.ctx.program(
            vertex_shader=Path(path_to_sh/'circle.vert').read_text(),
            geometry_shader=Path(path_to_sh/'circle.geom').read_text(),
            fragment_shader=Path(path_to_sh/'circle.frag').read_text()
        )
        self.vbo2 = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao2 = ctx.vertex_array(self.prog2, self.vbo2, 'in_vert', 'in_color')
        self.mvp2 = self.prog2['mvp']
        self.zf2 = self.prog2['zoomfact']


        # grid shaders
        self.prog4 = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform mat4 mvp;

                in vec2 in_vert;

                void main() {
                    gl_Position = mvp * vec4(in_vert, 0.0, 1.0);
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

        self.vbo4 = ctx.buffer(reserve='4MB', dynamic=True)
        self.vbo4.write(self.grid(1, 12))

        self.vao4 = ctx.vertex_array(self.prog4, self.vbo4, 'in_vert')
        self.mvp4 = self.prog4['mvp']
        self.grid_opacity = self.prog4['gridopacity']


        # msdf font shaders
        self.prog3 = self.ctx.program(
            vertex_shader=Path(path_to_sh/'text.vert').read_text(),
            fragment_shader=Path(path_to_sh/'text.frag').read_text()
        )
        self.vbo3 = ctx.buffer(reserve='4MB', dynamic=True)
        self.mvp3 = self.prog3['mvp']
        # self.zf3 = self.prog3['zoomfac']


        # font texture
        img = Image.open(path_to_msdf / "fonts.bmp").convert('RGB')
        self.tex0 = self.ctx.texture(img.size, 3, img.tobytes())
        self.s1 = self.ctx.sampler()
        self.s1.texture = self.tex0
        
        
        
    def grid(self, unit, size):
        gsize = unit*size
        gstep = unit

        u = np.linspace(-gsize, gsize, gsize*2 *gstep +1)
        # print(u)

        ys=np.column_stack((-gsize*np.ones_like(u), u))
        ye=np.column_stack((gsize*np.ones_like(u), u))
        hv=np.column_stack((ys,ye))

        xs=np.column_stack((u,-gsize*np.ones_like(u)))
        xe=np.column_stack((u,gsize*np.ones_like(u)))
        vv=np.column_stack((xs,xe))

        grid = np.concatenate((hv, vv))
        # print( grid )

        return grid.astype('f4').tobytes()
    
    def setGrid(self, unit):
        self.vbo4.clear()
        self.vbo4.write(self.grid(unit, 12))
        
    
    def textrender(self, pts):
        if pts.size:
            self.s1.use()
            data = pts.astype('f4').tobytes()
            self.vbo3.orphan()
            self.vbo3.write(data)
     
            rectangle_pattern = np.array([0, 1, 2,  0, 2, 3], dtype='i4')
            indices = np.tile(rectangle_pattern, pts.size//16 ) + np.repeat(np.arange(0, pts.size//16  * 4, 4), 6)
            ibo = self.ctx.buffer(indices.tobytes()) 
            vaox = self.ctx.vertex_array(self.prog3, [(self.vbo3, '2f 2f', 'in_vert', 'tex_coord')], ibo)
            vaox.render()

          

    # clear line and text buffer
    def bufcl(self):
        self.vbo.clear()
        self.vbo2.clear()
        self.vbo3.clear()

    def clearTextBuffer(self):
        self.vbo3.clear()

    def linerender(self, pts):
        data = pts.astype('f4').tobytes()
        self.vbo.orphan()
        self.vbo.write(data)
        self.vao.render(moderngl.LINES)

        # circle shader
        if pts.size:
            # print(pts.tolist())
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

        self.mvp1.write((proj * lookat).astype('f4'))
        self.mvp2.write((proj * lookat).astype('f4'))
        self.mvp3.write((proj * lookat).astype('f4'))
        self.mvp4.write((proj * lookat).astype('f4'))

        self.viewport.write(np.array([windw, windh]).astype('f4'))
        self.zf2.value =zf

        self.grid_opacity.write(np.array(self.clamp(zf,0,1)).astype('f4'))



    def zom(self, z):
        # self.prog['Zoo'].value = z
        self.zomf=z
        # pass
    
    def pan(self, pos):
        # self.prog['Pan'].value = pos
        self.ppp=pos
        # pass

    def clear(self, color=(0.0, .1, 0.1, 0)):
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
