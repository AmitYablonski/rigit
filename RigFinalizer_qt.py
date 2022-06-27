from sb_libs.latest.Qt import QtWidgets, QtCore, QtGui, QtCompat
from pipeline.variants.pipeline_maya.utils import maya_qt
from pipeline.widgets import UserMassage
import sb_ui

from maya import cmds, mel
import pymel.core as pm
from functools import partial

import fnmatch
import UI_modules as uim
import RigItMethodsUI as rim
import traceback
import FinalizerFixer
import generalMayaPrints as gmp
import generalMayaTools as gmt

reload(FinalizerFixer)
reload(gmp)
reload(gmt)


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
class RigFinalizer(QtWidgets.QMainWindow):
    """
    Qt MainWindow that will initial app.MainWindow using it's self.setCentralWidget()

    """
    def __init__(self, *args):

        self.title = 'Rig Finalizer'
        self.feedbackName = self.title

        self.winBase()
        self.populateUI()

        self.defaultFeedback()

    def winBase(self):
        parent = maya_qt.maya_main_window()
        QtWidgets.QMainWindow.__init__(self, parent)

        self.setStyleSheet(sb_ui.load_stylesheets(["main_window"]))

        # ---- Top Layout ---- #
        self.main_widget = QtWidgets.QWidget()
        self.top_layout = QtWidgets.QVBoxLayout(self.main_widget)

        self.top_layout.setContentsMargins(5, 5, 5, 5)  # window border
        self.top_layout.setSpacing(5)

        # ---- Main Layout ---- #
        self.main_layout = QtWidgets.QHBoxLayout()
        self.top_layout.addLayout(self.main_layout)

        # ---- feedback ---- #
        self.feedback = QtWidgets.QLineEdit()
        self.feedback.setReadOnly(True)
        self.top_layout.addWidget(self.feedback)

        self.setCentralWidget(self.main_widget)
        self.setWindowTitle(self.title)

    def closeEvent(self, event):
        global instances
        event.accept()  # let the window close
        instances = {}
        self.setParent(None)
        self.deleteLater()

    def populateUI(self):
        # ---- tabs layout ---- #
        self.tabs_layout = QtWidgets.QTabWidget()
        self.tabs_layout.addTab(CheckList(), "Check List")
        #self.main_layout.addWidget(self.tabs_layout)

        #self.checklist_layout = QtWidgets.QHBoxLayout()

        # ---- The log ---- #
        self.log = QtWidgets.QPlainTextEdit()

        self.main_layout.addWidget(self.log)

    def greenFeedback(self, text):
        self.printFeedback(text, 'green')

    def orangeFeedback(self, text):
        self.printFeedback(text, 'orange')

    def printFeedback(self, text, color=''):
        error = ' // %s : %s' % (self.feedbackName, text)
        print(error)
        fColor = 'red'
        if color:
            fColor = color
        self.changeFeedback(error, fColor)

    def defaultFeedback(self):
        self.changeFeedback('// %s' % self.feedbackName)

    def changeFeedback(self, messege, error=''):
        # set messege
        self.feedback.setText(messege)
        # set color
        # if too bright, use color: (.25, .25, .25)
        self.feedback.setStyleSheet("""QLineEdit { background-color: black; color: white) }""")
        if error == "red":
            self.feedback.setStyleSheet("""QLineEdit { background-color: red; color: white }""")
        if error == "green":
            self.feedback.setStyleSheet("""QLineEdit { background-color: green; color: white }""")
        if error == 'orange':
            self.feedback.setStyleSheet("""QLineEdit { background-color: orange; color: black }""")
        if error == 'yellow':
            self.feedback.setStyleSheet("""QLineEdit { background-color: yellow; color: black }""")

class CheckList(QtWidgets.QWidget):
    def __init__(self, parent=None):
        #QtWidgets.QMainWindow.__init__(self, parent)
        QtWidgets.QWidget.__init__(self, parent)
        fileNameLabel = QtWidgets.QLabel("File Name:")
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(fileNameLabel)
        mainLayout.addStretch(1)
        #self.setLayout(mainLayout)

# start the widget
def start_app():
    return maya_qt.show(RigFinalizer)



