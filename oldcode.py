    # def vertices():
#     x = np.linspace(-1.0, 1.0, 50)
#     y = np.random.rand(50) - 0.5
#     r = np.random.rand(50)
#     g = np.random.rand(50)
#     b = np.random.rand(50)
#     a = np.ones(50)
#     return np.dstack([x, y, r, g, b, a])
# verts = vertices()


def linecreate(self, x,y):
        global verts

        sw=self.size().width()/512/self.zfakt
        sh=self.size().height()/512/self.zfakt
        
        cx = (x*2 -1*sw+pan_tool.value[0])
        cy =(-y*2 +1*sh+pan_tool.value[1])

        # print('m ', x, -y )
        # print('c ', cx, cy )

        myvert = np.array([[0,0, 1,1,0,1],
                          [cx, cy, 1, random.uniform(0, 1) ,1,1]])
        verts = np.concatenate((verts, myvert), axis=0)

        # drawCircle(0.02, cx, cy)
        # print(verts)

    # def resizeEvent(self, event):
    #     print("resize")
    #     pass


        
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