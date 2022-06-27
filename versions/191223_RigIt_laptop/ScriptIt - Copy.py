from maya import cmds, mel
from functools import partial
import os, sys
import pymel.core as pm
import generalMayaTools as gmt
import SI_BspEditor as BspEditor
import SI_AttrMaker as AttrMaker
import SI_ExtraScriptIt as ExtraScriptIt
import SI_ConnectionMaker as ConnectionMaker
import SI_LiteWrap as LiteWrap
import SI_ColorIt as ColorIt
import SI_Varianter as Varianter

reload(BspEditor)
reload(AttrMaker)
reload(ExtraScriptIt)
reload(ConnectionMaker)
reload(LiteWrap)
reload(ColorIt)
reload(Varianter)


class ScriptIt:

    def __init__(self, path=''):

        self.widgets = {}
        self.scriptIt(path + "/ScriptIt")

    def scriptIt(self, scriptItPath):
        if cmds.window("scriptIt_window", exists=True):
            cmds.deleteUI("scriptIt_window")

        # todo allow creating loops (should be able to receive lists/range etc)
        # todo enable python related tricks for making multiple connections/commands
        # todo make something that can check the imports (if more than pymel will be needed)

        self.widgets["scriptIt_window"] = cmds.window("scriptIt_window", title="Script It!",
                                                      sizeable=1)  # , rtf=True)
        cmds.columnLayout(adj=True)
        # cmds.scrollLayout(childResizable=True)
        # self.widgets["highLayout"] = cmds.paneLayout(configuration='vertical2')
        self.widgets["highLayout"] = cmds.rowColumnLayout(nc=2, adj=True, adjustableColumn=2)
        self.widgets["mainLayout"] = cmds.columnLayout(adj=True)
        self.widgets["scriptIt_tabLayout"] = cmds.tabLayout(childResizable=True)

        # add script makers
        parent = self.widgets["scriptIt_tabLayout"]

        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False, p=self.widgets["mainLayout"])


        Varianter.Varianter(parent, self)

        ExtraScriptIt.ExtraScriptIt(parent, scriptItPath)  # changes the width
        ColorIt.ColorIt(parent)
        BspEditor.BspEditor(parent)
        AttrMaker.AttrMaker(parent)
        ConnectionMaker.ConnectionMaker(parent)
        LiteWrap.LiteWrap(parent)

        self.scriptItButtons(self.widgets["mainLayout"], self.widgets["highLayout"])

        # todo keep track of nodes to enable writing the rest of the code

        # todo

        # todo make error bar

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
            script = BspEditor.BspEditor.getScript()
        if tab == "Attr_Maker":
            script = AttrMaker.AttrMaker.getScript()
        if tab == "Connections":
            script = ConnectionMaker.ConnectionMaker.getScript()
        if tab == "Lite_Wrap":
            script = LiteWrap.LiteWrap.getScript()
        if tab == "Color_It":
            script = ColorIt.ColorIt.getScript()
        if tab == "Varianter":
            script = Varianter.Varianter.getScript()
            cmds.scrollField(self.widgets["scriptItField"], e=True, text="")
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
# todo reference to this somewhere
# if you have shift held down = 1, ctl = 4, alt = 8
#mods = cmds.getModifiers()

# todo add following to script it
def easyCodingReferences(self, parent='None'):
    if parent == 'None':
        return "Can't load Function"
    self.widgets["codingReferences_frameLayout"] = cmds.frameLayout(label="Easy coding references", parent=parent,
                                                                    bgc=self.darkGreen, collapsable=True, cl=0)
    self.codingTextReferences()


def codingTextReferences(self):
    self.widgets["codingTextReferences_frameLayout"] = cmds.frameLayout(label="Text fonts :", bgc=self.mainBGC,
                                                                        collapsable=True, collapse=True, cl=0)
    cmds.columnLayout(w=200, bgc=[0.15, 0.17, 0.15])
    cmds.text(label="cmds.text(font='')")
    cmds.text(label="smallPlainLabelFont", font='smallPlainLabelFont')
    cmds.text(label="obliqueLabelFont", font='obliqueLabelFont')
    cmds.text(label="smallObliqueLabelFont", font='smallObliqueLabelFont')
    cmds.text(label="tinyBoldLabelFont", font='tinyBoldLabelFont')
    cmds.text(label="smallBoldLabelFont", font='smallBoldLabelFont')
    cmds.text(label="boldLabelFont", font='boldLabelFont')
    cmds.text(label="fixedWidthFont", font='fixedWidthFont')
    cmds.text(label="smallFixedWidthFont", font='smallFixedWidthFont')
