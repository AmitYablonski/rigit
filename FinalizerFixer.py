from maya import cmds, mel
import pymel.core as pm
import RigItMethodsUI as rim
import mgear.core.icon as ic
import traceback
import generalMayaPrints as gmp
import fnmatch
from functools import partial


class FinalizerFixer:
    def __init__(self, par='', scriptIt=False, finalizer=''):
        self.selection = []
        self.widgets = {}
        self.finalizer = finalizer
        if finalizer:
            self.feedbackName = 'Fixer / Scripter'
        else:
            self.feedbackName = 'Rig Finalizer / Fixer'
        topLay, mainLay = self.winBase('FinalizerFixer', self.feedbackName, par)
        self.popCnsUI(mainLay, scriptIt)
        self.popSpringsUI(mainLay, scriptIt)
        self.defaultFeedback()

    def cnsExecute(self, *args):
        ctlSel = cmds.radioButtonGrp(self.widgets["cnsCtl_radio"], q=True, select=True)
        cnsCtl = 'local_C0_ctl'
        if ctlSel == 1:
            cnsCtl = 'global_C0_ctl'
        op = cmds.radioButtonGrp(self.widgets["cns_radio"], q=True, select=True)
        # grpText = cmds.textField(self.widgets["cns_text"], q=True, tx=True)
        mainCtl = pm.PyNode(cnsCtl)

        if op == 1:  # only global
            if ctlSel == 1:
                ctls = [mainCtl]
            else:
                ctls = [pm.PyNode("global_C0_ctl")]
        elif op == 2:  # all ctls
            ctls = pm.ls('*_ctl')  # , '*_offset')
        else:  # by selected
            ctls = pm.ls(sl=True)

        attrName = "ShowCnsCtrls"
        mainAttr = self.addAttr(mainCtl, attrName)

        for c in ctls:
            # todo replace with self.addCns?
            # todo if cns exists, see if it's connected
            oParent = c.getParent()
            icon = ic.create(oParent, c.name() + "_cns", c.getMatrix(), [0, 0, 0], 'cross')
            icon.setTransformation(c.getMatrix())
            pm.parent(c, icon)
            iconShape = icon.getShape()
            pm.connectAttr(mainAttr, iconShape.visibility)

            ro = pm.getAttr(c + '.rotateOrder')
            pm.setAttr(c.name() + "_cns" + '.rotateOrder', ro)

            print('[add cns controller] proccessed: {}'.format(c.name()))
            print("[rotate order]" + " ro = " + str(ro))

    def addCns(self, gloabl, ctl):  # todo is it used? if so, import ic
        oParent = ctl.getParent()
        # todo if cns exists, see if it's connected
        if not pm.objExists(ctl.name() + "_cns"):
            icon = ic.create(oParent, ctl.name() + "_cns", ctl.getMatrix(), [1, 0, 0], 'cross')
            icon.setTransformation(ctl.getMatrix())
            pm.parent(ctl, icon)
            iconShape = icon.getShape()
            pm.connectAttr(gloabl.ShowCnsCtrls, iconShape.visibility)
            self.printFeedback('[add cns controller] proccessed: {}'.format(ctl.name()))
        else:
            self.printFeedback('[add cns controller] already exists: {}'.format(ctl.name()))

    def cnsScriptIt(self, *args):
        ctlSel = cmds.radioButtonGrp(self.widgets["cnsCtl_radio"], q=True, select=True)
        cnsCtl = 'local_C0_ctl'
        if ctlSel == 1:
            cnsCtl = 'global_C0_ctl'
        op = cmds.radioButtonGrp(self.widgets["cns_radio"], q=True, select=True)
        if op == 2 and not pm.selected():
            self.printFeedback('Nothing is selected, please try again')
            return

        script = ('import pymel.core as pm\n'
                  'import mgear.maya.icon as ic\n'
                  'import traceback\n\n')

        script += ('mainCtl = pm.PyNode("%s")\n'
                   "attrName = '%s'\n" % (cnsCtl, 'ShowCnsCtrls'))
        script += '# ctls to add cns\n'
        if op == 1:
            if ctlSel == 1:
                script += ('ctls = [mainCtl]')
            else:
                script += ('ctls = [pm.PyNode("global_C0_ctl")]')
        elif op == 2:
            script += ('ctls = pm.ls("*_ctl")')
        else:
            tempList = pm.ls(sl=True)
            if len(tempList) <= 2:
                script += 'ctls = [pm.PyNode("%s")' % tempList[0]
                for i in range(1, len(tempList)):
                    script += ', pm.PyNode("%s")' % tempList[i]
                script += ']'
            else:
                script += ('temp = %s\n'
                           'ctls = []\n'
                           'for ctl in temp:\n'
                           '\tctls.append(pm.PyNode(ctl))' % gmp.cleanListForPrint(pm.ls(sl=True)))

        script += ('\n\n'
                   'try:\n'
                   '\tpm.addAttr(mainCtl, ln=attrName, at="double", dv=0, min=0, max=1)\n'
                   '\tmainAttr = mainCtl.attr(attrName)\n'
                   '\tpm.setAttr((mainAttr), e=1, keyable=False, cb=1)\n'
                   '\tpm.setAttr((mainAttr), 0)\n'
                   'except:\n'
                   '\tprint traceback.print_exc()\n'
                   '\tmainAttr = mainCtl.attr(attrName)\n'
                   '\tprint \'{} has cns show attribute\'.format(mainCtl.name())\n\n'
                   'for c in ctls:\n'
                   '\toParent = c.getParent()\n'
                   '\ticon = ic.create(oParent, c.name() + "_cns", c.getMatrix(), [0, 0, 0], \'cross\')\n'
                   '\ticon.setTransformation(c.getMatrix())\n'
                   '\tpm.parent(c, icon)\n'
                   '\ticonShape = icon.getShape()\n'
                   '\tpm.connectAttr(mainAttr, iconShape.visibility)\n\n'

                   '\tro = pm.getAttr(c + \'.rotateOrder\')\n'
                   '\tpm.setAttr(c.name() + "_cns" + \'.rotateOrder\', ro)\n\n'

                   '\tprint \'[add cns controller] proccessed: {}\'.format(c.name())\n'
                   '\tprint "[rotate order]" + " ro = " + str(ro)\n')
        rim.showScript(script)
        return

    def setMainAttrCtl(self, assetType, *args):
        mainCtl = (assetType == 'props' or assetType == 'set')
        for radGrp in ['cnsCtl_radio', 'springsCtl_radio']:
            if mainCtl:
                cmds.radioButtonGrp(self.widgets[radGrp], e=True, select=1)
            else:
                cmds.radioButtonGrp(self.widgets[radGrp], e=True, select=2)

    def addAttr(self, mainCtl, attrName):
        try:
            pm.addAttr(mainCtl, ln=attrName, at="double", dv=0, min=0, max=1)
            mainAttr = mainCtl.attr(attrName)
            pm.setAttr(mainAttr, e=1, keyable=False, cb=1)
        except:
            try:
                mainAttr = mainCtl.attr(attrName)
                error = '%s\n%s' % (traceback.print_exc(), '"%s.%s" attribute already exists' % (mainCtl, attrName))
            except:
                error = '%s\n%s' % (traceback.print_exc(), 'problem creating attribute "%s.%s"' % (mainCtl, attrName))
            self.printFeedback(error, 'none')
        pm.setAttr(mainCtl.attr(attrName), 0)
        return mainAttr

    def popCnsUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)
        pm.text(l='Cns Creator', font='boldLabelFont', p=mainLay)
        pm.separator(h=7, p=mainLay)
        self.widgets["cnsCtl_radio"] = cmds.radioButtonGrp(l='Attr ctl: ', numberOfRadioButtons=2, cw2=[100, 100],
                                                           labelArray2=['Global', 'Local'],
                                                           select=1, p=mainLay)
        self.widgets["cns_radio"] = cmds.radioButtonGrp(l='Affect: ', numberOfRadioButtons=3, cw3=[100, 100, 100],
                                                        labelArray3=['Global only', 'All controllers', 'Selected'],
                                                        select=2, p=mainLay)
        pm.separator(h=7, p=mainLay)
        # pm.text(l='I mean.. under the mainLay\nExample:', p=mainLay)
        # self.widgets['objField'] = uim.selectAndAddToField(self, mainLay, 'Select', 'transform')
        # self.widgets['attrField'] = uim.textAndField(mainLay, 'Text example: ', 'new string')

        # buttons
        cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
        cmds.button(l='Execute', h=28, c=self.cnsExecute)
        if scriptIt:
            cmds.button(l='Script it', w=100, c=self.cnsScriptIt)
        else:
            pm.separator(w=100, style='none')

    def springsExecute(self, *args):
        ctlSel = cmds.radioButtonGrp(self.widgets["springsCtl_radio"], q=True, select=True)
        uiSel = cmds.radioButtonGrp(self.widgets["springsUI_radio"], q=True, select=True)
        cnsCtl = 'local_C0_ctl'
        if ctlSel == 1:
            cnsCtl = 'global_C0_ctl'

        mainCtl = cnsCtl
        attrName = 'GlobalSpringVolume'
        mainAttr = self.addAttr(mainCtl, attrName)

        if uiSel == 1:  # all UI_ in scene
            pm.select('*UI_*')  # if it should get connected to all UIs (add to selection other controllers if needed)
        uiObjects = pm.ls(sl=True)

        theAttributeList = []
        for o in uiObjects:
            filtered = []
            attrs = pm.listAttr(o, r=1, s=1, k=1)
            filtered = fnmatch.filter(attrs, '*intensity*')
            if filtered.count > 0:
                for i in filtered:
                    FullName = (o + "." + i)
                    theAttributeList.append(FullName)

        numOfMults = len(theAttributeList) / 3 + sorted((0, (len(theAttributeList) % 3), 1))[1]

        counter = 0
        for i in range(0, numOfMults):
            MultNode = pm.createNode("multiplyDivide")
            for axis in "xyz":
                if counter < len(theAttributeList):
                    origOutputConnections = pm.listConnections(theAttributeList[counter], d=True, s=False, scn=True,
                                                               p=1)
                    for con in origOutputConnections:
                        pm.disconnectAttr(theAttributeList[counter], con)
                    pm.connectAttr(theAttributeList[counter], MultNode.attr('i1' + axis))
                    pm.connectAttr(mainAttr, MultNode.attr('i2' + axis))
                    for con in origOutputConnections:
                        MultNode.attr("o" + axis) >> con
                    counter = counter + 1

        for attr in theAttributeList:
            pm.setAttr(attr, 1)

        pm.currentTime(2)
        pm.currentTime(1)

    def springsScriptIt(self, *args):
        ctlSel = cmds.radioButtonGrp(self.widgets["springsCtl_radio"], q=True, select=True)
        uiSel = cmds.radioButtonGrp(self.widgets["springsUI_radio"], q=True, select=True)
        cnsCtl = 'local_C0_ctl'
        if ctlSel == 1:
            cnsCtl = 'global_C0_ctl'

        mainCtl = cnsCtl
        attrName = 'GlobalSpringVolume'
        # todo fix or remove:
        #if uiSel != 1:  # all UI_ in scene
        #    pm.select('*UI_*')  # if it should get connected to all UIs (add to selection other controllers if needed)

        script = (
                "import pymel.core as pm\n"
                "import fnmatch\n\n"

                "## - - - - Create Global Jiggle Volume Control - - - - ##\n"
                "mainCtl = '%s'\n"
                "attrName = '%s'\n"
                "pm.addAttr(mainCtl, ln=attrName, at='double', dv=0, min=0, max=1)\n"
                "mainAttr = mainCtl + '.' + attrName\n"
                "pm.setAttr(mainAttr, e=1, keyable=True)\n"
                "pm.setAttr(mainAttr, 0)\n\n" % (mainCtl, attrName))

        script += "uiObjects = %s\n\n" % gmp.cleanListForPrint(pm.ls(sl=True))
        script += (
            "theAttributeList = []\n"
            "for o in uiObjects:\n"
            "\tfiltered = []\n"
            "\tattrs = pm.listAttr(o, r=1, s=1, k=1)\n"
            "\tfiltered = fnmatch.filter(attrs, '*intensity*')\n"
            "\tif filtered.count > 0:\n"
            "\t\tfor i in filtered:\n"
            "\t\t\tFullName = (o + '.' + i)\n"
            "\t\t\ttheAttributeList.append(FullName)\n\n"

            "numOfMults = len(theAttributeList) / 3 + sorted((0, (len(theAttributeList) % 3), 1))[1]\n\n"

            "counter = 0\n"
            "for i in range(0, numOfMults):\n"
            "\tMultNode = pm.createNode('multiplyDivide')\n"
            "\tfor axis in 'xyz':\n"
            "\t\tif counter < len(theAttributeList):\n"
            "\t\t\torigOutputConnections = pm.listConnections(theAttributeList[counter], d=True, s=False, scn=True, p=1)\n"
            "\t\t\tfor con in origOutputConnections:\n"
            "\t\t\t\tpm.disconnectAttr(theAttributeList[counter], con)\n"
            "\t\t\tpm.connectAttr(theAttributeList[counter], MultNode.attr('i1' + axis))\n"
            "\t\t\tpm.connectAttr(mainAttr, MultNode.attr('i2' + axis))\n"
            "\t\t\tfor con in origOutputConnections:\n"
            "\t\t\t\tMultNode.attr('o' + axis) >> con\n"
            "\t\t\tcounter = counter + 1\n\n"

            "for attr in theAttributeList:\n"
            "\tpm.setAttr(attr, 1)\n\n"

            "pm.currentTime(2)\n"
            "pm.currentTime(1)\n")

        rim.showScript(script)
        return

    def popSpringsUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)
        pm.text(l='Global Springs', font='boldLabelFont', p=mainLay)
        pm.separator(h=7, p=mainLay)

        cmds.rowColumnLayout(nc=1, adj=True, p=mainLay)
        self.widgets["springsCtl_radio"] = cmds.radioButtonGrp(l='Attr ctl: ', numberOfRadioButtons=2, cw2=[100, 100],
                                                               labelArray2=['Global', 'Local'], select=1)
        self.widgets["springsUI_radio"] = cmds.radioButtonGrp(l='UI to connect: ', numberOfRadioButtons=2,
                                                              cw2=[100, 100],
                                                              labelArray2=['All *UI_*', 'Selected Ctls'], select=1)
        pm.text(l='temp: Script it gives an example')

        # buttons
        cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
        cmds.button(l='Execute', h=28, c=self.springsExecute)
        if scriptIt:
            cmds.button(l='Script it', w=100, c=self.springsScriptIt)
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
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedback"], e=True, bgc=bg, tx=messege)
