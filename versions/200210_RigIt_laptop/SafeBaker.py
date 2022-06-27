from maya import cmds, mel
import pymel.core as pm
from functools import partial
import UI_modules as uim
import RigItMethodsUI as rim
import generalMayaTools as gmt
import generalMayaSelections as gms

reload(uim)
reload(rim)
reload(gmt)
reload(gms)


class SafeBaker:
    def __init__(self, par='', scriptIt=False):
        self.widgets = {}
        self.feedbackName = 'Safe Baker'
        topLay, mainLay = self.winBase('safeBaker', self.feedbackName, par)
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def getNoneRefCns(self, *args):
        self.defaultFeedback()
        constraints = pm.ls(type='constraint')
        cnsList = []
        for obj in constraints:
            if ":" not in obj:
                cnsList.append(obj)
        if not cnsList:
            self.orangeFeedback('n=No none-referenced constraints found in scene')
        return cnsList

    def getCnsConnections(self, cns):
        # todo use this? if not, place it somewhere?
        # todo check if cns is pynode
        cnsObjTrans = pm.listConnections(cns.constraintTranslateX, source=False, destination=True)
        cnsObjRot = pm.listConnections(cns.constraintRotateX, source=False, destination=True)
        trans = False
        rot = False
        cnsCtl = ''
        if cnsObjTrans:
            cnsCtl = cnsObjTrans[0]
            trans = True
        if cnsObjRot:
            if cnsCtl == cnsObjRot[0]:
                rot = True
            else:
                self.printFeedback('Error - constraint connected to more than 1 obj')
        print 'cns', cns
        if not cnsCtl:
            print 'not cnsCtl'
        else:
            print 'cnsCtl', cnsCtl
        return cnsCtl, trans, rot

    def executeMakeBakeGrps(self, scrollName, *args):
        self.defaultFeedback()
        scroll = self.widgets[scrollName]
        cnsCtls = cmds.textScrollList(scroll, q=True, selectItem=True)
        if not cnsCtls:
            self.printFeedback('No constraints selected, please select and try again')
            return
        parGrp = pm.group(n='bakeCns_grp', em=True, w=True)
        bakeCtls = []
        bakeConsts = []
        bakeGrps = []
        for cnsCtl in cnsCtls:
            # todo make a checkbox to bake the ctl instead of the cns

            # todo check if attributes are locked

            grp = pm.group(n=cnsCtl + '_cnsGrp', em=True, p=parGrp)
            bakeCns = pm.parentConstraint(cnsCtl, grp)
            # todo allow manual setting for minimizeRotation ?
            # todo allow manual setting for start\end keys
            # todo allow manual setting for keeping preserveOutsideKeys (outside of time range)
            saveOutKeys = True
            startKey, endKey = gmt.getTimlineStartEnd()
            pm.bakeResults(grp, simulation=True, t=(startKey, endKey), disableImplicitControl=True,
                           preserveOutsideKeys=saveOutKeys, minimizeRotation=True, shape=True)
            # connect the baked group to ctl and bake again
            pm.delete(bakeCns)
            # todo get cns and delete needed ?
            #pm.delete(cns)
            # todo delete animation on ctl ? animCrvs = pm.listConnections(cnsCtl, source=True, destination=False, type='animCrv')
            bakeCtlCns = pm.parentConstraint(grp, cnsCtl)
            pm.bakeResults(cnsCtl, simulation=True, t=(startKey, endKey), disableImplicitControl=True,
                           preserveOutsideKeys=saveOutKeys, minimizeRotation=True, shape=True)
            pm.delete(bakeCtlCns)
        pm.delete(parGrp)

    def execute(self, *args):
        return

    def scriptIt(self, *args):
        script = "This isn't done yet"
        rim.showScript(script)
        return

    def populateNoneRefConstraints(self, scrollName, *args):
        self.defaultFeedback()
        scroll = self.widgets[scrollName]
        allItems = cmds.textScrollList(scroll, q=True, allItems=True)
        if allItems:
            for item in allItems:
                cmds.textScrollList(scroll, e=True, removeItem=item)
        noneRefCns = self.getNoneRefCns()
        for cns in noneRefCns:
            cnsCtl, trans, rot = self.getCnsConnections(cns)
            if cnsCtl:
                cmds.textScrollList(scroll, e=True, append=cnsCtl.name())
            else:
                self.printFeedback('NOTICE: "%s" isn\'t affecting a controller' % cns)

    def cnsScrollSelect(self, scrollName, select, *args):
        self.defaultFeedback()
        scroll = self.widgets[scrollName]
        cmds.textScrollList(scroll, e=True, deselectAll=True)
        if select:
            allItems = cmds.textScrollList(scroll, q=True, allItems=True)
            if allItems:
                for item in allItems:
                    cmds.textScrollList(scroll, e=True, selectItem=item)
            else:
                self.orangeFeedback('No constraints to select')

    def addRemoveCtl(self, scrollName, add, *args):
        self.defaultFeedback()
        scroll = self.widgets[scrollName]
        if add:
            self.addSelectedToScroll(scroll)
        else:
            self.removeFromScroll(scroll)

    def addSelectedToScroll(self, scroll):
        sele = pm.selected()
        if not sele:
            self.orangeFeedback('please make a selection and try again')
            return
        for sel in sele:
            cmds.textScrollList(scroll, e=True, append=sel.name())

    def removeFromScroll(self, scroll):
        selItems = cmds.textScrollList(scroll, q=True, selectItem=True)
        for item in selItems:
            cmds.textScrollList(scroll, e=True, removeItem=item)

    def populateUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)
        pm.text(l='Safe Baker', font='boldLabelFont', p=mainLay)
        pm.separator(h=7, p=mainLay)

        scrollName = 'cnsScroll'
        lay = cmds.rowColumnLayout(nc=2, adj=True, adjustableColumn=2, p=mainLay)
        cmds.rowColumnLayout(nc=1, adj=True, rs=[[1, 5], [2, 5], [3, 5], [4, 5], [5, 5]])
        pm.button('List Ctls:\nnone-ref cns', c=partial(self.populateNoneRefConstraints, scrollName))
        pm.separator(h=13)
        pm.button('Add ctl >>', c=partial(self.addRemoveCtl, scrollName, True))
        pm.button('Remove ctl <<', c=partial(self.addRemoveCtl, scrollName, False))
        pm.separator(h=13)
        pm.button('Select All', c=partial(self.cnsScrollSelect, scrollName, True))
        pm.button('Deselect All', c=partial(self.cnsScrollSelect, scrollName, False))
        self.widgets[scrollName] = cmds.textScrollList(allowMultiSelection=True, w=220, h=200, p=lay)

        pm.separator(h=7, p=mainLay)
        pm.separator(h=4, style='none', p=mainLay)
        cmds.button(l='Bake out and constraint selected', h=28, p=mainLay,
                    c=partial(self.executeMakeBakeGrps, scrollName))
        pm.separator(h=3, style='none', p=mainLay)
        #pm.separator(h=1, p=mainLay)
        '''
        # buttons
        cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
        cmds.button(l='Execute', h=28, c=self.execute)
        if scriptIt:
            cmds.button(l='Script it', w=100, c=self.scriptIt)
        else:
            pm.separator(w=100, style='none')
        '''

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
