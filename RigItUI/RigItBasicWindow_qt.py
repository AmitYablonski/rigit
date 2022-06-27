from sb_libs.latest.Qt import QtWidgets, QtCore, QtGui, QtCompat
from pipeline.variants.pipeline_maya.utils import maya_qt
from pipeline.widgets import UserMassage
import sb_ui

from maya import cmds, mel
import pymel.core as pm
from functools import partial


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
class ToolName(QtWidgets.QMainWindow):
    """
    Qt MainWindow that will initial app.MainWindow using it's self.setCentralWidget()

    """
    def __init__(self, *args):

        self.title = 'Tool Title'
        self.feedbackName = self.title

        self.winBase()
        self.populateUI()

        self.defaultFeedback()

    def winBase(self):
        parent = maya_qt.maya_main_window()
        QtWidgets.QMainWindow.__init__(self, parent)

        self.setStyleSheet(sb_ui.load_stylesheets(["main_window"]))

        # ---- Top Layout ---- #
        self.mainWidget = QtWidgets.QWidget()
        self.topLayout = QtWidgets.QVBoxLayout(self.mainWidget)

        self.topLayout.setContentsMargins(5, 5, 5, 5)  # window border
        self.topLayout.setSpacing(5)

        # ---- Main Layout ---- #
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.topLayout.addLayout(self.mainLayout)

        # ---- feedback ---- #
        self.feedback = QtWidgets.QLineEdit()
        self.feedback.setReadOnly(True)
        self.topLayout.addWidget(self.feedback)

        self.setCentralWidget(self.mainWidget)
        self.setWindowTitle(self.title)

    def closeEvent(self, event):
        global instances
        event.accept()  # let the window close
        instances = {}
        self.setParent(None)
        self.deleteLater()

    def populateUI(self):
        # ---- pop layout ---- #
        label = QtWidgets.QLabel('This is where you should build UI')
        self.mainLayout.addWidget(label)

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

# start the widget
def start_app():
    return maya_qt.show(ToolName)



