from maya import cmds, mel
import pymel.core as pm
import SnowRigMethodsUI as srm

reload(srm)


class Varianter:

    def __init__(self):

        self.varPath = "C:/Users/3dami/Documents/maya/2018/temp_deleteIt"
        self.varDict = {}
        self.widgets = {}
        self.varianterWin()

    def varianter(self):
        if cmds.window("varianter_window", exists=True):
            cmds.deleteUI("varianter_window")
        self.widgets["varianter_window"] = cmds.window("varianter_window", title="Variater", sizeable=1, rtf=True)
        self.widgets["group_main_Layout"] = cmds.rowColumnLayout(numberOfColumns=1)
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.text('Characters:')
        cmds.text('Variants:')
        self.widgets["char_scroll"] = cmds.textScrollList(allowMultiSelection=False, w=130, h=120,
                                                          sc=self.varListUpdate)
        self.widgets["var_scroll"] = cmds.textScrollList(allowMultiSelection=False, w=130, h=120,
                                                         sc=self.varSelected)
        self.widgets["group_Layout"] = cmds.rowColumnLayout(numberOfColumns=2)
        self.widgets["group_text"] = cmds.textField(text="")
        cmds.button(l="Runner", c=self.varianter)

        self.initializeVariants()
        cmds.showWindow()

    def initializeVariants(self):
        folders = srm.getFoldersFromPath(self.varPath)
        for fol in folders:
            pre, _, suf = fol.partition('_')
            if pre not in self.varDict:
                self.varDict[pre] = []
                self.varDict[pre].append(suf)
        for char in self.varDict:
            cmds.textScrollList(self.widgets['char_scroll'], e=True, append=char)

    def varSelected(self, *args):
        selected = cmds.textScrollList(self.widgets["char_scroll"], query=True, selectItem=True)
        if selected:
            selected = selected[0]

    def varListUpdate(self, *args):
        selected = cmds.textScrollList(self.widgets["char_scroll"], query=True, selectItem=True)
        cmds.textScrollList(self.widgets["var_scroll"], e=True, removeAll=True)
        if selected:
            selected = selected[0]
        else:
            return
        for var in self.varDict[selected]:
            cmds.textScrollList(self.widgets['var_scroll'], e=True, append=var)

    def varianter(self, *args):
        selection = pm.ls(sl=True)
        grpText = cmds.textField(self.widgets["group_text"], q=True, tx=True)
