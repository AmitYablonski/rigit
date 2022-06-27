from maya import cmds, mel
import pymel.core as pm
from functools import partial
import UI_modules as uim
import RigItMethodsUI as rim
reload(uim)
reload(rim)


class ToolName:
    def __init__(self, par='', scriptIt=False):
        self.widgets = {}
        self.feedbackName = 'Tool Feedback call'
        mainLay = self.winBase('Tool Title', self.feedbackName, par)
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def execute(self, *args):
        self.printFeedback('Execute pressed', color='green')
        return

    def scriptIt(self, *args):
        script = 'Script Will be shown here'
        self.printFeedback('Script pressed', color='red')
        rim.showScript(script)
        return

    def populateUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)
        pm.text(l=self.feedbackName, font='boldLabelFont', p=mainLay)
        pm.separator(h=7, p=mainLay)
        pm.text(l='Place to place stuff:', p=mainLay)
        self.widgets['objField'] = uim.selectAndAddToField(self, mainLay, 'Select', objType='transform')
        self.widgets['attrField'] = uim.textAndField(mainLay, 'Text example: ', 'new string')

        # buttons
        cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
        cmds.button(l='Execute', h=28, c=self.execute)
        if scriptIt:
            cmds.button(l='Script it', w=100, c=self.scriptIt)
        else:
            pm.separator(w=100, style='none')

    def winBase(self, name, title, par):
        winName = name + "_window"
        mainLay = "mainLay"
        asWindow = True
        if par:
            print(' // %s - creating Layout under parent' % self.feedbackName)
            asWindow = False
        if asWindow:
            if cmds.window(winName, exists=True):
                cmds.deleteUI(winName)
            self.widgets[winName] = cmds.window(winName, title=title, sizeable=1, rtf=True)
            form = pm.formLayout()
        else:
            form = pm.formLayout(title, p=par)
        # form and main layout
        self.widgets['topForm'] = form
        self.widgets[mainLay] = pm.columnLayout(adj=True)
        mLay = self.widgets[mainLay]
        pm.formLayout(form, e=True, af=((mLay, 'top', 0), (mLay, 'left', 0),
                                        (mLay, 'right', 0), (mLay, 'bottom', 30)))

        # feedback layout
        fLay = pm.columnLayout(adj=True, p=self.widgets['topForm'])
        pm.separator(h=7)
        self.widgets["feedback"] = cmds.textField(tx="", editable=False)  # , p=self.widgets['topForm'])
        pm.formLayout(form, e=True, af=((fLay, 'left', 0),
                                        (fLay, 'right', 0), (fLay, 'bottom', 0)))

        if asWindow:
            cmds.showWindow()
        self.defaultFeedback()
        return self.widgets[mainLay]

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

