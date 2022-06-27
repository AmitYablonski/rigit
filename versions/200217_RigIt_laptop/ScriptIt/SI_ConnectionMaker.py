from maya import cmds, mel
import pymel.core as pm
from functools import partial
#import RigItMethodsUI as rim


class ConnectionMaker:

    def __init__(self, parent):

        # todo find a way to create multiply/divide/plus/minus/etc..
        # todo find a way to setup the rest of the node (set attribute defaults)
        self.typeNames = {'transform': 'newGrp', 'multiplyDivide': 'multNode', 'condition': 'conNode',
                          'reverse': 'revNode', 'choice': 'choiceNode', 'plusMinusAverage': 'plusMin'}
        self.nodeTypes = []
        for type in self.typeNames:
            self.nodeTypes.append(type)

        self.attributesIn = {'transform': ['translate', 'tx', 'ty', 'tz',
                                           'rotate', 'rx', 'ry', 'rz',
                                           'scale', 'sx', 'sy', 'sz', 'visibility'],
                             'multiplyDivide': ['input1', 'i1x', 'i1y', 'i1z',
                                                'input2', 'i2x', 'i2y', 'i2z'],
                             'condition': ['firstTerm', 'secondTerm',
                                           'colorIfTrue', 'colorIfTrueR', 'colorIfTrueG', 'colorIfTrueB',
                                           'colorIfFalse', 'colorIfFalseR', 'colorIfFalseG', 'colorIfFalseB'],
                             'reverse': ['input', 'inputX', 'inputY', 'inputZ'],
                             'choice': ['selector', 'input', 'input[0]', 'input[1]', 'input[2]'],
                             'plusMinusAverage': ['i1[0]', 'i1[1]', 'i1[1]', 'i1[1]']}
        self.attributesOut = {'transform': self.attributesIn['transform'],
                              'multiplyDivide': ['output', 'ox', 'oy', 'oz'],
                              'condition': ['outColor', 'outColorR', 'outColorG', 'outColorB'],
                              'reverse': ['output', 'ox', 'oy', 'oz'],
                              'choice': ['output'],
                              'plusMinusAverage': ['o1', 'o3']}
        self.widgets = {}
        self.connectionMaker(parent)

    def connectionMaker(self, parent='None'):
        if parent == 'None':
            return ("Can't load ConnectionMaker")
        self.widgets["connections_mainLayout"] = cmds.columnLayout("Connections", p=parent, adj=True)

        pm.text("Select Node type and attributes to connect", h=30)

        self.widgets["connections_menuLayout"] = cmds.rowColumnLayout(nc=3, adj=True, adjustableColumn=2,
                                                                      p=self.widgets["connections_mainLayout"])

        # names
        cmds.text(" Node1 Name:", al="left", p=self.widgets["connections_menuLayout"])
        cmds.separator(vis=False, p=self.widgets["connections_menuLayout"])
        cmds.text(" Node2 Name:", al="left", p=self.widgets["connections_menuLayout"])
        self.widgets["nameLine1"] = cmds.textField(w=120, p=self.widgets[
            "connections_menuLayout"])  # , cc=self.nameTextChange)
        cmds.separator(vis=False, p=self.widgets["connections_menuLayout"])
        self.widgets["nameLine2"] = cmds.textField(w=120, p=self.widgets[
            "connections_menuLayout"])  # , cc=self.nameTextChange)

        # nodes and attribute lists
        layout1 = cmds.rowColumnLayout(nc=2, adj=True, p=self.widgets["connections_menuLayout"])
        #cmds.separator(w=18, vis=False, p=self.widgets["connections_menuLayout"])
        pm.text(">>", p=self.widgets["connections_menuLayout"])
        layout2 = cmds.rowColumnLayout(nc=2, adj=True, p=self.widgets["connections_menuLayout"])

        # 1st node selection scroll
        cmds.rowColumnLayout(nr=2, adj=True, p=layout1, rh=[1, 20])
        self.widgets["newNode1_checkBox"] = cmds.checkBox('Create Node', v=True)
        scrollW = 100
        self.widgets["nodes1_scroll"] = cmds.textScrollList(append=self.nodeTypes, allowMultiSelection=False, w=scrollW,
                                                            sc=partial(self.nodeTypeUpdate, 1))
        cmds.rowColumnLayout(nr=2, adj=True, p=layout1, rh=[1, 20])
        pm.text("Out Attribute:", al="left")  # todo make sure multi selection works (next line)
        self.widgets["attrs1_scroll"] = cmds.textScrollList(append=[], allowMultiSelection=True, w=scrollW)
        # 2nd node selection scroll
        cmds.rowColumnLayout(nr=2, adj=True, p=layout2, rh=[1, 20])
        self.widgets["newNode2_checkBox"] = cmds.checkBox('Create Node', v=True)
        self.widgets["nodes2_scroll"] = cmds.textScrollList(append=self.nodeTypes, allowMultiSelection=False, w=scrollW,
                                                            sc=partial(self.nodeTypeUpdate, 2))
        cmds.rowColumnLayout(nr=2, adj=True, p=layout2, rh=[1, 20])
        pm.text("In Attribute:", al="left")  # todo make sure multi selection works (next line)
        self.widgets["attrs2_scroll"] = cmds.textScrollList(append=[], allowMultiSelection=True, w=scrollW)


        # bottom buttons and field
        cmds.separator(h=7, p=self.widgets["connections_mainLayout"])
        scriptItButtons = cmds.rowColumnLayout(nc=2, adj=True, p=self.widgets["connections_mainLayout"])
        cmds.columnLayout(adj=False)
        cmds.button(w=199, l="Compile Script!", c=partial(self.scriptIt, False))
        cmds.columnLayout(adj=True, p=scriptItButtons)

        cmds.separator(h=7, p=self.widgets["connections_mainLayout"])
        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False,
                                                           p=self.widgets["connections_mainLayout"])
        self.defaultFeedback()

    @staticmethod
    def getScript(*args):
        if script:
            return script
        else:
            return False

    def scriptIt(self, *args):
        self.defaultFeedback()
        name1 = cmds.textField(self.widgets["nameLine1"], q=True, tx=True)
        name2 = cmds.textField(self.widgets["nameLine2"], q=True, tx=True)

        # check name
        if not name1 or not name2:
            self.changeFeedback("Missing node name", "red")
            return
        script = ""

        # check if type and attribute are selected
        newNode1 = cmds.checkBox(self.widgets["newNode1_checkBox"], query=True, v=True)
        type1 = cmds.textScrollList(self.widgets["nodes1_scroll"], query=True, selectItem=True)
        attr1 = cmds.textScrollList(self.widgets["attrs1_scroll"], query=True, selectItem=True)
        newNode2 = cmds.checkBox(self.widgets["newNode2_checkBox"], query=True, v=True)
        type2 = cmds.textScrollList(self.widgets["nodes2_scroll"], query=True, selectItem=True)
        attr2 = cmds.textScrollList(self.widgets["attrs2_scroll"], query=True, selectItem=True)
        if not type1 or not attr1:
            self.changeFeedback("Please select node1 type and attribute", "red")
            return
        if not type2 or not attr2:
            self.changeFeedback("Please select node2 type and attribute", "red")
            return
        nodeType1 = self.typeNames[type1[0]]
        if newNode1:
            script += "%s = pm.shadingNode('%s', asUtility=True, name='%s')\n" % (nodeType1, type1[0], name1)
        else:  # todo check if possible to avoid writing the variable line below if already written
            script += "%s = pm.PyNode('%s')\n" % (nodeType1, name1)
        # to avoid name clashings - checks both node types
        nodeType2 = self.typeNames[type2[0]]
        if type1[0] == type2[0]:
            nodeType2 += "2"
        if newNode2:
            script += "%s = pm.shadingNode('%s', asUtility=True, name='%s')\n" % (nodeType2, type2[0], name2)
        else:
            script += "%s = pm.PyNode('%s')\n" % (nodeType2, name2)
        # todo enable connecting to several attrs
        script += "pm.connectAttr(%s.%s, %s.%s)\n" % (nodeType1, attr1[0], nodeType2, attr2[0])
        #script += "%s.%s >> %s.%s\n" % (nodeType1, attr1[0], nodeType2, attr2[0])
        global script
        self.changeFeedback("Compiled!", "green")

    def nodeTypeUpdate(self, num):
        # todo update attrs scroll list (populate)
        nodeType = cmds.textScrollList(self.widgets["nodes" + str(num) + "_scroll"], query=True, selectItem=True)[0]
        cmds.textScrollList(self.widgets["attrs" + str(num) + "_scroll"], e=True, removeAll=True)
        if num == 1:  # update attr1
            for attr in self.attributesOut[nodeType]:
                cmds.textScrollList(self.widgets["attrs1_scroll"], e=True, append=attr)
        else:  # update attr2
            for attr in self.attributesIn[nodeType]:
                cmds.textScrollList(self.widgets["attrs2_scroll"], e=True, append=attr)

    def newNodeChange(self, set, *args):
        self.defaultFeedback()
        self.newNode1[set] = cmds.checkBox(self.widgets["newNode" + set(i) + "_checkBox"], q=True, v=True)

    def defaultFeedback(self):
        self.changeFeedback("Connection Maker/Editor")

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)

    def bspWinSelection(self, bShapes, *args):
        idx = cmds.textScrollList(self.widgets["bspScroll"], query=True, selectIndexedItem=True)[0]
        idx -= 1
        cmds.textField(self.widgets["bsp_name"], e=True, text=bShapes[idx].name())
        self.bShapeName = bShapes[idx]
        cmds.deleteUI("bspSel_win")
