from maya import cmds, mel
import pymel.core as pm
from functools import partial


class SelectionDemoWin:

    def __init__(self):

        self.feedbackName = 'Selection Demo Win'
        self.selection = []
        self.widgets = {}
        self.selectionDemoWin()

    def selectionDemoWin(self):
        if cmds.window("selectDemo_window", exists=True):
            cmds.deleteUI("selectDemo_window")
        self.widgets["window"] = cmds.window("selectDemo_window", title=self.feedbackName, sizeable=1, rtf=True)
        mainLay = cmds.rowColumnLayout(numberOfColumns=1)

        selectLay = cmds.rowColumnLayout(nc=3, cs=[[2, 5], [3, 5]])
        cmds.button(l='Select Ctrls', c=self.updateFromSelection)
        cmds.button(l='Add', c=partial(self.updateFromSelection, True))
        self.widgets['selection'] = cmds.textField(w=300, cc=self.updateSelection)
        cmds.button(l="Execute", c=self.execute, p=mainLay)
        cmds.separator(h=7, p=mainLay)
        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False, p=mainLay)
        cmds.separator(h=7, p=mainLay)
        self.defaultFeedback()
        cmds.showWindow()

    def selectionFromText(self, tx, stringList=[]):
        if not tx:
            return stringList
        if ' ' in tx:
            tx = tx.replace(' ', '')
        if ',' in tx:
            ctl, com, tx = tx.partition(',')
            stringList.append(ctl)
            stringList = self.selectionFromText(tx, stringList)
        else:
            stringList.append(tx)
            stringList = self.selectionFromText('', stringList)
        return stringList

    def updateSelection(self, *args):
        self.defaultFeedback()
        text = cmds.textField(self.widgets['selection'], q=True, tx=True)
        stringList = self.selectionFromText(text)
        print stringList
        notFound = []
        nodesList = []
        for obj in stringList:
            if pm.objExists(obj):
                self.selection.append(pm.PyNode(obj))
            else:
                notFound.append(obj)
        if nodesList:
            print " // %s : nodes found:" % self.feedbackName
            print nodesList
        if notFound:
            print " // %s : warning, can't find the following names:" % self.feedbackName
            print notFound
            self.changeFeedback(" // warning, check scriptEditor for details. some nodes couldn't be found", 'red')
        self.selection = nodesList

    def updateTextField(self):
        self.defaultFeedback()
        if not self.selection:
            error = ' // %s : no selection found' % self.feedbackName
            print error
            self.changeFeedback(error, 'red')
            return
        tx = '%s' % self.selection[0].name()
        for i in range(1, len(self.selection)):
            tx += ', %s' % self.selection[i].name()
        cmds.textField(self.widgets['selection'], e=True, tx=tx)


    def updateFromSelection(self, add=False, *args):
        self.defaultFeedback()
        sele = pm.selected()
        if not sele:
            error = ' // %s : make a selection and try again' % self.feedbackName
            print error
            self.changeFeedback(error, 'red')
            return
        if add:
            for sel in sele:
                check = True
                for obj in self.selection:
                    if sel.name() == obj.name():
                        check = False
                if check:
                    self.selection.append(sel)
        else:
            self.selection = sele
        self.updateTextField()

    def execute(self, *args):
        self.defaultFeedback()
        sele = self.selection
        if not sele:
            error = ' // %s : make a selection and try again' % self.feedbackName
            print error
            self.changeFeedback(error, 'red')
            return
        tx = ' // Selection is: %s' % sele
        print tx
        self.changeFeedback(tx, 'green')
        return

    def defaultFeedback(self):
        self.changeFeedback(self.feedbackName)

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)
