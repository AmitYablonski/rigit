from maya import cmds, mel
from functools import partial
import os, sys
import pymel.core as pm
import generalMayaTools as gmt

import SI_commonScripts as sic
import SINode_Base as nodeBase
import SINode_blendShape as BspNode
import SINode_AttrNode as AttrNode
import SI_ExtraScriptIt as ExtraScriptIt
import SINode_Connections as ConnectionNode
import SINode_LiteWrap as LiteWrap
import SINode_ColorIt as ColorNode

reload(sic)
reload(nodeBase)
reload(BspNode)
reload(AttrNode)
reload(ExtraScriptIt)
reload(ConnectionNode)
reload(LiteWrap)
reload(ColorNode)


class ScriptItMaster:

    def __init__(self, path=''):

        self._nodes = {}
        self.widgets = {}
        self.scriptIt(path + "/ScriptIt")

    def scriptIt(self, scriptItPath):
        if cmds.window("scriptIt_window", exists=True):
            cmds.deleteUI("scriptIt_window")

        # todo create node list
        # todo keep track of nodes to enable writing the rest of the code
        #   (if something needs to created first for connections etc)
        # todo allow creating loops (should be able to receive lists/range etc) enable python related tricks for making multiple connections/commands
        # todo add imports according to content
        # todo create an option (drop down menu) to export and load the setup

        self.widgets["scriptIt_window"] = cmds.window("scriptIt_window", title="Script It!",
                                                      sizeable=1)  # , rtf=True)
        cmds.columnLayout(adj=True)
        # cmds.scrollLayout(childResizable=True)
        # self.widgets["highLayout"] = cmds.paneLayout(configuration='vertical2')
        self.widgets["highLayout"] = cmds.rowColumnLayout(nc=3, adj=True, adjustableColumn=2)
        self.widgets["toolsLayout"] = cmds.rowColumnLayout(nc=1, adj=True)
        self.widgets["mainLayout"] = cmds.columnLayout(adj=True, p=self.widgets["highLayout"])
        self.widgets["scriptIt_tabLayout"] = cmds.tabLayout(childResizable=True, p=self.widgets["mainLayout"])
        # This is where the node will sit when created
        self.widgets["nodesLayout"] = cmds.rowColumnLayout(nc=1, p=self.widgets["mainLayout"])
        '''
        # add script makers
        parent = self.widgets["scriptIt_tabLayout"]

        ExtraScriptIt.ExtraScriptIt(parent, scriptItPath)  # changes the width
        ColorNode.ColorNode(parent)
        BspNode.BspNode(parent)
        AttrNode.AttrNode(parent)
        ConnectionNode.ConnectionNode(parent)
        LiteWrap.LiteWrap(parent)

        '''
        self.populateTools(self.widgets["toolsLayout"])
        self.scriptItButtons(self.widgets["mainLayout"], self.widgets["highLayout"])

        # todo

        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False, p=self.widgets["mainLayout"])
        cmds.showWindow()
        cmds.window(self.widgets["scriptIt_window"], edit=True, h=400)  # , w=425
        self.defaultFeedback()

    def scriptItButtons(self, parent1, parent2):
        width = 600
        hight = 400
        # this is the buttons and scrollfield for script it
        cmds.separator(h=7, p=parent1)  # w=width
        scriptItButtons = cmds.rowColumnLayout(nc=3, adj=True, p=parent1)
        # cmds.columnLayout(adj=False)
        cmds.button(w=199, l="Script it!", c=partial(self.addScript, False))
        cmds.separator(w=30, vis=False)
        # cmds.columnLayout(adj=True, p=scriptItButtons)
        cmds.button(w=199, l="add to script!", c=partial(self.addScript, True))
        # cmds.separator(w=1, vis=False)
        # Data Type
        cmds.columnLayout(parent=parent2, adj=True)
        self.widgets["scriptIt_frameLayout"] = cmds.frameLayout(label="Script:", collapsable=False)  # , w=width)
        cmds.rowColumnLayout(adj=True)  # todo set default width without it becoming the minimum
        self.widgets["scriptItField"] = cmds.scrollField(h=645, w=550)

        cmds.separator(h=7, p=parent1)  # w=width

    def addScript(self, add, *args):
        self.defaultFeedback()
        newText = True
        if add:
            text = cmds.scrollField(self.widgets["scriptItField"], query=True, text=True)
            if text != '':
                newText = False
        if newText:
            cmds.scrollField(self.widgets["scriptItField"], e=True, text="")
            cmds.scrollField(self.widgets["scriptItField"], e=True, it="import pymel.core as pm\n" +
                                                                       "from maya import cmds, mel\n\n\n")
        else:
            cmds.scrollField(self.widgets["scriptItField"], e=True, it="\n\n")

        # todo tab should return an error to communicate with the error or return script if everything is fine
        # check current tab
        script = ""
        tab = cmds.tabLayout(self.widgets["scriptIt_tabLayout"], q=True, selectTab=True)
        if tab == "Blend_Shape":
            script = BspNode.BspNode()
        if tab == "Attr_Maker":
            script = AttrNode.AttrNode.getScript()
        if tab == "Connections":
            script = ConnectionNode.ConnectionNode.getScript()
        if tab == "Lite_Wrap":
            script = LiteWrap.LiteWrap.getScript()
        if tab == "Color_It":
            script = ColorNode.ColorNode.getScript()
        if script:
            cmds.scrollField(self.widgets["scriptItField"], e=True, it=script)
            self.changeFeedback("Script imported from %s" % tab, "green")
        else:
            self.changeFeedback("Script isn't compiled, please compile before adding it.", "red")
            return
        ''' current tabs
        Extra
        Blend_Shape
        Attr_Maker
        Connections
        Lite_Wrap
        '''
        return

    def addNode(self, node, *args):
        if node == "Tester":
            newNode = nodeBase.SIBase(self)
        if node == "Blend_Shape":
            newNode = BspNode.BspNode(self)
        if node == "Attr_Maker":
            newNode = AttrNode.AttrNode(self)
        if node == "Connections":
            newNode = ConnectionNode.ConnectionNode(self)
        if node == "Lite_Wrap":
            newNode = LiteWrap.LiteWrap(self)
        if node == "Color_It":
            newNode = ColorNode.ColorNode(self)
        # todo possibly clear the layout and recreate it  according to the in/outputs
        # todo a drop down list / window that will allow choosing an input from one of the existing nodes or string ("name.attr")
        cmds.rowColumnLayout(nc=2, p=self.widgets["nodesLayout"])
        self._nodes[newNode] = cmds.button(c=newNode.settings)
        name = newNode.getNodeName()
        self.updateButtonName(newNode, name)

    def updateButtonName(self, node, name):
        cmds.button(self._nodes[node], e=True, l=name)

    def populateTools(self, parent1):
        pm.separator(h=3, st='double', p=parent1)
        pm.text("ToolBox", font='boldLabelFont', p=parent1)
        pm.separator(h=3, st='double', p=parent1)
        pm.separator(h=3, p=parent1, vis=False)
        nodesList = ["Tester", "Blend_Shape", "Attr_Maker", "Connections", "Lite_Wrap", "Color_It"]
        for node in nodesList:
            pm.button(l=node, p=parent1, c=partial(self.addNode, node))
        # todo the toolsPopulate is where we will call the "script blocks" that will give us in/outputs
        return

    def defaultFeedback(self):
        self.changeFeedback("ScriptIt!")

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)


# todo create "import " and LiteWrap in script it
'''
cmds.file("P:/MBA/assets/characters/beaker/rigging/customSteps/lapelFiles/lapelCollider9.ma",
          i=True, typ="mayaAscii", ignoreVersion=True, rpr="collider")

collider = ""
heavyMesh = ""
deleteFaces = ""
wrapper = gmt.liteWrap(objToWrap, heavyMesh, deleteFaces)[0]
'''
