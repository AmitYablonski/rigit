import pymel.core as pm
# from PyQt5 import QtCore, QtGui, QtWidgets
from PySide2 import QtWidgets, QtCore, QtGui
# from sb_libs.latest.Qt import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui
import os
import sb_ui


# import paperMethods
# reload(paperMethods)


def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow()
    return wrapInstance(long(win), QtWidgets.QMainWindow)


class paperUI(QtWidgets.QDialog):
    def __init__(self):
        # todo: singleton
        parent = getMayaMainWindow()
        super(paperUI, self).__init__(parent=parent)
        # self.setStyleSheet("background-color: yellow");
        self.setStyleSheet(sb_ui.load_stylesheets(["main_window"]))

        # self.paperInst = paperMethods.Paper()

        self.setWindowTitle("paper")
        # self.paperInst = paper.paper()
        self.setEnabled(True)
        self.setToolTip("")
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.setMinimumHeight(1000)
        self.setMinimumWidth(400)

        # main vertical layout
        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(50, 50, 300, 1000))
        self.mainVerticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.mainVerticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

        # temp!
        # self.horizontalLayoutForLists = QtWidgets.QListWidget(self.horizontalLayoutWidget)
        # self.mainVerticalLayout.addWidget(self.horizontalLayoutForLists)

        # drawings list
        self.drawingsList = QtWidgets.QListWidget(self.verticalLayoutWidget)
        # draws_list = self.populateList()
        # draws_list = self.paperInst.getDrawingsProps()
        # os.listdir('Z:/ART/Projects/Live Action')
        project_list = self.populateProjectList()
        for project in project_list:
            self.drawingsList.addItem(project)
        self.mainVerticalLayout.addWidget(self.drawingsList)

        # todo: replace with a spacer
        # spacer label
        self.spacerLabel_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.spacerLabel_2.setText("")
        self.mainVerticalLayout.addWidget(self.spacerLabel_2)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.pushButtonRig = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButtonRig.clicked.connect(self.makeRig)
        self.horizontalLayout.addWidget(self.pushButtonRig)
        self.pushButtonRig.setText("Rig")

        self.pushButtonShading = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pushButtonShading.clicked.connect(self.makeShading)
        self.horizontalLayout.addWidget(self.pushButtonShading)
        self.pushButtonShading.setText("Shading")

        self.mainVerticalLayout.addLayout(self.horizontalLayout)

    @staticmethod
    def populateProjectList():
        props_dir = 'Z:/ART/Projects/Live Action'
        project_list = os.listdir(props_dir)
        return drawing_props

    def makeRig(self):
        draw = self.drawingsList.currentItem().text()
        # self.paperInst.create_rig(draw)

    def makeShading(self):
        draw = self.drawingsList.currentItem().text()
        # self.paperInst.create_shading(draw)


inst = paperUI()
inst.show()