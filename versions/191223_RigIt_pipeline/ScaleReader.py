from maya import cmds, mel
import pymel.core as pm
from functools import partial


class ScaleReader:

    def __init__(self):

        self.selection = []
        self.widgets = {}
        self.scaleReaderWin()

    def scaleReaderWin(self):
        if cmds.window("scaleReader_window", exists=True):
            cmds.deleteUI("scaleReader_window")
        self.widgets["window"] = cmds.window("scaleReader_window", title="Create Scale Reader", sizeable=1, rtf=True)
        mainLay = cmds.rowColumnLayout(numberOfColumns=1)

        selectLay = cmds.rowColumnLayout(nc=3, cs=[[2, 5], [3, 5]])
        cmds.button(l='Select Ctrls', c=self.updateFromSelection)
        cmds.button(l='Add', c=partial(self.updateFromSelection, True))
        self.widgets['selection'] = cmds.textField(w=300, cc=self.updateSelection)
        cmds.button(l="Execute", c=self.scaleReader, p=mainLay)
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
            print " // Scale Reader : nodes found:"
            print nodesList
        if notFound:
            print " // Scale Reader : warning, can't find the following names:"
            print notFound
            self.changeFeedback(" // warning, check scriptEditor for details. some nodes couldn't be found", 'red')
        self.selection = nodesList

    def updateTextField(self):
        self.defaultFeedback()
        if not self.selection:
            error = ' // Scale Reader : no selection found'
            print error
            self.changeFeedback(error, 'red')
            return
        print 'building new text from %s' % self.selection
        tx = '%s' % self.selection[0].name()
        for i in range(1, len(self.selection)):
            tx += ', %s' % self.selection[i].name()
        print 'new text is %s' % tx
        cmds.textField(self.widgets['selection'], e=True, tx=tx)


    def updateFromSelection(self, add=False, *args):
        self.defaultFeedback()
        print 'list before updateFromSelection: %s' % self.selection
        sele = pm.selected()
        if not sele:
            error = ' // Scale Reader : make a selection and try again'
            print error
            self.changeFeedback(error, 'red')
            return
        if add:
            print 'add selection'
            for sel in sele:
                check = True
                for obj in self.selection:
                    if sel.name() == obj.name():
                        check = False
                if check:
                    print 'adding!'
                    self.selection.append(sel)
        else:
            print 'new selection'
            self.selection = sele
        print 'list before update text: %s' % self.selection
        self.updateTextField()

    def scaleReader(self, *args):
        self.defaultFeedback()
        cList = self.selection
        gCtl = 'global_C0_ctl'
        hGrp = 'high_grp'
        error = ''
        try:
            gCtl = pm.PyNode(gCtl)
        except:
            error = ' // Scale Reader : Couldn\'t find "global_C0_ctl" in scene'
        try:
            hGrp = pm.PyNode(hGrp)
        except:
            error = ' // Scale Reader : Couldn\'t find "high_grp" in scene'
        if not cList:
            error = ' // Scale Reader : Make a selection and try again'
        if error:
            print error
            self.changeFeedback(error, 'red')
            return
        dontParent = False
        if pm.objExists('scaleReader_grp'):
            sclGrp = pm.PyNode('scaleReader_grp')
            dontParent = True
        else:
            sclGrp = pm.group(n='scaleReader_grp', em=True, w=True)
        for con in cList:
            #prefix = con.name()[:-3]
            prefix = con.name().rpartition('_')
            prefix = prefix[0] + '_'
            # start
            loc = pm.spaceLocator(n=prefix + 'loc')
            pm.scaleConstraint(con, loc)
            pm.parent(loc, sclGrp)
            attrName = prefix + 'scaleReader'
            pm.addAttr(gCtl, ln=attrName, typ='float', k=True)
            pm.addAttr(hGrp, ln='c_' + attrName, typ='float', k=True)
            loc.scaleX >> gCtl.attr(attrName)
            gCtl.attr(attrName) >> hGrp.attr('c_' + attrName)
            loc.v.set(0)
            # done
            print 'scale reader for : "%s" created' % con
        if dontParent:
            self.changeFeedback(" // Scale Reader : Done", 'green')
            return
        if pm.objExists('setup'):
            pm.parent(sclGrp, 'setup')
        elif pm.objExists('extraSetup'):
            pm.parent(sclGrp, 'extraSetup')
        elif pm.objExists('ExtraSetup'):
            pm.parent(sclGrp, 'ExtraSetup')
        else:
            error = " // Scale Reader : Done but couldn't find a \"setup\" group"
            print error
            self.changeFeedback(error, 'orange')

    def defaultFeedback(self):
        self.changeFeedback("Scale Reader")

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)
