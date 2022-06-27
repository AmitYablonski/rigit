from maya import cmds, mel
import pymel.core as pm
import generalMayaTools as gmt
from functools import partial


class MassTools:

    def __init__(self):
        self.feedbackName = 'Mass Tools'
        self.colorBank()
        self.widgets = {}
        self.massWin()

    def colorBank(self):
        self.purple1 = [.55, .45, .8]
        self.purple2 = [.6, .5, .8]
        self.orange1 = [.9, .45, .5]
        self.green1 = [0.2, 0.6, .2]
        self.green2 = [0.4, 0.7, .3]

    def massWin(self):
        if cmds.window("mass_window", exists=True):
            cmds.deleteUI("mass_window")
        self.widgets["mass_window"] = cmds.window("mass_window", title=self.feedbackName, sizeable=1, rtf=True)
        mainLay = cmds.rowColumnLayout(nc=1)
        pm.separator(h=5)
        pm.text('Weapons of mass destruction')
        pm.separator(h=5)
        self.widgets["buttons_Layout"] = cmds.rowColumnLayout(nc=3, cs=[[2, 5], [3, 5]], rs=[[2, 7], [3, 7]])
        h = 70
        w = 90
        cmds.button(l="Filter Mesh\nSelection", h=h, w=w, bgc=self.green1, c=gmt.filterMeshSelection,
                    ann='Filters selection only to transforms that have a shape')
        cmds.button(l="Filter Mesh\nSelection\nHierarchy", h=h, w=w, bgc=self.green2,
                    c=partial(gmt.filterMeshSelection, True),
                    ann='Filters selection only to transforms that have a shape')
        cmds.button(l="Mass\nAttributes\nTransfer", h=h, w=w, bgc=self.purple1, c=self.MassAttrTransfer)
        cmds.button(l="instance\nto object", w=w, bgc=self.orange1, c=gmt.instanceToObject,  # , h=h
                    ann="converts selection from instances to objects")

        pm.separator(h=5, p=mainLay)
        pm.text('Tools to handle mass amount of objects', p=mainLay)
        pm.separator(h=5, p=mainLay)

        cmds.showWindow()

    def MassAttrTransfer(self, *args):
        import MassAttrTransfer
        reload(MassAttrTransfer)
        MassAttrTransfer.MassAttrTransfer()
