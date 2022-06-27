from sb_libs.latest.Qt import QtWidgets, QtCore, QtGui, QtCompat
from pipeline.variants.pipeline_maya.utils import maya_qt
from pipeline.widgets import UserMassage
import sb_ui
import sys


def printAction(action):
    print(action.text())

def printAndSetCheck(action):
    tx = action.text()
    print tx
    action.setCheckable(1)
    if 'myTrash' in tx:
        ch = action.isChecked()
        print 'ch', ch
    else:
        action.setChecked(1)


app = maya_qt.maya_main_window()
w = QtWidgets.QMainWindow(app)

icons = QtWidgets.QFileIconProvider()
tb = w.addToolBar('MyToolbar')
ag = QtWidgets.QActionGroup(w)

ag.addAction(tb.addAction(icons.icon(icons.File), 'myFile'))
tb.addSeparator()
ag.addAction(tb.addAction(icons.icon(icons.Folder), 'myFolder'))
ag.addAction(tb.addAction(icons.icon(icons.File), 'first'))
ag.setExclusive(1)

tb.addSeparator()
tb.addAction(icons.icon(icons.Trashcan), 'myTrash')

tb.actionTriggered.connect(printAndSetCheck)
#tb.setIconSize(QSize)

w.resize(300, 300)
w.show()