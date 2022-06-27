from maya import cmds, mel
import pymel.core as pm
from functools import partial
import UI_modules as uim
import RigItMethodsUI as rim
import generalMayaPrints as gmp


class Duplicator:
    def __init__(self, par='', scriptIt=False):
        self.widgets = {}
        self.feedbackName = 'Duplicator'

        # todo make UI nicer ?

        # todo optinos to add suffix to all duplicates

        # todo check all duplicate options

        topLay, mainLay = self.winBase(self.feedbackName, self.feedbackName, par)
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def execute(self, *args):
        name = pm.textField(self.widgets['name'], q=True, tx=True)
        inputConnections = pm.checkBox(self.widgets['inputConnections'], q=True, v=True)
        upstreamNodes = pm.checkBox(self.widgets['upstreamNodes'], q=True, v=True)
        instanceLeaf = pm.checkBox(self.widgets['instanceLeaf'], q=True, v=True)
        parentOnly = pm.checkBox(self.widgets['parentOnly'], q=True, v=True)
        renameChildren = pm.checkBox(self.widgets['renameChildren'], q=True, v=True)
        smartTransform = pm.checkBox(self.widgets['smartTransform'], q=True, v=True)

        objects = pm.selected()
        if name:
            pm.duplicate(objects, inputConnections=inputConnections, instanceLeaf=instanceLeaf, name=name,
                         parentOnly=parentOnly, renameChildren=renameChildren,
                         smartTransform=smartTransform, upstreamNodes=upstreamNodes)
        else:
            pm.duplicate(objects, inputConnections=inputConnections, instanceLeaf=instanceLeaf,
                         parentOnly=parentOnly, renameChildren=renameChildren,
                         smartTransform=smartTransform, upstreamNodes=upstreamNodes)

    def scriptIt(self, *args):
        name = pm.textField(self.widgets['name'], q=True, tx=True)
        inputConnections = pm.checkBox(self.widgets['inputConnections'], q=True, v=True)
        upstreamNodes = pm.checkBox(self.widgets['upstreamNodes'], q=True, v=True)
        instanceLeaf = pm.checkBox(self.widgets['instanceLeaf'], q=True, v=True)
        parentOnly = pm.checkBox(self.widgets['parentOnly'], q=True, v=True)
        renameChildren = pm.checkBox(self.widgets['renameChildren'], q=True, v=True)
        returnRootsOnly = pm.checkBox(self.widgets['returnRootsOnly'], q=True, v=True)
        smartTransform = pm.checkBox(self.widgets['smartTransform'], q=True, v=True)

        sele = pm.selected()
        script = 'dup = pm.duplicate(%s' % gmp.cleanListForPrint(sele)
        if name:
            script += ', name="%s"' % name
        if inputConnections:
            script += ', inputConnections=True'
        if upstreamNodes:
            script += ', upstreamNodes=True'
        if instanceLeaf:
            script += ', instanceLeaf=True'
        if parentOnly:
            script += ', parentOnly=True'
        if renameChildren:
            script += ', renameChildren=True'
        if smartTransform:
            script += ', smartTransform=True'
        if returnRootsOnly:
            script += ', returnRootsOnly=True'

        rim.showScript(script + ')')

    def populateUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)

        # self.widgets['objField'] = uim.selectAndAddToField(self, mainLay, 'Select', 'transform')

        # todo if some options clash with others, give feedback error
        self.widgets['name'] = uim.textAndField(mainLay, 'Duplicate Name: ', '')

        pm.setParent(mainLay)

        pm.separator(h=7)
        self.widgets['inputConnections'] = pm.checkBox(l='Duplicate input connections')

        pm.separator(h=7)
        self.widgets['upstreamNodes'] = pm.checkBox(l='Duplicate outputs')

        pm.separator(h=7)
        self.widgets['instanceLeaf'] = pm.checkBox(l='Make instance')
        pm.separator(h=7)
        self.widgets['parentOnly'] = pm.checkBox(l='Duplicate selected parent (no shapes)')
        pm.separator(h=7)
        self.widgets['renameChildren'] = pm.checkBox(l='Rename Children')
        pm.separator(h=7)
        self.widgets['smartTransform'] = pm.checkBox(l='Smart Transform')
        pm.separator(h=7)
        self.widgets['returnRootsOnly'] = pm.checkBox(l='Return Roots Only (for code)')

        pm.separator(h=10)

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
            bg = [1, .4, .4]
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedback"], e=True, bgc=bg, tx=messege)
