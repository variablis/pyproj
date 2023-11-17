# renderer_example.py

import moderngl

import os
import struct
from PIL import Image
import numpy as np


# You can read each image separately and append the images to a list. Finally convert the list to an numpy.array.
# In the following snippet imageList is a list of filenames and width and height is the size of an individual image (the images must all be the same size):

def createTextureArray(imageList, width, height):

    # depth = len(imageList)

    dataList = []
    for filename in imageList:
        
        image = Image.open(filename)
        if width != image.size[0] or height != image.size[1]:
            raise ValueError(f"image size mismatch: {image.size[0]}x{image.size[1]}")
        
        dataList.append(list(image.getdata()))

    return np.array(dataList, np.uint8)

    # imageArrayData = np.array(dataList, np.uint8)

    # components = 4 # 4 for RGBA, 3 for RGB
    # context.texture_array((width, height, depth), components, imageArrayData)

# print(createTextureArray(['a.png', 'b.png', 'c.png'], 96,96))

class HelloWorld2D:
    def __init__(self, ctx, reserve='4MB'):
        self.ctx = ctx
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform vec2 Pan;
                uniform float zz;

                in vec2 in_vert;
                in vec4 in_color;

                out vec4 v_color;

                void main() {
                    v_color = in_color*zz;
                    gl_Position = vec4(in_vert - Pan, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                in vec4 v_color;

                out vec4 f_color;

                void main() {
                    f_color = v_color;
                }
            ''',
        )

        self.vbo = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao = ctx.vertex_array(self.prog, self.vbo, 'in_vert', 'in_color')

        self.vbo2 = ctx.buffer(reserve='4MB', dynamic=True)
        self.vao2 = ctx.vertex_array(self.prog, self.vbo2, 'in_vert', 'in_color')


        # Shaders & Program

        self.prog2 = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec2 in_vert;
                in vec3 in_text;

                out vec3 v_text;

                void main() {
                    v_text = in_text;
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                uniform sampler2DArray Texture;

                in vec3 v_text;

                out vec4 color;

                void main() {
                    color = texture(Texture, v_text);
                }
            ''',
        )


        # Buffer
        self.vbo3 = ctx.buffer(struct.pack(
            '12f',
            1.0, 0.0, 0.5, 1.0,
            -0.5, 0.86, 1.0, 0.0,
            -0.5, -0.86, 0.0, 0.0,
        ))

        # Put everything together

        

        # Texture

        # img = Image.open(os.path.join(os.path.dirname(__file__), 'msdf.png'))
        # texture = ctx.texture(img.size, 3, img.tobytes())
        # texture.use()

        # texture_arr = ctx.texture_array((96, 96, 3), 3, createTextureArray(['a.png', 'b.png', 'c.png'], 96,96))
        # # texture.use()

        images = [
            Image.new('RGB', (32, 32), 'red'),
            Image.new('RGB', (32, 32), color=(33,255,0) ),
            Image.new('RGB', (32, 32), 'blue'),
        ]

        merged = b''.join(img.tobytes() for img in images)

        texture_arr = ctx.texture_array((32, 32 ,3), 3, merged)
        self.prog2['Texture']=1
        texture_arr.use(location=1)

        # first_texture.use(location=0)
        # second_texture.use(location=1


        self.vao3 = ctx.vertex_array(self.prog2, self.vbo3, 'in_vert', 'in_text')


    def chcol (self,col):
        self.prog['zz'].value=col

    def kuku(self, pts):
        # print('press')
        
        data = pts.astype('f4').tobytes()
        self.vbo.orphan()
        self.vbo.write(data)
        self.ctx.line_width = 2
        self.ctx.point_size = 5.0
        self.vao.render(moderngl.LINE_STRIP, vertices=len(data) // 2)
       
        # print('here')
        self.vao3.render(moderngl.TRIANGLE_FAN, vertices=3)

    def dodo(self, pts):
        data2 = pts.astype('f4').tobytes()
        # self.vbo2.orphan()
        

        for i in range(0, len(pts)):
            self.vbo2.orphan()
            self.vbo2.write(data2)
            self.vao2.render(moderngl.TRIANGLE_FAN, first=i*6, vertices=6)

        # print(len(pts))
        
    def pan(self, pos):
        self.prog['Pan'].value = pos

    def clear(self, color=(0.0, .1, 0, 0)):
        self.ctx.clear(*color)

    def plot(self, points, type='line'):
        data = points.astype('f4').tobytes()
        self.vbo.orphan()
        self.vbo.write(data)
        if type == 'line':
            self.ctx.line_width = 1
            self.vao.render(moderngl.LINE_STRIP, vertices=len(data) // 24)
        if type == 'points':
            self.ctx.point_size = 3.0
            self.vao.render(moderngl.POINTS, vertices=len(data) // 24)

    def mcoord(self, x,y):
        # print(x,y)
        pass



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
