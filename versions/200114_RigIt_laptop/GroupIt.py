from maya import cmds, mel
import pymel.core as pm
from functools import partial


class GroupIt:

    def __init__(self):

        self.selection = []
        self.widgets = {}
        self.groupItWin()

    def groupItWin(self):
        if cmds.window("groupIt_window", exists=True):
            cmds.deleteUI("groupIt_window")
        self.widgets["groupIt_window"] = cmds.window("groupIt_window", title="Group It", sizeable=1, rtf=True)
        self.widgets["group_main_Layout"] = cmds.rowColumnLayout(numberOfColumns=1)
        self.widgets["group_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=2, cw2=[100, 100], select=2,
                                                          labelArray2=['Add Prefix', 'Suffix'])  #, onc=self.groupItFix)
        self.widgets["group_Layout"] = cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(l="Group It", c=self.groupIt, p=self.widgets["group_Layout"])
        self.widgets["group_text"] = cmds.textField(text="_npo", p=self.widgets["group_Layout"])
        pm.separator(vis=False)
        cmds.rowColumnLayout(nc=3, cs=[[2,1],[3,1]], rs=[[2,1],[3,1]])
        pm.button('_root', c=partial(self.changeText, '_root'))
        pm.button('_cns', c=partial(self.changeText, '_cns'))
        pm.button('_npo', c=partial(self.changeText, '_npo'))
        pm.button('_auto', c=partial(self.changeText, '_auto'))
        pm.button('_fix', c=partial(self.changeText, '_fix'))
        pm.button('_grp', c=partial(self.changeText, '_grp'))
        pm.button('_rot', c=partial(self.changeText, '_rot'))
        pm.button('_trans', c=partial(self.changeText, '_trans'))
        pm.button('_scale', c=partial(self.changeText, '_scale'))

        cmds.showWindow()

    def changeText(self, text, *args):
        cmds.textField(self.widgets["group_text"], e=True, text=text)

    def groupIt(self, *args):
        selection = pm.ls(sl=True)
        op = cmds.radioButtonGrp(self.widgets["group_radio"], q=True, select=True)
        grpText = cmds.textField(self.widgets["group_text"], q=True, tx=True)
        for sel in selection:
            parent1 = pm.listRelatives(sel, p=True)
            if parent1:
                grp = pm.group(em=True, p=parent1[0])
            else:
                grp = pm.group(em=True)
            ####### get its position instead of mel.eval
            if op == 1:
                pm.rename(grp, grpText + sel)
            else:
                pm.rename(grp, sel + grpText)
            pm.select(sel, grp)
            mel.eval("delete`parentConstraint`")
            pm.parent(sel, grp)

    def groupItFix(self, *args): # todo this...
        op = cmds.radioButtonGrp(self.widgets["group_radio"], q=True, select=True)
        grpText = cmds.textField(self.widgets["group_text"], q=True, tx=True)
        print op
        print grpText
        '''
        if op == 1 and grpText == "_grp":
            cmds.textField(self.widgets["group_text"], edit=True, tx="grp_")
        if op == 2 and grpText == "grp_":
            cmds.textField(self.widgets["group_text"], edit=True, tx="_grp")
        '''