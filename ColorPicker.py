# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Time: 2023/04/17
@Author: Wang Yang
"""
import sys, json
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMenuBar, QMenu, QAction, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QPen, QPainter, QColor, QPixmap
from PyQt5.QtCore import Qt, QRect


class ColorPickerApp(QMainWindow):
    # 初始化变量
    fullScreenImage = None
    captureImage = None
    isMousePressLeft = None
    beginPosition = None
    endPosition = None
    SelectColor = None

    # 创建 QPainter 对象
    painter = QPainter()

    def __init__(self):
        super().__init__()

        self.image_label = QLabel()

        self.pick_button = QPushButton("Pick Color")
        self.save_button = QPushButton("Save Color")

        self.pick_button.clicked.connect(self.pick_color)
        self.save_button.clicked.connect(self.save_color)

        menu_bar = QMenuBar(self)
        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)
        import_action = QAction("Import Image", self)
        import_action.triggered.connect(self.import_image)
        file_menu.addAction(import_action)

        self.setMenuBar(menu_bar)

        image_widget = QWidget()
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.pick_button)  # 将颜色选取按钮放置在图像下方
        image_layout.addWidget(self.save_button)  # 将保存颜色按钮放置在图像下方
        image_widget.setLayout(image_layout)

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.addWidget(image_widget)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)
        self.setWindowTitle("Color Picker")

        screen = QApplication.desktop().screenGeometry()
        self.setGeometry((screen.width() - 800) // 2, (screen.height() - 600) // 2, 800, 600)

        self.image = None
        self.color = None

    def import_image(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)
            self.fullScreenImage = pixmap
            self.image = pixmap.toImage()

    def mousePressEvent(self, event):
        if self.SelectColor is not None:
            """鼠标按下事件"""
            # 如果鼠标事件为左键，则记录起始鼠标光标相对于窗口的位置
            if event.button() == Qt.LeftButton:
                self.beginPosition = event.pos()
                self.isMousePressLeft = True
            # 如果鼠标事件为右键，如果已经截图了则重新开始截图，如果没有截图就退出
            if event.button() == Qt.RightButton:
                if self.captureImage is not None:
                    self.captureImage = None
                    self.update()  # 更新，会擦除之前的选框
                else:
                    self.close()

    def mouseMoveEvent(self, event):
        if self.SelectColor is not None:
            """鼠标移动事件"""
            if self.isMousePressLeft is True:
                self.endPosition = event.pos()
                self.update()

    def mouseReleaseEvent(self, event):
        if self.SelectColor is not None:
            """鼠标释放事件"""
            self.endPosition = event.pos()
            self.isMousePressLeft = False

    @staticmethod
    def getRectangle(beginPoint, endPoint):
        """获取矩形选框"""
        # 计算矩形宽和高
        rectWidth = int(abs(beginPoint.x() - endPoint.x()))
        rectHeight = int(abs(beginPoint.y() - endPoint.y()))
        # 计算矩形左上角 x 和 y
        rectTopleftX = beginPoint.x() if beginPoint.x() < endPoint.x() else endPoint.x()
        rectTopleftY = beginPoint.y() if beginPoint.y() < endPoint.y() else endPoint.y()
        # 构造一个以（x，y）为左上角，给定宽度和高度的矩形
        pickRect = QRect(rectTopleftX, rectTopleftY, rectWidth, rectHeight)
        # 调试日志
        # logging.info('开始坐标：%s,%s', beginPoint.x(),beginPoint.y())
        # logging.info('结束坐标：%s,%s', endPoint.x(), endPoint.y())
        return pickRect

    def paintBackgroundImage(self):
        """绘制背景图"""
        # 填充颜色，黑色半透明
        fillColor = QColor(0, 0, 0, 100)
        # 加载显示捕获的图片到窗口
        self.painter.drawPixmap(0, 0, self.image_label, self.fullScreenImage)
        # 填充颜色到给定的矩形
        self.painter.fillRect(self.fullScreenImage.rect(), fillColor)

    def paintSelectBox(self):
        """绘制选框"""
        # 画笔颜色，蓝色
        penColor = QColor(30, 150, 255)  # 画笔颜色
        # 设置画笔属性，蓝色、2px大小、实线
        self.painter.setPen(QPen(penColor, 2, Qt.SolidLine))
        if self.isMousePressLeft is True:
            pickRect = self.getRectangle(self.beginPosition, self.endPosition)  # 获得要截图的矩形框
            self.captureImage = self.fullScreenImage.copy(pickRect)  # 捕获截图矩形框内的图片
            self.painter.drawPixmap(pickRect.topLeft(), self.captureImage)  # 填充截图的图片
            self.painter.drawRect(pickRect)  # 绘制矩形边框

    def paintEvent(self, event):
        if self.SelectColor is not None:
            """接收绘制事件开始绘制"""
            self.painter.begin(self)  # 开始绘制
            self.paintBackgroundImage()  # 绘制背景
            self.paintSelectBox()  # 绘制选框
            self.painter.end()  # 结束绘制

    def pick_color(self):
        if self.image is not None:
            self.SelectColor = True


    # def pick_color(self):
    #     if self.image is not None:
    #         rect = self.image_label.geometry()
    #         rect.moveLeft(self.image_label.pos().x())
    #         rect.moveTop(self.image_label.pos().y())
    #
    #         # 添加鼠标点击事件处理函数
    #         pick_rect = QRect(rect.left(), rect.top(), rect.width(), rect.height())
    #         picker_image = self.image.copy(pick_rect)
    #
    #         # 获取框选区域的RGB值
    #         min_r, max_r = 255, 0
    #         min_g, max_g = 255, 0
    #         min_b, max_b = 255, 0
    #
    #         for x in range(picker_image.width()):
    #             for y in range(picker_image.height()):
    #                 color = picker_image.pixelColor(x, y)
    #                 r, g, b, _ = color.getRgb()
    #                 min_r = min(min_r, r)
    #                 max_r = max(max_r, r)
    #                 min_g = min(min_g, g)
    #                 max_g = max(max_g, g)
    #                 min_b = min(min_b, b)
    #                 max_b = max(max_b, b)
    #
    #         print("RGB值的上下限：")
    #         print("R: [{} - {}]".format(min_r, max_r))
    #         print("G: [{} - {}]".format(min_g, max_g))
    #         print("B: [{} - {}]".format(min_b, max_b))

    def save_color(self):
        if self.color is not None:
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.AnyFile)
            file_dialog.setNameFilter("JSON Files (*.json)")
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                color_dict = {
                    'red': (self.color.red(), self.color.red()),
                    'green': (self.color.green(), self.color.green()),
                    'blue': (self.color.blue(), self.color.blue())
                }
                with open(file_path, 'w') as f:
                    json.dump(color_dict, f)
                print("Color saved successfully.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ColorPickerApp()
    window.show()
    sys.exit(app.exec_())
