import sys
import moderngl as mgl
import numpy as np
from PyQt5 import QtCore, QtWidgets
from pyrr import Matrix44, Vector3

class DesktopCharacter(QtWidgets.QOpenGLWidget):
    def __init__(self):
        super().__init__(flags=QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        
        # 窗口设置
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowTitle("Work Buddy")
        self.resize(300, 400)
        
        # 初始位置
        self.position = Vector3([100, 100, 0])
        self.drag_offset = None
        
        # 加载模型数据（示例用立方体代替，实际需替换为glTF模型）
        self.vertices = np.array([
            [-0.5, -0.5, 0.5], [0.5, -0.5, 0.5], [0.5, 0.5, 0.5], [-0.5, 0.5, 0.5],
            [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5]
        ], dtype='f4')
        
        self.indices = np.array([
            0,1,2, 2,3,0,   # 前面
            4,5,6, 6,7,4,   # 后面
            0,3,7, 7,4,0,   # 左面
            1,5,6, 6,2,1,   # 右面
            3,2,6, 6,7,3,   # 上面
            0,4,5, 5,1,0    # 底面
        ], dtype='i4')

    def initializeGL(self):
        self.ctx = mgl.create_context()
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 Mvp;
                in vec3 in_position;
                void main() {
                    gl_Position = Mvp * vec4(in_position, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                out vec4 color;
                void main() {
                    color = vec4(0.8, 0.2, 0.5, 0.7);
                }
            '''
        )
        
        self.vbo = self.ctx.buffer(self.vertices.tobytes())
        self.ibo = self.ctx.buffer(self.indices.tobytes())
        self.vao = self.ctx.vertex_array(
            self.prog,
            [(self.vbo, '3f', 'in_position')],
            self.ibo
        )
        
        # 启动动画定时器
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def paintGL(self):
        self.ctx.clear(color=(0,0,0,0))
        proj = Matrix44.orthogonal_projection(0, self.width(), 0, self.height(), -100, 100)
        model = Matrix44.from_translation(self.position)
        mvp = proj * model
        
        self.prog['Mvp'].write(mvp.astype('f4').tobytes())
        self.vao.render()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.drag_offset:
            self.position.x += event.pos().x() - self.drag_offset.x()
            self.position.y += self.height() - (event.pos().y() - self.drag_offset.y())
            self.drag_offset = event.pos()
            self.update()

    def animate(self):
        # 简单漂浮动画
        self.position.y += np.sin(QtCore.QTime.currentTime().msec() / 500) * 0.5
        self.update()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = DesktopCharacter()
    window.show()
    sys.exit(app.exec_())