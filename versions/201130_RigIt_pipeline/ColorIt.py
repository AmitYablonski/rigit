from maya import cmds, mel
import pymel.core as pm
from functools import partial
import UI_modules as uim
import RigItMethodsUI as rim

reload(uim)


class ColorIt:
    def __init__(self, par='', scriptIt=False):
        self.widgets = {}
        self.feedbackName = 'Color It'
        topLay, mainLay = self.winBase('ColorIt', self.feedbackName, par)
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def execute(self, *args):
        ctl, attrName, mainShader, makeFiles = self.getUiData()
        if not ctl:
            return
        if not self.validObjects([ctl, mainShader]):
            return
        ctl = pm.PyNode(ctl)
        mainShader = pm.PyNode(mainShader)
        mainDest = mainShader.color

        colorList = self.getColorList()

        # create attr
        enumString = colorList[0][0]
        for i in range(1, len(colorList)):
            name = colorList[i][0]
            enumString += ":%s" % name
        pm.addAttr(ctl, ln=attrName, at="enum", enumName=enumString, keyable=True)

        # create choice node
        choiceNode = pm.shadingNode('choice', asUtility=True, name=attrName + '_choice')
        ctl.attr(attrName) >> choiceNode.selector
        choiceNode.output >> mainDest

        for i, [name, rgbVal] in enumerate(colorList):
            shader = pm.shadingNode("lambert", asShader=True, n="%s_mtl" % name)
            shader.color.set(rgbVal)
            shader.color >> choiceNode.input[i]
            if makeFiles:
                # todo check if this is needed: fileDest = '%s' % shader.color
                fileNode = pm.PyNode(mel.eval('createRenderNodeCB -as2DTexture "" file "defaultNavigation '
                                              '-force true -connectToExisting -source %node '
                                              '-destination ' + str(shader.color) + '; '
                                                                                    'window -e -vis false createRenderNodeWindow;";'))
                pm.rename(fileNode, 'file_%s' % name)

    def scriptIt(self, *args):
        ctl, attrName, mainShader, makeFiles = self.getUiData()
        self.validObjects([ctl, mainShader])
        script = 'import pymel.core as pm\n' \
                 'from maya import mel\n\n' \
                 'attrName = "%s"\n' \
                 'ctl = pm.PyNode("%s")\n' \
                 'mainShader = pm.PyNode("%s")\n' % (attrName, ctl, mainShader)

        # get and cleanup colorList
        temp = self.getColorList()
        colorList = []
        for name, val in temp:
            if makeFiles:
                colorList.append(str(name))
            else:
                cleanRgb = [round(val[0], 3), round(val[1], 3), round(val[2], 3)]
                colorList.append([str(name), cleanRgb])
        script += 'colorList = %s\n\n' % colorList

        script += '# create attr\n' \
                  'enumString = colorList[0][0]\n' \
                  'for i in range(1, len(colorList)):\n\t' \
                  'enumString += ":%s" % colorList[i][0]\n' \
                  'pm.addAttr(ctl, ln=attrName, at="enum", enumName=enumString, keyable=True)\n\n'

        script += "# create choice node\n" \
                  "choiceNode = pm.shadingNode('choice', asUtility=True, name=attrName + '_choice')\n" \
                  "ctl.attr(attrName) >> choiceNode.selector\n" \
                  "choiceNode.output >> mainShader.color\n\n"
        if makeFiles:
            script += "for i, name in enumerate(colorList):\n\t"
        else:
            script += "for i, [name, rgbVal] in enumerate(colorList):\n\t"
        script += "shader = pm.shadingNode('lambert', asShader=True, n='%s_mtl' % name)\n\t"
        if not makeFiles:
            script += "shader.color.set(rgbVal)\n\t"
        script += "shader.color >> choiceNode.input[i]\n\t"
        if makeFiles:
            script += "fileNode = pm.PyNode(mel.eval('createRenderNodeCB -as2DTexture \"\" file \"defaultNavigation '" \
                      "\n\t                              '-force true -connectToExisting -source %node '" \
                      "\n\t                              '-destination ' + str(shader.color) + '; '" \
                      "\n\t                              'window -e -vis false createRenderNodeWindow;\";'))" \
                      "\n\tpm.rename(fileNode, 'file_%s' % name)"
        script += '\n'
        rim.showScript(script)

    def getColorList(self):
        colorList = []
        for i in range(1, len(self.widgets["colorDict"]) + 1):
            cmds.textScrollList(self.widgets["enumScroll"], e=True, selectIndexedItem=i)
            idx, name = self.getScrollSelection()
            rgbVal = cmds.colorInputWidgetGrp(self.widgets["colorDict"][i], q=True, rgb=True)
            colorList.append([name, rgbVal])
        return colorList

    def validObjects(self, toValidate):
        if isinstance(toValidate, list) or isinstance(toValidate, tuple):
            for obj in toValidate:
                if not pm.objExists(obj):
                    self.printFeedback('Error finding objs: %s' % obj)
                    return False
        else:
            if not pm.objExists(toValidate):
                self.printFeedback('Error finding objs: %s' % toValidate)
                return False
        return True

    def getUiData(self):
        obj = cmds.textField(self.widgets['objField'], q=True, tx=True)
        attrName = cmds.textField(self.widgets['attrField'], q=True, tx=True)
        shader = cmds.textField(self.widgets['shdField'], q=True, tx=True)
        makeFiles = cmds.checkBox(self.widgets['filesCBox'], q=True, v=True)
        if not obj or not shader:
            self.printFeedback('Please make sure an object and a shader are selected')
            return False, False, False, False
        if not attrName:
            self.printFeedback('Please name the attribute')
            return False, False, False, False
        return obj, attrName, shader, makeFiles

    def populateUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)
        pm.text(l='Create/Connect color switcher', font='boldLabelFont', p=mainLay)
        pm.separator(h=7, p=mainLay)
        self.widgets['objField'] = uim.selectAndAddToField(self, mainLay, 'Select controller', 'transform')
        self.widgets['shdField'] = uim.selectAndAddToField(self, mainLay, 'Select shader')
        self.widgets['attrField'] = uim.textAndField(mainLay, 'Attribute Name: ', 'colorSwitcher')
        pm.separator(h=7, p=mainLay)

        self.populateAttrEdit(mainLay)

        pm.separator(h=7, p=mainLay)

        self.populateColorEdit(mainLay)

        # buttons
        pm.separator(h=7, p=mainLay)
        cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
        cmds.button(l='Execute', h=28, c=self.execute)
        if scriptIt:
            cmds.button(l='Script it', w=100, c=self.scriptIt)
        else:
            pm.separator(w=100, style='none')

    def populateAttrEdit(self, mainLay):  # Enum attr
        cmds.frameLayout(label="Shaders and attribute Names:", collapsable=False, p=mainLay)
        layTop = cmds.rowColumnLayout(nc=2, adj=True, adjustableColumn=1)
        lay = cmds.rowColumnLayout(nc=2, adj=True, adjustableColumn=2)
        cmds.text("Select color: ", al='left', w=80)
        self.widgets["enumScroll"] = cmds.textScrollList(append=['Color1', 'Color2'], allowMultiSelection=False, w=125,
                                                         sc=self.editScroll, p=lay)
        cmds.text("Edit name: ", al='left', w=80, p=lay)
        self.widgets["enumTextFld"] = cmds.textField(w=125, cc=self.scrollRenamer, p=lay)

        pm.separator(h=7)
        pm.separator(h=7)

        pm.separator(style='none')
        self.widgets['filesCBox'] = cmds.checkBox('Create File nodes for each option')

        cmds.rowColumnLayout(nc=1, adj=True, p=layTop)
        cmds.separator(h=15)
        cmds.button(l='<< Add Color', c=self.addColor)
        cmds.separator(h=15)
        cmds.button(l='>> Remove   ', c=self.removeColor)
        cmds.separator(h=15)

    def addColor(self, *args):
        self.defaultFeedback()
        newIdx = len(self.widgets["colorDict"]) + 1
        newName = 'Color%s' % newIdx
        self.widgets["colorDict"][newIdx] = cmds.colorInputWidgetGrp(label='%s : ' % newName, rgb=(1, 0, 0),
                                                                     p=self.widgets['colorShow'])
        cmds.textScrollList(self.widgets["enumScroll"], edit=True, appendPosition=[newIdx, newName])
        cmds.textScrollList(self.widgets["enumScroll"], e=True, selectIndexedItem=newIdx)
        self.editScroll()

    def removeColor(self, *args):
        self.defaultFeedback()
        idx, tx = self.getScrollSelection()
        if not idx:
            return
        cmds.textScrollList(self.widgets["enumScroll"], edit=True, removeIndexedItem=idx)
        cmds.deleteUI(self.widgets["colorDict"][int(idx)])
        self.removeIdxFromDict(idx)

    def removeIdxFromDict(self, idx):
        tempDict = {}
        ii = 1
        for i in range(1, len(self.widgets["colorDict"]) + 1):
            if i != idx:
                tempDict[ii] = self.widgets["colorDict"][i]
                ii += 1
        self.widgets["colorDict"] = tempDict
        self.editScroll()

    def getScrollSelection(self):
        idx = cmds.textScrollList(self.widgets["enumScroll"], q=True, selectIndexedItem=True)
        tx = cmds.textScrollList(self.widgets["enumScroll"], q=True, selectItem=True)
        if idx and tx:
            return idx[0], tx[0]
        else:
            self.printFeedback("Nothing's selected under enum scroll")
            return False, False

    def populateColorEdit(self, mainLay):  # Enum attr
        self.widgets['colorFrame'] = cmds.frameLayout(label="Edit Color:", collapsable=False, p=mainLay)
        self.widgets['colorShow'] = cmds.rowColumnLayout(nr=1)
        self.widgets["colorDict"] = {}
        for i in range(1, 3):
            cmds.textScrollList(self.widgets["enumScroll"], e=True, selectIndexedItem=i)
            idx, tx = self.getScrollSelection()
            self.widgets["colorDict"][i] = cmds.colorInputWidgetGrp(label='%s : ' % tx, rgb=(1, 0, 0))
        cmds.textScrollList(self.widgets["enumScroll"], edit=True, selectIndexedItem=1)
        # self.widgets['colorHide'] = cmds.rowColumnLayout(nc=2, w=1, h=1)
        self.editScroll()

    def scrollRenamer(self, *args):
        self.defaultFeedback()
        item = cmds.textScrollList(self.widgets["enumScroll"], query=True, selectIndexedItem=True)
        if item:
            item = item[0]
        else:
            self.printFeedback("Nothing's selected under enum scroll")
            return
        newText = cmds.textField(self.widgets["enumTextFld"], query=True, text=True)

        cmds.textScrollList(self.widgets["enumScroll"], edit=True, appendPosition=[int(item), newText])
        cmds.textScrollList(self.widgets["enumScroll"], edit=True, removeIndexedItem=int(item) + 1)
        cmds.textScrollList(self.widgets["enumScroll"], edit=True, selectIndexedItem=int(item))
        # update color name in color selection
        cmds.colorInputWidgetGrp(self.widgets["colorDict"][item], e=True, label='%s : ' % newText)

    def editScroll(self, *args):
        self.defaultFeedback()
        idx, tx = self.getScrollSelection()
        if not idx:
            cmds.textField(self.widgets["enumTextFld"], edit=True, text='')
            for i in self.widgets["colorDict"]:
                cmds.colorInputWidgetGrp(self.widgets["colorDict"][i], e=True, w=1)
            return
        cmds.textField(self.widgets["enumTextFld"], edit=True, text=tx)
        # show relevant color edit
        for i in self.widgets["colorDict"]:
            cmds.colorInputWidgetGrp(self.widgets["colorDict"][i], e=True, w=1)
        idx, tx = self.getScrollSelection()
        if idx:
            cmds.colorInputWidgetGrp(self.widgets["colorDict"][idx], e=True, w=360)

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
