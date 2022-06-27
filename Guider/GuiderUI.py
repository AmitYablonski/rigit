import pymel.core as pm
from PySide2 import QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
from maya import OpenMayaUI as omui
import GuiderMethods as Guider
import sb_ui
import importlib

if pm.about(version=True) == '2022':
    importlib.reload(Guider)
else:
    reload(Guider)


def getMayaMainWindow():
    win = omui.MQtUtil_mainWindow()
    ptr = wrapInstance(int(win), QtWidgets.QMainWindow)
    return ptr


class GuiderUI(QtWidgets.QDialog):
    def __init__(self):
        # todo make it close an existing win if found
        parent = getMayaMainWindow()
        super(GuiderUI, self).__init__(parent=parent)
        self.setWindowTitle("Guider")
        self.setStyleSheet(sb_ui.load_stylesheets(["main_window"]))
        self.buildUI()
        self.show()
        self.guiderInst = Guider.Guider()

    def buildUI(self):
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)

        # Create label - guide from selection
        createGuideLabelWidget = QtWidgets.QWidget()
        createGuideLabelLayout = QtWidgets.QHBoxLayout(createGuideLabelWidget)
        layout.addWidget(createGuideLabelWidget)

        createGuideLabel = QtWidgets.QLabel("Create guide from selection:")
        createGuideLabelLayout.addWidget(createGuideLabel)

        # Create guide from selection buttons
        btnWidget = QtWidgets.QWidget()
        btnLayout = QtWidgets.QHBoxLayout(btnWidget)
        layout.addWidget(btnWidget)

        createGuideBtn = QtWidgets.QPushButton("Create Guides")
        createGuideBtn.clicked.connect(self.createGuidesFromObjectsFunc)
        btnLayout.addWidget(createGuideBtn)

        self.jointCkbx = QtWidgets.QCheckBox("Joint")
        btnLayout.addWidget(self.jointCkbx)

        self.worldOriCkbx = QtWidgets.QCheckBox("world Ori")
        btnLayout.addWidget(self.worldOriCkbx)

        self.shapeCombx = QtWidgets.QComboBox()
        self.shapeCombx.addItems(["Circle", "Square", "Cross", "Cube", "Diamond"])
        btnLayout.addWidget(self.shapeCombx)

        # Add spacer

        spacerWidget = QtWidgets.QWidget()
        spacerLayout = QtWidgets.QHBoxLayout(spacerWidget)
        layout.addWidget(spacerWidget)

        # spacer = QtWidgets.QSpacerItem(4,4)
        # spacerLayout.addWidget(spacer)

        # Quick stuff
        quickRigWidget = QtWidgets.QWidget()
        quickRigLayout = QtWidgets.QHBoxLayout(quickRigWidget)
        layout.addWidget(quickRigWidget)

        createLocalBtn = QtWidgets.QPushButton("Create Local")
        createLocalBtn.clicked.connect(self.createLocalFunc)
        quickRigLayout.addWidget(createLocalBtn)

        quickRigBtn = QtWidgets.QPushButton("Quick Rig")
        quickRigBtn.clicked.connect(self.quickRigFunc)
        quickRigLayout.addWidget(quickRigBtn)

        # Close button
        closeWidget = QtWidgets.QWidget()
        closeLayout = QtWidgets.QHBoxLayout(closeWidget)
        layout.addWidget(closeWidget)

        closeBtn = QtWidgets.QPushButton("Close")
        closeBtn.clicked.connect(self.close)
        closeLayout.addWidget(closeBtn)

    def createLocalFunc(self):
        self.guiderInst.createLocal()

    def quickRigFunc(self):
        obj = pm.selected()
        self.guiderInst.quickRig(obj)

    def createGuidesFromObjectsFunc(self):
        shape = str(self.shapeCombx.currentText()).lower()
        jnt = False
        ori = False
        if "Checked" in str(self.jointCkbx.checkState()):
            jnt = True
        if "Checked" in str(self.worldOriCkbx.checkState()):
            ori = True

        objects = pm.ls(sl=True)
        self.guiderInst.createGuidesFromObjects(objects, jnt, ori, shape)
