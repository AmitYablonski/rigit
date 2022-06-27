from maya import cmds, mel
import pymel.core as pm
from functools import partial


class ToolName:
    def __init__(self):
        self.widgets = {}
        self.feedbackName = 'Tool Title'
        topLay, mainLay = self.winBase('ToolName', self.feedbackName)
        self.populateUI(mainLay)
        self.defaultFeedback()

    def populateUI(self, mainLay):
        pm.separator(h=7, p=mainLay)
        pm.text(l='This is where you place stuff', font='boldLabelFont', p=mainLay)
        pm.text(l='Imean.. under the mainLay', p=mainLay)
        pm.separator(h=7, p=mainLay)

    def winBase(self, name, title):
        winName = name + "_window"
        mainLay = "mainLay"
        topLay = "topLay"
        if cmds.window(winName, exists=True):
            cmds.deleteUI(winName)
        self.widgets['window'] = cmds.window(winName, title=title, sizeable=1, rtf=True)
        self.widgets[topLay] = cmds.columnLayout(adj=True)
        self.widgets[mainLay] = cmds.columnLayout(adj=True)

        self.widgets["feedback"] = cmds.textField(tx="", editable=False, p=self.widgets[topLay])
        cmds.showWindow()
        return self.widgets[topLay], self.widgets[mainLay]

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
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.7, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedback"], e=True, bgc=bg, tx=messege)

