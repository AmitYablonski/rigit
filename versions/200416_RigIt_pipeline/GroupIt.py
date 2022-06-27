from sb_libs.latest.Qt import QtWidgets, QtCore, QtGui, QtCompat
from pipeline.variants.pipeline_maya.utils import maya_qt
from pipeline.widgets import UserMassage
import sb_ui

from maya import cmds, mel
import pymel.core as pm
from functools import partial

from sb_libs.latest.Qt import QtWidgets, QtCore, QtGui
from pipeline.variants.pipeline_maya.utils import maya_qt
from pipeline.widgets import UserMassage
import sb_ui

instances = {}


class SingletonException(Exception):
    def __init__(self, class_):
        self.class_ = class_


def singleton(class_):
    def getinstance(*args, **kwargs):
        global instances

        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
            return instances[class_]
        else:
            UserMassage("Oops...", "This widget is already loaded")
            instances[class_].raise_()
            raise SingletonException(instances[class_])

    return getinstance


@singleton  # make sure that there can only be one instance of the widget. it's not mandatory!
class GroupIt_QT(QtWidgets.QMainWindow):
    """
    Qt MainWindow that will initial app.MainWindow using it's self.setCentralWidget()

    """

    def __init__(self, *args):

        self.presets = ['root', 'cns', 'npo', 'grp', 'fix', 'auto', 'trans', 'rot', 'scale']
        self.groupItWin()
        self.groupItWin_populate()

    def groupItWin(self):
        parent = maya_qt.maya_main_window()
        QtWidgets.QMainWindow.__init__(self, parent)

        self.setStyleSheet(sb_ui.load_stylesheets(["main_window"]))

        self.mainWidget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.mainWidget)

        self.layout.setContentsMargins(5, 5, 5, 5)  # window border
        self.layout.setSpacing(5)

        self.setCentralWidget(self.mainWidget)
        self.setWindowTitle("Group It!")

    def closeEvent(self, event):
        global instances
        event.accept()  # let the window close
        instances = {}
        self.setParent(None)
        self.deleteLater()

    def groupItWin_populate(self):
        # radio button
        radio_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(radio_layout)


        self.prefix_button = QtWidgets.QRadioButton("Add Prefix", self)  # radio
        self.suffix_button = QtWidgets.QRadioButton("Suffix", self)
        radio_layout.addWidget(self.prefix_button)
        radio_layout.addWidget(self.suffix_button)
        self.suffix_button.setChecked(True)

        # top layout
        split_layout = QtWidgets.QHBoxLayout()  # layout splits
        self.layout.addLayout(split_layout)
        # left layout
        left_layout = QtWidgets.QVBoxLayout()
        split_layout.addLayout(left_layout)
        # right layout
        right_layout = QtWidgets.QVBoxLayout()
        split_layout.addLayout(right_layout)

        button = QtWidgets.QPushButton('Group It')  # button
        left_layout.addWidget(button)
        button.setMaximumSize(400, 40)
        button.setMaximumSize(200, 40)
        button.setStyleSheet('background-color: rgb(1, 1, 1): color: rgb(0, 0, 0)')
        button.clicked.connect(self.groupIt)

        self.textLine = QtWidgets.QLineEdit()  # text field
        right_layout.addWidget(self.textLine)
        self.textLine.setText('_npo')

        # this needs to be added after textLine creation
        self.prefix_button.toggled.connect(self.radio_update)
        self.suffix_button.toggled.connect(self.radio_update)

        # buttom buttons
        buttons_layout = QtWidgets.QGridLayout()
        right_layout.addLayout(buttons_layout)
        self.presetButtons = []
        i = 0
        ii = 0
        for preset in self.presets:
            button = QtWidgets.QPushButton(preset)
            buttons_layout.addWidget(button, ii, i)
            button.clicked.connect(partial(self.changeText, preset))
            self.presetButtons.append([button, preset])
            i += 1
            if i > 2:
                ii += 1
                i = 0
        self.update_preset_buttons()

        # keep all buttons together on top
        left_layout.addStretch()
        right_layout.addStretch()

    def update_preset_buttons(self, *args):
        op = self.suffix_button.isChecked()
        for button, name in self.presetButtons:
            if op:
                preset = '_' + name
            else:
                preset = name + '_'
            button.clicked.connect(partial(self.changeText, name))
            button.setText(preset)

    def changeText(self, text, *args):
        op = self.suffix_button.isChecked()
        if op:
            text = '_' + text
        else:
            text = text + '_'
        self.textLine.setText(text)

    def radio_update(self):
        op = self.suffix_button.isChecked()
        text = self.textLine.text()
        if op:
            if text[-1] == '_':
                text = '_' + text[:-1]
        else:
            if text[0] == '_':
                text = text[1:] + '_'
        self.textLine.setText(text)
        self.update_preset_buttons()

    def groupIt(self, *args):
        op = self.suffix_button.isChecked()
        text = self.textLine.text()

        selection = pm.ls(sl=True)
        for sel in selection:
            parent1 = pm.listRelatives(sel, p=True)
            if parent1:
                grp = pm.group(em=True, p=parent1[0])
            else:
                grp = pm.group(em=True)
            if op:
                pm.rename(grp, sel + text)
            else:
                pm.rename(grp, text + sel)
            # todo use xform instead?
            pm.delete(pm.parentConstraint(sel, grp))
            pm.parent(sel, grp)

# start the widget
def start_app():
    return maya_qt.show(GroupIt_QT)

