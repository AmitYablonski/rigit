from maya import cmds, mel
import pymel.core as pm
from functools import partial
import RigItMethodsUI as srm
#global script

class BspEditor:
    def __init__(self, parent):

        global script
        self.selection = []
        self.widgets = {}
        self.bShapeName = ''
        self.geometry = ''
        self.bShapeGeo = ''
        self.newBsp = False
        self.bspEditor(parent)

    def bspEditor(self, parent='None'):
        if parent == 'None':
            return ("Can't load BspEditor")
        self.widgets["bspEditor_mainLayout"] = cmds.columnLayout("Blend Shape", p=parent, adj=True)

        self.widgets["bsp_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=2, select=1,  # , cw2=[100, 100]
                                                        labelArray2=['Add to existing', 'New'], onc=self.bspEditorFix)
        cmds.separator(h=7)
        self.widgets["bspName_rowLayout"] = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[1, 80],
                                                           p=self.widgets["bspEditor_mainLayout"])
        self.widgets["bspText"] = cmds.text("bspText", l="Bsp Name:")
        self.widgets["bsp_name"] = cmds.textField(tx="")
        self.widgets["group_rowLayout"] = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[1, 80],
                                                         p=self.widgets["bspEditor_mainLayout"])
        cmds.text("Object Name:")
        self.widgets["object_name"] = cmds.textField(tx="")
        cmds.rowLayout(numberOfColumns=2, p=self.widgets["bspEditor_mainLayout"])
        cmds.button(l="Add names from selection", w=140, c=self.addNameSelection)
        cmds.separator(vis=False)

        cmds.separator(h=7, p=self.widgets["bspEditor_mainLayout"])
        self.widgets["bspName_rowLayout"] = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[1, 80],
                                                           p=self.widgets["bspEditor_mainLayout"])
        cmds.text("Blend Shape/s:")
        self.widgets["bspToAdd"] = cmds.textField(tx="")
        cmds.rowLayout(numberOfColumns=2, p=self.widgets["bspEditor_mainLayout"])
        cmds.button(l="Add shapes from selection", w=140, c=self.addBspSelection)
        cmds.separator(vis=False)

        cmds.separator(h=7, p=self.widgets["bspEditor_mainLayout"])
        self.widgets["turnOn_checkBox"] = cmds.checkBox('Turn on blend shape after adding it', v=True,
                                                        p=self.widgets["bspEditor_mainLayout"])
        self.widgets["delete_checkBox"] = cmds.checkBox('Delete blend shape after adding it',
                                                        p=self.widgets["bspEditor_mainLayout"])

        cmds.separator(h=7, p=self.widgets["bspEditor_mainLayout"])
        scriptItButtons = cmds.rowColumnLayout(nc=2, adj=True, p=self.widgets["bspEditor_mainLayout"])
        cmds.columnLayout(adj=False)
        cmds.button(w=199, l="Compile Script!", c=self.scriptIt)
        cmds.columnLayout(adj=True, p=scriptItButtons)
        # todo? self.widgets["signalButton"] = cmds.button(w=199, l="not compiled", bgc=[.5,.5,.5])
        cmds.separator(w=400, h=7, p=self.widgets["bspEditor_mainLayout"])
        '''
        cmds.columnLayout(p=self.widgets["bspEditor_mainLayout"], adj=True)
        self.widgets["dataType_frameLayout"] = cmds.frameLayout(label="Script:", collapsable=False, w=400)
        cmds.rowColumnLayout(adj=True)
        self.widgets["scriptField"] = cmds.scrollField(h=200)
        '''

        cmds.separator(h=7, p=self.widgets["bspEditor_mainLayout"])
        self.widgets["feedbackTextField"] = cmds.textField(tx="Blend Shape Editor", editable=False,
                                                           p=self.widgets["bspEditor_mainLayout"])
        self.defaultFeedback()

    @staticmethod
    def getScript(*args):
        if script:
            return script
        else:
            return False

    def scriptIt(self, *args):
        self.defaultFeedback()
        op = cmds.radioButtonGrp(self.widgets["bsp_radio"], q=True, select=True)
        delete = cmds.checkBox(self.widgets["delete_checkBox"], query=True, v=True)
        turnOn = cmds.checkBox(self.widgets["turnOn_checkBox"], query=True, v=True)

        # check if geometries and blend shapes were selected or named
        objName = cmds.textField(self.widgets["object_name"], q=True, tx=True)
        bspToAdd = cmds.textField(self.widgets["bspToAdd"], q=True, tx=True)

        if not objName:
            self.changeFeedback("No geometry was assigned", "red")
            return
        if not bspToAdd:
            self.changeFeedback("No blend shape geometries were assigned", "red")
            return

        # start of script creation (excluding import)
        script = 'geometry = "%s"\n' % objName  # geo with the bsp node
        script += 'bShapeGeo = "%s"\n' % bspToAdd
        # todo check if blend shape names were selected
        if op is 1: # add to existing
            bspName = cmds.textField(self.widgets["bsp_name"], q=True, tx=True)
            # todo find the next available position
            # number after geometry is the position in the node
            if not bspName:
                self.changeFeedback("No blend shape nodes were assigned", "red")
                return
            script += 'bShapeName = pm.PyNode("%s")\n' %bspName
            # todo find blend shape position
            # todo find blend shape position
            # todo find blend shape position
            script += "pos = 10  # position to add to the bsp node\n"
            # add bShapes command
            script += "# add to blend shape\n"
            if bspName.partition(",")[1] == ",":
                script += "for bsp in bShapeGeo:\n"
                # todo find pos command
                script += "\tpm.blendShape(bShapeName, edit=True, t=[geometry, pos, bsp, 1.0])\n"
                script += "\tpos += 1\n"
            else:
                script += "pm.blendShape(bShapeName, edit=True, t=[geometry, pos, bShapeGeo, 1.0])\n"

        else: # create new
            # todo make sure it works with multiple blend shapes to add
            # todo check if name is given, else, name it "properly"
            script += '# Create new blendShape\nbShape = pm.blendShape(bShapeGeo, geometry, n="bsp_name")[0]\n'
        if turnOn:
            script += '# turn bShapes on\n'
            # todo if multiple bsp geometries, make a loop, else:
            if bspToAdd.partition(",")[1] == ",":
                script += 'for bsp in bShapeGeo:\n'
                script += '\tbShape.setAttr(bsp, 1)\n'
            else:
                script += 'bShape.setAttr(bShapeGeo, 1)\n'
        if delete:
            script += "pm.delete(bShapeGeo)\n"
        global script
        self.changeFeedback("Compiled!", "green")

        #cmds.scrollField(self.widgets["scriptField"], e=True, it=script+"\n")

    def addBspSelection(self, *args):
        self.defaultFeedback()
        sel = pm.ls(sl=True)
        self.bShapeGeo = sel
        if len(sel) >= 1:
            temp = ""
            if len(sel) > 1:
                temp += "[" + sel[0].name()
                for i in range(1, len(sel)):
                    temp += ", %s" % sel[i].name()
                temp += "]"
            else:
                temp += sel[0].name()
            cmds.textField(self.widgets["bspToAdd"], e=True, text=temp)
        else:
            srm.makeSelectionWin()
            self.changeFeedback("Make a selection and try again", "red")

    def addNameSelection(self, *args):
        self.defaultFeedback()
        selection = pm.ls(sl=True)

        op = cmds.radioButtonGrp(self.widgets["bsp_radio"], q=True, select=True)
        bShapes = []
        if len(selection) is 1:
            self.geometry = selection[0]
            cmds.textField(self.widgets["object_name"], e=True, text=self.geometry.name())
            # find blend shapes
            # todo filter it to inputs only!
            if op is 1:
                history = pm.listHistory(self.geometry)
                for hist in history:
                    types = pm.nodeType(hist, inherited=True)
                    if 'geometryFilter' in types:
                        if 'BlendShape' in pm.nodeType(hist, apiType=True):
                            bShapes.append(hist)

                if bShapes == []:
                    self.changeFeedback("No blend shape nodes were found on %s" % self.geometry, "red")
                    return
                else:
                    if len(bShapes) > 1:
                        # todo make a selection window if found multiple blend shapes
                        self.changeFeedback("Can't dreal with multimple blend shapes yet %s" % self.geometry, "red")
                        return
                    else:
                        self.bShapeName = bShapes[0]

        else:
            cmds.textField(self.widgets["object_name"], e=True, text="")
            if op is 1:
                cmds.textField(self.widgets["bsp_name"], e=True, text="")
                srm.makeSelectionWin()
                self.changeFeedback("Please select one object to add the Blend shape to", "red")
            return

        if op is 1:
            if (len(bShapes) > 0):
                if (len(bShapes) > 1):
                    self.bShapeSelectionWin(bShapes)
                else:
                    self.bShapeName = bShapes[0]
                    cmds.textField(self.widgets["bsp_name"], e=True, text=self.bShapeName.name())
            else:
                cmds.textField(self.widgets["bsp_name"], e=True, text="")
                self.changeFeedback('No blend shapes found on "%s"' % self.geometry.name(), "red")
                return

    def bspEditorFix(self, *args):
        self.defaultFeedback()
        op = cmds.radioButtonGrp(self.widgets["bsp_radio"], q=True, select=True)
        if op is 2:
            self.newBsp = True
        else:
            self.newBsp = False

    def defaultFeedback(self):
        self.changeFeedback("Blend Shape Editor")

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)

    def messegeButton(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        cmds.button(self.widgets["signalButton"], e=True, l=messege, bgc=bg)

    def bShapeSelectionWin(self, bShapes):
        if cmds.window("bspSel_win", exists=True):
            cmds.deleteUI("bspSel_win")
        self.widgets["bspSel_win"] = cmds.window("bspSel_win", title="Select Blend Shape", sizeable=1, rtf=True)
        self.widgets[("bspSel_main_Layout")] = cmds.rowColumnLayout(numberOfColumns=1, adj=True)
        bShapeNames = []
        for bsp in bShapes:
            bShapeNames.append(bsp.name())
        hight = 20 * len(bShapes)
        if hight < 100:
            hight = 100
        self.widgets["bspScroll"] = cmds.textScrollList(append=bShapeNames, allowMultiSelection=False, sii=1, w=250,
                                                        h=hight)
        cmds.button(l="Select Blend Shape", h=40, c=partial(self.bspWinSelection, bShapes))
        cmds.showWindow()
        cmds.window("bspSel_win", e=True, h=100)

    def bspWinSelection(self, bShapes, *args):
        idx = cmds.textScrollList(self.widgets["bspScroll"], query=True, selectIndexedItem=True)[0]
        idx -= 1
        cmds.textField(self.widgets["bsp_name"], e=True, text=bShapes[idx].name())
        self.bShapeName = bShapes[idx]
        cmds.deleteUI("bspSel_win")
