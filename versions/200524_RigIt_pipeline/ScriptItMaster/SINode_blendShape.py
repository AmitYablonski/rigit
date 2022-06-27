from maya import cmds, mel
import pymel.core as pm
from functools import partial
import SnowRigMethodsUI as srm
import SINode_Base as SIBase
import generalMayaTools as gmt
import SI_commonScripts as sic


# todo make the UI remember the parameters
class BspNode(SIBase.SIBase):
    _nodeName = "bspNode"
    _addToBsp = False
    _bspName = ""
    _objName = ""
    _bspToAdd = ""
    _delete = False
    _turnOn = True
    _multipleBsp = False

    def __init__(self, parentNode):

        SIBase.SIBase.__init__(self, parentNode)
        self._defaultFeedback = "Blend Shape Editor"
        self._showScript = self._defaultFeedback
        self.defaultFeedback()
        # todo update that the script isn't compiled
        # todo add attributes according to base class methods (addInput etc..)
        # TODO make it possible to connect to a named string or an input from another SINode

    def editor(self, parent1):

        self.widgets["mainLayout"] = cmds.columnLayout("Blend Shape", adj=True, p=parent1)
        if self._addToBsp:
            idx = 2
        else:
            idx = 1
        self.widgets["bsp_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=2, select=idx,  # , cw2=[100, 100]
                                                        labelArray2=['New', 'Add to existing'], onc=self.bspEditorFix)
        cmds.separator(h=7)
        self.widgets["bspName_rowLayout"] = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[1, 80],
                                                           p=self.widgets["mainLayout"])
        self.widgets["bspText"] = cmds.text("bspText", l="Bsp Name:")
        self.widgets["bsp_name"] = cmds.textField(tx=self._bspName, cc=partial(self.updateFromField, "bsp_name"))
        self.widgets["group_rowLayout"] = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[1, 80],
                                                         p=self.widgets["mainLayout"])
        cmds.text("Object Name:")
        self.widgets["object_name"] = cmds.textField(tx=self._objName, cc=partial(self.updateFromField, "object_name"))
        cmds.rowLayout(numberOfColumns=2, p=self.widgets["mainLayout"])
        cmds.button(l="Add names from selection", w=140, c=self.addNameSelection)
        cmds.separator(vis=False)

        cmds.separator(h=7, p=self.widgets["mainLayout"])
        self.widgets["bspName_rowLayout"] = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[1, 80],
                                                           p=self.widgets["mainLayout"])
        cmds.text("Blend Shape/s:")
        if self._bspToAdd:
            if isinstance(self._bspToAdd, list) or isinstance(self._bspToAdd, tuple):
                tx = gmt.stringMyPmList(self._bspToAdd)
            elif isinstance(self._bspToAdd, pm.PyNode):
                tx = self._bspToAdd.name()
            else:
                tx = self._bspToAdd
        else:
            tx = ""
        self.widgets["bspToAdd"] = cmds.textField(tx=tx, cc=partial(self.updateFromField, "bspToAdd"))
        cmds.rowLayout(numberOfColumns=2, p=self.widgets["mainLayout"])
        cmds.button(l="Add shapes from selection", w=140, c=self.addBspSelection)
        cmds.separator(vis=False)

        cmds.separator(h=7, p=self.widgets["mainLayout"])
        # todo change command to update the delete/tunrOn variables
        self.widgets["turnOn_checkBox"] = cmds.checkBox('Turn on blend shape after adding it', v=self._turnOn,
                                                        p=self.widgets["mainLayout"],
                                                        cc=partial(self.updateCheckBoxes, "turnOn_checkBox"))
        self.widgets["delete_checkBox"] = cmds.checkBox('Delete blend shape after adding it', v=self._delete,
                                                        p=self.widgets["mainLayout"],
                                                        cc=partial(self.updateCheckBoxes, "delete_checkBox"))

        # todo? self.widgets["signalButton"] = cmds.button(w=199, l="not compiled", bgc=[.5,.5,.5])
        cmds.separator(w=400, h=7, p=self.widgets["mainLayout"])
        '''
        cmds.columnLayout(p=self.widgets["mainLayout"], adj=True)
        self.widgets["dataType_frameLayout"] = cmds.frameLayout(label="Script:", collapsable=False, w=400)
        cmds.rowColumnLayout(adj=True)
        self.widgets["scriptField"] = cmds.scrollField(h=200)
        '''

    def customScriptIt(self, *args):
        '''
        :return: the compiled script
        '''
        # check if geometries and blend shapes were selected or named

        if not self._objName:
            self.changeFeedback("No geometry was assigned", "red")
            return
        if not self._bspToAdd:
            self.changeFeedback("No blend shape geometries were assigned", "red")
            return
        if self._addToBsp and self._multipleBsp:
            script = self.getFindIdx()
        else:
            script = ""
        if self._addToBsp and not self._bspName:
            self.changeFeedback("No blend shape name wes assigned", "red")
        # start of script creation (excluding import)
        script += 'geometry = "%s"\n' % self._objName  # geo with the bsp node
        if isinstance(self._bspToAdd, list) or isinstance(self._bspToAdd, tuple):
            script += 'bShapeGeo = %s\n' % gmt.stringMyPmList(self._bspToAdd, True)  # True will be PyNode
        else:
            script += 'bShapeGeo = "%s"\n' % self._bspToAdd  # todo make it PyNode?
        if self._addToBsp:  # add to existing
            script += 'bShapeName = pm.PyNode("%s")\n' % self._bspName
            if self._multipleBsp:
                script += "pos = bspFreeIndex(bShapeName)  # position to add to the bsp node\n"
            # add bShapes command
            script += "# add to blend shape\n"
            if isinstance(self._bspToAdd, list) or isinstance(self._bspToAdd, tuple):
                script += "for bsp in bShapeGeo:\n"
                # todo find pos command
                script += "\tpm.blendShape(bShapeName, edit=True, t=[geometry, pos, bsp, 1.0])\n"
                # todo possibly add this in the loop: "pos = bspFreeIndex(bShapeName)"
                script += "\tpos += 1\n"
            else:
                script += "pm.blendShape(bShapeName, edit=True, t=[geometry, pos, bShapeGeo, 1.0])\n"

        else:  # create new
            # todo check if name is given, else, name it "properly"
            script += '# Create new blendShape\nbShape = pm.blendShape(bShapeGeo, geometry, n="bsp_name")[0]\n'
        if self._turnOn:
            script += '# turn bShapes on\n'
            # todo if multiple bsp geometries, make a loop, else:
            if isinstance(self._bspToAdd, list) or isinstance(self._bspToAdd, tuple) or \
                    self._bspToAdd.partition(",")[1] == ",":
                script += 'for bsp in bShapeGeo:\n'
                script += '\tbShape.setAttr(bsp, 1)\n'
            else:
                script += 'bShape.setAttr(bShapeGeo, 1)\n'
        if self._delete:
            script += "pm.delete(bShapeGeo)\n"
        return script

    def getFindIdx(self):
        script = "# find the first available index in bsp\n" \
                 "def bspFreeIndex(bsp):\n\t" \
                     "targetList = pm.aliasAttr(bsp, query=True)\n\t" \
                     "targetNums = []\n\t" \
                     "for i in targetList[1::2]:\n\t\t" \
                         "num = i.split('[')[-1][:-1]\n\t\t" \
                         "targetNums.append(int(num))\n\t" \
                     "i = 0\n\t" \
                     "while (i < 200):\n\t\t" \
                         "if i not in targetNums:\n\t\t\t" \
                             "break\n\t\t" \
                         "i += 1\n\t" \
                     "return i\n\n"
        return script

    def bspEditorFix(self, *args):
        self.defaultFeedback()
        op = cmds.radioButtonGrp(self.widgets["bsp_radio"], q=True, select=True)
        if op is 2:
            self._addToBsp = True
        else:
            self._addToBsp = False

    def updateCheckBoxes(self, field, *args):
        state = cmds.checkBox(self.widgets[field], query=True, v=True)
        if field is "turnOn_checkBox":
            self._turnOn = state
        if field is "delete_checkBox":
            self._delete = state

    def updateFromField(self, field, *args):
        # todo update that the script isn't compiled
        newTx = cmds.textField(self.widgets[field], q=True, tx=True)
        if field is "bsp_name":
            self._bspName = newTx
        if field is "object_name":
            self._objName = newTx
        if field is "bspToAdd":
            self._bspToAdd = newTx

    def addBspSelection(self, *args):
        # todo update that the script isn't compiled
        self.defaultFeedback()
        sel = pm.ls(sl=True)
        if len(sel) >= 1:
            temp = ""
            if len(sel) > 1:
                self._bspToAdd = sel
                self._multipleBsp = True
                temp = gmt.stringMyPmList(sel)
            else:
                self._bspToAdd = sel[0]
                temp += sel[0].name()
            cmds.textField(self.widgets["bspToAdd"], e=True, text=temp)
        else:
            srm.makeSelectionWin()
            self.changeFeedback("Make a selection and try again", "red")

    def addNameSelection(self, *args):
        # todo update that the script isn't compiled
        self.defaultFeedback()
        selection = pm.ls(sl=True)
        if len(selection) is 1:
            geo = selection[0]
            self._objName = geo.name()
            cmds.textField(self.widgets["object_name"], e=True, text=self._objName)
            # todo filter it to inputs only!  <<---  ha?!
            if self._addToBsp:  # look for blend shapes nodes
                self.findBlendSahpes(geo)
        else:
            srm.makeSelectionWin()
            self.changeFeedback("Select a single object to add the Blend shape to", "red")

    def findBlendSahpes(self, obj):
        self.changeFeedback("looking for blendShapes on %s" % obj.name())
        bShapes = []
        history = pm.listHistory(obj)
        # Search on object's history for blend shape nodes
        for hist in history:
            types = pm.nodeType(hist, inherited=True)
            if 'geometryFilter' in types:
                if 'BlendShape' in pm.nodeType(hist, apiType=True):
                    bShapes.append(hist)
        if (len(bShapes) > 0):
            if (len(bShapes) > 1):
                self.bShapeSelectionWin(bShapes)
            else:
                # todo check if it's better keeping it a PyNode (probably not to enable working without a scene)
                self._bspName = bShapes[0].name()
                cmds.textField(self.widgets["bsp_name"], e=True, text=self._bspName)
        else:
            cmds.textField(self.widgets["bsp_name"], e=True, text="")
            self.changeFeedback('No blend shapes found on "%s"' % obj.name(), "red")

    def bShapeSelectionWin(self, bShapes):  # todo check if this still works (changed to pm)
        if pm.window("bspSel_win", exists=True):
            pm.deleteUI("bspSel_win")
        self.widgets["bspSel_win"] = pm.window("bspSel_win", title="Select Blend Shape", sizeable=1, rtf=True)
        self.widgets[("bspSel_main_Layout")] = cmds.rowColumnLayout(numberOfColumns=1, adj=True)
        bShapeNames = []
        for bsp in bShapes:
            bShapeNames.append(bsp.name())
        hight = 20 * len(bShapes)
        if hight < 100:
            hight = 100
        self.widgets["bspScroll"] = pm.textScrollList(append=bShapeNames, allowMultiSelection=False,
                                                      sii=1, w=250, h=hight)
        pm.button(l="Select Blend Shape", h=40, c=partial(self.bspWinSelection, bShapes))
        pm.showWindow()
        pm.window(self.widgets["bspSel_win"], e=True, h=100)

    def bspWinSelection(self, bShapes, *args):
        idx = pm.textScrollList(self.widgets["bspScroll"], query=True, selectIndexedItem=True)[0]
        idx -= 1
        pm.textField(self.widgets["bsp_name"], e=True, text=bShapes[idx].name())
        # todo check if it's better keeping it a PyNode
        self._bspName = bShapes[idx].name()
        pm.deleteUI("bspSel_win")
