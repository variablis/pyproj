import moderngl
import numpy as np
from PIL import Image
from pyrr import Matrix44
from pathlib import Path

from dc_point import Point
from df_math import clamp


# absolute path needed for pyinstaller
bundle_dir = Path(__file__).parent
path_to_sh = Path.cwd() / bundle_dir / "shaders"
path_to_msdf = Path.cwd() / bundle_dir / "msdf"


class Renderer:
    '''
    renderer class
    '''
    def __init__(self, ctx, reserve='4MB'):
        self.ctx = ctx


        # lines shaders
        self.prog = self.ctx.program(
            vertex_shader=(path_to_sh/'lines.vert').read_text(),
            geometry_shader=(path_to_sh/'lines.geom').read_text(),
            fragment_shader=(path_to_sh/'lines.frag').read_text()
        )
        self.vbo = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao = ctx.vertex_array(self.prog, [(self.vbo, '2f 4f', 'in_vert', 'in_color')])
        self.mvp1 = self.prog['mvp']
        self.wsize = self.prog['viewportsize']


        # circles shaders
        self.prog2 = self.ctx.program(
            vertex_shader=Path(path_to_sh/'circle.vert').read_text(),
            geometry_shader=Path(path_to_sh/'circle.geom').read_text(),
            fragment_shader=Path(path_to_sh/'circle.frag').read_text()
        )
        self.vbo2 = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao2 = ctx.vertex_array(self.prog2, [(self.vbo2, '2f 4f', 'in_vert', 'in_color')])
        self.mvp2 = self.prog2['mvp']
        self.zf2 = self.prog2['zoomfact']


        # grid shaders
        self.prog4 = self.ctx.program(
            vertex_shader=Path(path_to_sh/'grid.vert').read_text(),
            fragment_shader=Path(path_to_sh/'grid.frag').read_text(),
        )
        self.vbo4 = ctx.buffer(reserve='4MB', dynamic=True)
        self.vbo4.write(self.make_grid(1, 12))
        self.vao4 = ctx.vertex_array(self.prog4, [(self.vbo4, '2f 4f', 'in_vert', 'in_color')])
        self.mvp4 = self.prog4['mvp']
        self.grid_opacity = self.prog4['opacity']


        # msdf font shaders
        self.prog3 = self.ctx.program(
            vertex_shader=Path(path_to_sh/'text.vert').read_text(),
            fragment_shader=Path(path_to_sh/'text.frag').read_text()
        )
        self.vbo3 = ctx.buffer(reserve='4MB', dynamic=True)
        self.mvp3 = self.prog3['mvp']

        # font texture
        img = Image.open(path_to_msdf / "fonts.bmp").convert('RGB')
        self.tex0 = self.ctx.texture(img.size, 3, img.tobytes())
        self.s1 = self.ctx.sampler()
        self.s1.texture = self.tex0
        

    def make_grid(self, unit, size):
        gsize = unit*size
        gstep = unit

        u = np.linspace(-gsize, gsize, gsize*2 *gstep +1)

        color=np.array([0.0, 1, 0.3, .2])

        ys=np.column_stack((-gsize*np.ones_like(u), u, color * np.ones((len(u), 1)) ))
        ye=np.column_stack((gsize*np.ones_like(u), u, color * np.ones((len(u), 1)) ))
        hv=np.column_stack((ys,ye))

        xs=np.column_stack((u,-gsize*np.ones_like(u), color * np.ones((len(u), 1)) ))
        xe=np.column_stack((u,gsize*np.ones_like(u), color * np.ones((len(u), 1)) ))
        vv=np.column_stack((xs,xe))

        grid = np.concatenate((hv, vv))
        # # print( grid )

        grid = np.append(grid, [
            [0.0, 0.0, 0,1,0,1,
            0.0, 0.5, 0,1,0,1], 

            [0.0, 0.0, 1,0,0,1, 
            0.5, 0.0, 1,0,0,1]
        ])
        

        return grid.astype('f4').tobytes()
    

    def set_grid(self, unit):
        grid = self.make_grid(unit, 12)
        self.vbo4.clear()
        self.vbo4.write(grid)
        
    
    def text_render(self, pts):
        '''
        writes text vertex data into vertex buffer object, 
        calculates indices, renders new vertex array object
        '''
        if pts.size:
            self.s1.use()
            data = pts.astype('f4').tobytes()
            self.vbo3.orphan()
            self.vbo3.write(data)
     
            rectangle_pattern = np.array([0, 1, 2,  0, 2, 3], dtype='i4')
            indices = np.tile(rectangle_pattern, pts.size//16 ) + np.repeat(np.arange(0, pts.size//16  * 4, 4), 6)
            ibo = self.ctx.buffer(indices.tobytes()) 
            vao = self.ctx.vertex_array(self.prog3, [(self.vbo3, '2f 2f', 'in_vert', 'tex_coord')], ibo)
            vao.render()


    def line_render(self, pts):
        '''
        writes lines vertex data into vertex buffer object, 
        renders new vertex array object, 
        same line data passed to render end circles in geometry shader.
        reder order is important for depth sorting
        '''
        # render grid
        self.vao4.render(moderngl.LINES)

        # render lines
        data = pts.astype('f4').tobytes()
        self.vbo.clear()
        self.vbo.write(data)
        self.vao.render(moderngl.LINES)

        # render circles
        if pts.size:
            self.vbo2.clear()
            self.vbo2.write(data)
            self.vao2.render(moderngl.POINTS)


    def update_mvp(self, zf, pan):
        '''
        calculate projection matrix, camera matrix, pass data to shaders as uniform
        '''

        vw = self.ctx.viewport[2]
        vh = self.ctx.viewport[3]
        f5 = 512 *zf

        proj = Matrix44.orthogonal_projection(-vw/f5, vw/f5, vh/f5, -vh/f5, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            (pan.x, pan.y, -1.0),
            (pan.x, pan.y, 0.0),
            (0.0, -1.0, 0),
        )
        self.mvp4.write((proj * lookat).astype('f4'))
        self.mvp1.write((proj * lookat).astype('f4'))
        self.mvp2.write((proj * lookat).astype('f4'))
        self.mvp3.write((proj * lookat).astype('f4'))
        

        self.wsize.write(np.array([vw, vh]).astype('f4'))
        self.zf2.value = zf

        self.grid_opacity.write(np.array(clamp(zf,0,1)).astype('f4'))


    # clear line and text buffer
    def clear_buffers(self):
        self.vbo.clear()
        self.vbo2.clear()
        self.vbo3.clear()

    def clear_text_buffer(self):
        self.vbo3.clear()

    def clear_grid_buffer(self):
        self.vbo4.clear()

    def clear(self, color=(0.0, .1, 0.1, 0)):
        # self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.clear(*color)


class PanTool:
    '''
    pan calculation
    '''

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
            self.delta_x = (self.start_x-point.x) #* 2.0
            self.delta_y = (self.start_y-point.y) #* 2.0

    def stop_drag(self, point):
        if self.drag:
            self.dragging(point)
            self.total_x += self.delta_x
            self.total_y += self.delta_y
            self.delta_x = 0.0
            self.delta_y = 0.0
            self.drag = False

    @property
    def value(self):
        x = self.total_x + self.delta_x
        y = self.total_y + self.delta_y

        return Point(x,y)
