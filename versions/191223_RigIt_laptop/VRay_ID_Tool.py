from maya import cmds, mel
import pymel.core as pm
from functools import partial
import UI_modules as uim
import RigItMethodsUI as rim


class VRay_ID_Tool:
    def __init__(self, par='', scriptIt=False):
        # todo check if there's VRay and that it's loaded
        self.widgets = {}
        self.feedbackName = 'VRay ID Tool'
        topLay, mainLay = self.winBase('VRay_ID_Tool', self.feedbackName, par)
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def execute(self, *args):
        self.defaultFeedback()

        idNum = cmds.intSliderGrp(self.widgets['vRayID'], q=True, v=True)

        sele = pm.selected()
        if not sele:
            self.orangeFeedback('Make a selection and try again')
            return
        for obj in sele:
            # get correct shape name
            objShp = obj.getShape()
            shpName = objShp.name()
            if '|' in shpName:
                part = shpName.partition('|')
                if part[0]:
                    objShp = '|' + shpName
            # turn on ID
            mel.eval('vray addAttributesFromGroup %s vray_objectID 1;' % objShp)
            # set ID
            objShp.vrayObjectID.set(idNum)

    def scriptIt(self, *args):
        self.defaultFeedback()
        idNum = cmds.intSliderGrp(self.widgets['vRayID'], q=True, v=True)
        sele = pm.selected()
        if not sele:
            objects = 'pm.selected'
        else:
            objects = "['%s'" % sele[0]
            for i in range(1, len(sele)):
                objects += ", '%s'" % sele[i]
            objects += "]"
        script = ('import pymel.core as pm\n\n'
                  'idNum = %s\n'
                  'objects = %s\n\n' % (idNum, objects))
        script += ("for obj in objects:\n"
                   "\t# get correct shape name\n"
                   "\tobjShp = obj.getShape()\n"
                   "\tshpName = objShp.name()\n"
                   "\tif '|' in shpName:\n"
                   "\t\tpart = shpName.partition('|')\n"
                   "\t\tif part[0]:\n"
                   "\t\t\tobjShp = '|' + shpName\n"
                   "\t# turn on ID\n"
                   "\tmel.eval('vray addAttributesFromGroup %s vray_objectID 1;' % objShp)\n"
                   "\t# set ID\n"
                   "\tobjShp.vrayObjectID.set(idNum)\n")
        rim.showScript(script)
        return

    def populateUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)
        pm.text(l='VRay ID Tool', font='boldLabelFont', p=mainLay, w=220)
        pm.separator(h=7, p=mainLay)
        # step 1
        pm.separator(h=4, style='none', p=mainLay)
        pm.text(l='Step 1: Select ID number', p=mainLay)
        self.widgets['vRayID'] = cmds.intSliderGrp(field=True, label='vRay ID', v=1, p=mainLay)
        # minValue=-10, maxValue=10, fieldMinValue=-100, fieldMaxValue=100,
        # step 2
        pm.separator(h=7, p=mainLay)
        pm.text(l='Step 2: Make a selection', p=mainLay)
        pm.separator(h=7, p=mainLay)
        # step 3
        # buttons
        if scriptIt:
            # buttons
            cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
            cmds.button(l='Execute', h=28, c=self.execute)
            cmds.button(l='Script it', w=100, c=self.scriptIt)
        else:
            cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
            cmds.button(l='Step 3: Execute', h=28, p=mainLay, c=self.execute)

    def winBase(self, name, title, par):
        winName = name + "_window"
        mainLay = "mainLay"
        topLay = "topLay"
        asWindow = True
        if par:
            print(' // %s - creating Layout under parent' % self.feedbackName)
            asWindow = False
        if asWindow:
            if cmds.window(winName, exists=True):
                cmds.deleteUI(winName)
            self.widgets[winName] = cmds.window(winName, title=title, sizeable=1, rtf=True)
            self.widgets[topLay] = cmds.columnLayout(adj=True)
        else:
            self.widgets[topLay] = cmds.columnLayout(title, adj=True, p=par)
        self.widgets[mainLay] = cmds.columnLayout(adj=True)
        pm.separator(h=7, p=self.widgets[topLay])
        self.widgets["feedback"] = cmds.textField(tx="", editable=False, p=self.widgets[topLay])
        if asWindow:
            cmds.showWindow()
        self.defaultFeedback()
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
