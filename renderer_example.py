# renderer_example.py

import moderngl

import os
import struct
from PIL import Image
import numpy as np
import json


class HelloWorld2D:
    def __init__(self, ctx, reserve='4MB'):
        self.ctx = ctx
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform vec2 Pan;
                uniform float zz;
                uniform float Zoo;
                uniform vec2 mp;

                in vec2 in_vert;
                in vec4 in_color;

                out vec4 v_color;

                void main() {

                    vec3 cameraPos = vec3(Pan.x, Pan.y, 0.5f); 

                    vec3 eye = vec3(0,0, -3);
                    vec3 center = vec3(0,0, 0.0);
                    vec3 up = vec3(0.0, 1.0, 0.0);

                    vec3 _f = normalize(center - eye);
                    vec3 _r = normalize(cross(up, _f));
                    vec3 u = cross(_f, _r);

                    mat4 view = mat4(
                        vec4(_r, -dot(_r, eye)),
                        vec4(u, -dot(u, eye)),
                        vec4(-_f, -dot(_f, eye)),
                        vec4(-Pan, 0.0, 1.0)
                    );

                    float r,l,t,b,f,n=0;

                    l=-1;
                    r=1;
                    b=-1;
                    t=1;

                    n=-1;
                    f=1;
                   
                    mat4 proj = mat4(
                       vec4(2/(r-l), 0, 0, -(r+l)/(r-l)),
                       vec4(0, 2/(t-b), 0, -(t+b)/(t-b)),
                       vec4(0, 0, -2/(f-n), -(f+n)/(f-n)),
                       vec4(0, 0, 0, 1.0)
                    );

                     //   mat4 proj = mat4(
                     //       vec4(2.0 / (r - l), 0.0, 0.0, 0.0),
                       //     vec4(0.0, 2.0 / (t - b), 0.0, 0.0),
                         //   vec4(0.0, 0.0, -2.0 / (f - n), 0.0),
                          //  vec4(-(r + l) / (r - l), -(t + b) / (t - b), -(f + n) / (f - n), 1.0)
                        //);

                    // Pass the color to the fragment shader
                    v_color = in_color * zz;

                    // Set the transformed position
                    gl_Position = proj* view * vec4(in_vert, 0.0, 1.0);
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

                in vec2 in_pos;
                in vec2 in_vert;
                in vec2 tex_coord;

                out vec2 uvCoord;

                void main() {
                    gl_Position = vec4(in_pos+in_vert, 0.0, 1.0);
                    uvCoord = tex_coord;
                }

            ''',
            fragment_shader='''
                #version 330

                uniform sampler2D tex;

                in vec2 uvCoord;
                out vec4 outColor;

                float median(float r, float g, float b) {
                    return max(min(r, g), min(max(r, g), b));
                }

                float screenPxRange(sampler2D tex) {
                    vec2 unitRange = vec2(6.0)/vec2(textureSize(tex, 0));
                    vec2 screenTexSize = vec2(1.0)/fwidth(uvCoord);
                    return max(0.5*dot(unitRange, screenTexSize), 1.0);
                }

                void main() {
                
                    //vec2 inverteduvCoord = vec2(uvCoord.s, 1.0 - uvCoord.t);

                    vec4 texel = texture(tex, uvCoord);
                    

                    float pxRange; 
                    pxRange = screenPxRange(tex);

                    float dist = median(texel.r, texel.g, texel.b);

                    float pxDist = pxRange * (dist - 0.5);
                    float opacity = clamp(pxDist + 0.5, 0.0, 1.0);

                    outColor = vec4(0.3, 0.8, 0.8, opacity*texel.a);
                }

            ''',
        )

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




        # Buffer
        # xx=np.array([
        #     -0.5, -0.5, 0.0, 1.0,  # Vertex 0, s,t
        #     0.5, -0.5, 1.0, 1.0,   # Vertex 1
        #     0.5, 0.5,  1.0, 0.0,   # Vertex 2
        #     -0.5, 0.5, 0.0, 0.0,   # Vertex 3

        #     0.5, -0.5, 0.0, 1.0,  # Vertex 4, s,t
        #     1.5, -0.5, 1.0, 1.0,   # Vertex 5
        #     1.5, 0.5,  1.0, 0.0,   # Vertex 6
        #     0.5, 0.5, 0.0, 0.0,   # Vertex 7
        # ])

        vertices=np.array([ txt2vtx('12734.98234cm') ])
        self.vbo3 = ctx.buffer(vertices.astype('f4'))

        # print(xx)


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
        texture = ctx.texture(img.size, 3, img.tobytes())
        texture.use()


        # Opening the binary file in binary mode as rb(read binary)
        # f = open('msdf_gen/fonts.binfloat', mode="rb")
        # img = f.read()
        # f.close()
        # texture = ctx.texture((148,148), 4, img, dtype='f4')
        # texture.use()


        


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
        # for i in range(0, 2):
            # self.vao3.render(moderngl.TRIANGLE_FAN, first=i*4, vertices=4)
        
        # Render all instances of the square
        self.vao3.render()


    def dodo(self, pts):
        data2 = pts.astype('f4').tobytes()
        # self.vbo2.orphan()
        

        for i in range(0, len(pts)):
            self.vbo2.orphan()
            self.vbo2.write(data2)

            self.vao2.render(moderngl.TRIANGLE_FAN, first=i*6, vertices=6)

        # print(len(pts))

    def zom(self, z):
        self.prog['Zoo'].value = z
        # pass

    def mp(self, po):
        # self.prog['mp'].value = po
        pass
    
    def pan(self, pos):
        self.prog['Pan'].value = pos
        # pass

    def clear(self, color=(0.0, .1, 0.1, 0)):
        # fbo1 = self.ctx.framebuffer(self.ctx.renderbuffer((512, 512), samples=4))
        # fbo1.use()
        
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)

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
