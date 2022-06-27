from maya import cmds, mel
import pymel.core as pm
import os, sys
from functools import partial
import re
import SnowballTools as sbt
import generalMayaTools as gmt
import generalMayaPrints as gmp
import RigItMethodsUI as rim
import mGearMethods as mgm
# todo import setupRigIt
import mgear
import mGear_utils
import mgear.maya.synoptic as syn

reload(sbt)
reload(gmt)
reload(gmp)
reload(rim)
reload(mgm)


# TODO possibly set hotkeys

class RigItUI:

    def __init__(self, path=''):

        # this allows the order of selection
        pm.selectPref(trackSelectionOrder=1)

        if cmds.dockControl("RigIt_dockControl", exists=True):
            cmds.deleteUI("RigIt_dockControl")

        if path:
            self.scriptsPath = path
        else:  # this will only work locally from the user scripts folder
            self.scriptsPath = cmds.internalVar(usd=True)

        self.rigItImports()

        self.iconPath = self.scriptsPath + "/icons/"
        self.mainFramesLayouts = {}
        self.secFramesLayouts = {}
        self.set1rowColumnLayouts = {}
        self.set1frameLayouts = {}
        self.set1rowLayouts = {}
        self.set1buttons = {}
        self.set2rowColumnLayouts = {}
        self.set2frameLayouts = {}
        self.set2rowLayouts = {}
        self.set2buttons = {}
        self.widgets = {}
        self.sWidgets = {}
        self.tabs = []
        self.buildRigItUI()

        # cmds.showWindow(self.widgets["window"])
        self.widgets["RigIt_dock"] = cmds.dockControl("RigIt_dockControl", label="Snowball Rigging", area='right',
                                                      bgc=self.dockBGC, allowedArea='right',
                                                      content=self.widgets["window"])
        print("RigIt - Rigging Toolbox is opened")

    def rigItImports(self):
        for pFolder in ["/RigItUI", "/ScriptIt"]:
            path = self.scriptsPath + pFolder
            if os.path.exists(path):
                if not path in sys.path:
                    sys.path.append(path)

    def buildRigItUI(self):
        self.colorAndSizeLibrary()
        self.mainLayoutSetup()
        self.dropDownMenuSetup()
        self.mayaMenuesPopulate()
        self.mayaToolsPopulate()
        self.pipelineToolsPopulate()

    def mayaToolsPopulate(self):
        parent = self.widgets["Maya_Tools_frameLayout"]
        self.externalTools(parent)
        self.shelfTools(parent)
        self.funkyTools(parent)
        self.handyRiggingTools(parent)
        # todo selectionTools
        self.handyPrints(parent)
        self.cleanupTools(parent)
        self.collectiveTools(parent)

    def pipelineToolsPopulate(self):
        parent = self.widgets["Pipeline_Tools_frameLayout"]
        self.snowballToolsFrame(parent)

    def mayaMenuesPopulate(self):
        parent = self.widgets["mayaMenues_frameLayout"]
        self.mayaMenuesSetup(parent)

    def colorAndSizeLibrary(self):
        self.paleGreen = [0.23, 0.26, 0.23]
        self.brightGreen = [0.1, 0.65, 0.1]
        self.darkGreen = [0.05, 0.2, 0.05]
        self.mediumGreen = [0.08, 0.223, 0.089]
        self.warningRed = [0.5783, 0.1247, 0.1247]
        self.mediumGreen2 = [0.0, 0.25, 0.0]
        self.mediumBlue = [0.15, 0.15, 0.45]
        # turqeeez = [0.05, 0.2, 0.2]
        # color associations:
        self.mayaDarkGrey = [.19, .19, .19]
        self.mayaDarkGrey2 = [.23, .23, .23]
        self.mayaBrightGrey = [.58, .58, .58]
        self.grey = [.27, .27, .27]
        self.dockBGCDef = self.mayaDarkGrey
        self.dockBGC = self.dockBGCDef
        self.mainBGCDef = self.mayaDarkGrey
        self.mainBGC = self.mainBGCDef
        # self.mainFramesDef = [.37, .37, .37]
        self.mainFramesDef = [0.105, 0.217, 0.423]
        self.mainFrames = self.mainFramesDef
        # self.secFramesDef = [0.29, 0.29, 0.29]
        # self.secFramesDef = [0.038, 0.258, 0.045] # old green
        self.secFramesDef = [0.15, 0.23, 0.15]
        self.secFrames = self.secFramesDef
        self.buttonColor1Def = self.mayaDarkGrey2
        self.buttonColor1 = self.buttonColor1Def
        self.buttonColor2Def = self.mayaDarkGrey2
        self.buttonColor2 = self.buttonColor2Def
        # size associations:
        self.mainWidth = 221
        self.buttonW3 = (self.mainWidth - 8) / 3
        self.buttonW4 = (self.mainWidth - 8) / 4
        self.buttonW5 = (self.mainWidth - 8) / 5
        self.buttonH = 32
        self.iconButtonH = 57

    def mainLayoutSetup(self):
        # setup the UI
        if cmds.window("RigIt_window", exists=True):
            cmds.deleteUI("RigIt_window")
        self.widgets["window"] = cmds.window("RigIt_window", title="Rigging Toolbox", mnb=0, mxb=0, sizeable=1)
        self.widgets["menuBarLayout"] = cmds.menuBarLayout()
        self.widgets["leftScrollLayout"] = cmds.scrollLayout(w=self.mainWidth + 12)
        self.widgets["mainLayout"] = cmds.rowColumnLayout(w=self.mainWidth)
        cmds.rowColumnLayout(nc=4, bgc=[.2, .2, .2])
        cmds.separator(w=2, visible=False)
        cmds.iconTextButton(style='iconOnly', image1=self.iconPath + "rigIt_top_210X33_001.jpg")

        self.widgets["top_paneLayout"] = cmds.paneLayout(configuration='horizontal2', p=self.widgets["mainLayout"])
        self.widgets["mayaMenues_frameLayout"] = cmds.rowColumnLayout(bgc=self.mainBGC, w=self.mainWidth - 6,
                                                                      parent=self.widgets["top_paneLayout"])

        self.widgets["mainLayout2"] = cmds.rowColumnLayout(parent=self.widgets["top_paneLayout"])
        self.widgets["Pipeline_Tools_frameLayout"] = cmds.frameLayout(label="Pipeline Tools", collapsable=True,
                                                                      bgc=self.mainFrames, w=self.mainWidth - 6,
                                                                      parent=self.widgets["mainLayout2"])
        self.widgets["Maya_Tools_frameLayout"] = cmds.frameLayout(label="Maya Tools", collapsable=True,
                                                                  bgc=self.mainFrames, w=self.mainWidth - 6,
                                                                  parent=self.widgets["mainLayout2"])
        self.widgets["MBA_Tools_frameLayout"] = cmds.frameLayout(label="MBA Tools", collapsable=True,
                                                                 bgc=self.mainFrames, w=self.mainWidth - 6,
                                                                 parent=self.widgets["mainLayout2"])
        self.mainFramesLayouts[1] = self.widgets["Pipeline_Tools_frameLayout"]
        self.mainFramesLayouts[2] = self.widgets["Maya_Tools_frameLayout"]
        self.mainFramesLayouts[3] = self.widgets["MBA_Tools_frameLayout"]
        self.mainFramesLayouts[4] = self.widgets["mayaMenues_frameLayout"]
        # end decoration
        cmds.separator(h=5, style='in', p=self.widgets["mainLayout"], visible=False)
        cmds.separator(h=3, style='in', p=self.widgets["mainLayout"])
        cmds.iconTextButton(style='iconOnly', h=120, w=120, image1=self.iconPath + "rigIT_logo_002.jpg",
                            p=self.widgets["mainLayout"])
        cmds.separator(h=3, style='out', p=self.widgets["mainLayout"])

    def dropDownMenuSetup(self):
        cmds.menu(label='Options', p=self.widgets["menuBarLayout"])
        # Todo: cmds.menuItem(label='Reset Tool', c=partial(setupRigIt.setupRigIt, self.scriptsPath))
        cmds.menuItem(divider=True)

        # Todo: cmds.menuItem(label='load prefs')
        # Todo: cmds.menuItem(label='set prefs')
        cmds.menuItem(divider=True)

        cmds.menuItem(label='settings', c=self.settingsWindow)

        cmds.menu(label='Menus', p=self.widgets["menuBarLayout"])
        cmds.menuItem(label='Node Editor', c="mel.eval('NodeEditorWindow')")
        cmds.menuItem(divider=True, l="general")
        cmds.menuItem(label='Component Editor', c="mel.eval('ComponentEditor')")
        cmds.menuItem(label='Connection Editor', c="mel.eval('ConnectionEditor')")
        cmds.menuItem(label='Hypergraph: Hierarchy', c="mel.eval('HypergraphHierarchyWindow')")
        cmds.menuItem(label='Hypergraph: Connections', c="mel.eval('HypergraphDGWindow')")

        cmds.menuItem(divider=True, l="animation")
        cmds.menuItem(label='Blend Shape Editor', c="mel.eval('ShapeEditor')")
        cmds.menuItem(label='Expression Editor', c="mel.eval('ExpressionEditor')")
        cmds.menuItem(label='Graph Editor', c="mel.eval('GraphEditor')")
        cmds.menuItem(divider=True, l="Rendering")
        cmds.menuItem(label='Hypershade', c="mel.eval('HypershadeWindow')")

        # cmds.menu(label='Help', p=self.widgets["menuBarLayout"])
        # cmds.menuItem(label='Author')

    def mayaMenuesSetup(self, parent='None'):
        if parent == 'None':
            return "Can't load mayaMenuesSetup"
        # self.widgets["menues_leftScrollLayout"] = cmds.scrollLayout(h=70, p=parent)
        self.widgets["menues_mainLayout"] = cmds.rowColumnLayout(nc=2, p=parent)
        w = 105
        self.widgets["menues_Layout1"] = cmds.rowColumnLayout(p=self.widgets["menues_mainLayout"], w=w)

        h = 20
        set1 = [.2, .3, .2]
        set2 = [.2, .2, .3]
        set2b = [.3, .3, .4]
        set3 = [.2, .3, .3]
        set4 = [.3, .2, .2]
        cmds.button(label='Node Editor', c="mel.eval('NodeEditorWindow')", w=w, h=h, bgc=set1)
        # cmds.text("general")
        cmds.button(label='Component Editor', c="mel.eval('ComponentEditor')", h=h, bgc=set2)
        cmds.button(label='Connection Editor', c="mel.eval('ConnectionEditor')", h=h, bgc=set2)
        cmds.button(label='Hypergraph: Hier', c="mel.eval('HypergraphHierarchyWindow')", h=h, bgc=set2b)
        cmds.button(label='Hypergraph: Con', c="mel.eval('HypergraphDGWindow')", h=h, bgc=set2b)

        self.widgets["menues_Layout2"] = cmds.rowColumnLayout(p=self.widgets["menues_mainLayout"], w=w)
        # cmds.text("animation")
        cmds.button(label='bShape Editor', c="mel.eval('ShapeEditor')", w=w, h=h, bgc=set3)
        cmds.button(label='Expression Editor', c="mel.eval('ExpressionEditor')", h=h, bgc=set3)
        cmds.button(label='Graph Editor', c="mel.eval('GraphEditor')", h=h, bgc=set3)
        # cmds.text("Rendering")
        cmds.iconTextButton(label='Hypershade', style="iconAndTextHorizontal", h=h,
                            c="mel.eval('HypershadeWindow')", bgc=set4)
        # cmds.text("Other")
        cmds.button(label='Reference Editor', c="mel.eval('ReferenceEditor')", h=h, bgc=set1)

    def settingsWindow(self, *args):
        # main back ground color
        # secondary back ground color
        # main drop down menus
        # secondary drop down menus
        # 1st buttons set
        # 2nd buttons set
        if cmds.window("RigIt_settings", exists=True):
            cmds.deleteUI("RigIt_settings")
        self.sWidgets["settings"] = cmds.window("RigIt_settings", title="RigItSettings", sizeable=1,
                                                rtf=True, w=self.buttonW3 * 6 + 10)
        # self.widgets["settingsMenuBar"] = cmds.menuBarLayout()
        self.sWidgets["settingsLeftScroll"] = cmds.scrollLayout()
        self.sWidgets["settingsMainLayout"] = cmds.rowColumnLayout(bgc=self.mainBGC)

        self.colorSettingsMenu(self.sWidgets["settingsMainLayout"])

        cmds.showWindow()

    def colorSettingsMenu(self, parent='None'):
        if parent == 'None':
            return "Can't load colorSettingsMenu"
        # colors settings drop down menu
        self.sWidgets["color_settings_frameLayout"] = cmds.frameLayout(label="Change colors settings", collapsable=True,
                                                                       bgc=self.mainFrames, w=self.buttonW3 * 6 + 5,
                                                                       parent=parent)
        self.sWidgets["colorSettingsLayout"] = cmds.rowColumnLayout(bgc=self.dockBGC, numberOfColumns=6)
        for i in range(6):
            cmds.button(visible=False, h=7)
        self.sWidgets['bockButton'] = cmds.button(l='Dock back\nground\ncolor', w=self.buttonW3,
                                                  bgc=self.dockBGC, c=partial(self.setMenuItemColor, 'dock'))
        self.sWidgets['bgButton'] = cmds.button(l='back\nground\ncolor', w=self.buttonW3,
                                                bgc=self.mainBGC, c=partial(self.setMenuItemColor, 'bgButton'))
        self.sWidgets['mFrameButton'] = cmds.button(l='main\nframes\ncolor', w=self.buttonW3,
                                                    bgc=self.mainFrames,
                                                    c=partial(self.setMenuItemColor, 'mFrameButton'))
        self.sWidgets['sFrameButton'] = cmds.button(l='secondary\nframes\ncolor', w=self.buttonW3,
                                                    bgc=self.secFrames,
                                                    c=partial(self.setMenuItemColor, 'sFrameButton'))
        self.sWidgets['set1Button'] = cmds.button(l='buttons\nset1\ncolor', w=self.buttonW3,
                                                  bgc=self.buttonColor1, c=partial(self.setMenuItemColor, 'set1Button'))
        self.sWidgets['set2Button'] = cmds.button(l='buttons\nset2\ncolor', w=self.buttonW3,
                                                  bgc=self.buttonColor2, c=partial(self.setMenuItemColor, 'set2Button'))
        cmds.button(h=7, visible=False)
        cmds.button(l="Revert Colors", w=self.buttonW3 * 2, c=self.revertColors, bgc=self.mainFramesDef,
                    p=self.sWidgets["color_settings_frameLayout"])
        cmds.separator(h=4, p=self.sWidgets["color_settings_frameLayout"])

    def revertColors(self, *args):
        self.setupDockColor(self.dockBGCDef)
        self.setupBgColor(self.mainBGCDef)
        self.setupMainFrameColor(self.mainFramesDef)
        self.setupSecFrameColor(self.secFramesDef)
        self.setupSet1Color(self.buttonColor1Def)
        self.setupSet2Color(self.buttonColor2Def)

    def setMenuItemColor(self, button, *args):
        color = gmt.colorPickerRGB()
        if not color:
            return  # "no color is changed."
        if button == 'dock':
            self.setupDockColor(color)
        elif button == 'bgButton':
            self.setupBgColor(color)
        elif button == 'mFrameButton':
            self.setupMainFrameColor(color)
        elif button == 'sFrameButton':
            self.setupSecFrameColor(color)
        elif button == 'set1Button':
            self.setupSet1Color(color)
        elif button == 'set2Button':
            self.setupSet2Color(color)
        print("    ---->    " + button + " color set to %s" % color)

    def setupDockColor(self, color):
        self.dockBGC = color
        cmds.rowColumnLayout(self.sWidgets["colorSettingsLayout"], e=True, bgc=self.dockBGC)
        cmds.button(self.sWidgets['bockButton'], e=True, bgc=self.dockBGC)
        cmds.dockControl(self.widgets["RigIt_dock"], e=True, bgc=self.dockBGC)

    def setupBgColor(self, color):
        self.mainBGC = color
        cmds.button(self.sWidgets['bgButton'], e=True, bgc=self.mainBGC)
        cmds.rowColumnLayout(self.sWidgets["settingsMainLayout"], e=True, bgc=self.mainBGC)

    def setupMainFrameColor(self, color):
        self.mainFrames = color
        cmds.button(self.sWidgets['mFrameButton'], e=True, bgc=self.mainFrames)
        for item in self.mainFramesLayouts:
            cmds.frameLayout(self.mainFramesLayouts[item], e=True, bgc=self.mainFrames)

    def setupSecFrameColor(self, color):
        self.secFrames = color
        cmds.button(self.sWidgets['sFrameButton'], e=True, bgc=self.secFrames)
        for item in self.secFramesLayouts:
            cmds.frameLayout(self.secFramesLayouts[item], e=True, bgc=self.secFrames)

    def setupSet1Color(self, color):
        self.buttonColor1 = color
        cmds.button(self.sWidgets['set1Button'], e=True, bgc=self.buttonColor1)
        for item in self.set1buttons:
            cmds.rowLayout(self.set1buttons[item], e=True, bgc=self.buttonColor1)
        for item in self.set1rowLayouts:
            cmds.rowLayout(self.set1rowLayouts[item], e=True, bgc=self.buttonColor1)
        for item in self.set1rowColumnLayouts:
            cmds.rowColumnLayout(self.set1rowColumnLayouts[item], e=True, bgc=self.buttonColor1)
        for item in self.set1frameLayouts:
            cmds.frameLayout(self.set1frameLayouts[item], e=True, bgc=self.buttonColor1)

    def setupSet2Color(self, color):
        self.buttonColor2 = color
        cmds.button(self.sWidgets['set2Button'], e=True, bgc=self.buttonColor2)
        for item in self.set2buttons:
            cmds.button(self.set2buttons[item], e=True, bgc=self.buttonColor2)
        for item in self.set2rowLayouts:
            cmds.rowLayout(self.set2rowLayouts[item], e=True, bgc=self.buttonColor2)
        for item in self.set2rowColumnLayouts:
            cmds.rowColumnLayout(self.set2rowColumnLayouts[item], e=True, bgc=self.buttonColor2)
        for item in self.set2frameLayouts:
            cmds.frameLayout(self.set2frameLayouts[item], e=True, bgc=self.buttonColor2)

    def shelfTools(self, parent='None'):
        if parent == 'None':
            return "Can't load shelfTools"
        self.widgets["shelfTools_frameLayout"] = cmds.frameLayout(label="Shelf Tools", collapsable=True,
                                                                  bgc=self.secFrames, p=parent)
        self.secFramesLayouts["shelfTools_frameLayout"] = self.widgets["shelfTools_frameLayout"]
        self.widgets["shelf_mainLayout"] = cmds.rowColumnLayout(nc=4, bgc=self.buttonColor1,
                                                                parent=self.widgets["shelfTools_frameLayout"])
        self.set1rowColumnLayouts["shelf_mainLayout"] = self.widgets["shelf_mainLayout"]
        cmds.iconTextButton(style='iconAndTextVertical', label='DelHist', image1=self.iconPath + "DH_icon.png",
                            ann='Delete History', w=self.buttonW4, h=self.iconButtonH,
                            c="mel.eval('DeleteHistory;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='NonDefor', image1=self.iconPath + "DH_ND_icon.png",
                            ann='Delete None-Deformer History', w=self.buttonW4, h=self.iconButtonH,
                            c="mel.eval('BakeNonDefHistory;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='CenPivot', image1=self.iconPath + "CP_icon.png",
                            ann='Center Pivot', w=self.buttonW4, h=self.iconButtonH, c="mel.eval('CenterPivot;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='delUnused', image1=self.iconPath + "DUN_icon.png",
                            ann='Delete unused nodes', w=self.buttonW4, h=self.iconButtonH,
                            c="mel.eval('MLdeleteUnused;')")
        # cmds.button(l='Delete ND\nHistory', h=self.buttonH, w=self.buttonW4, c="mel.eval('BakeNonDefHistory;')")
        # cmds.button(l='Center\nPivot', h=self.buttonH, w=self.buttonW4, c="mel.eval('CenterPivot;')")
        # freeze_Layout
        cmds.text("Reset / Freeze transformations:", align="left", p=self.widgets["shelfTools_frameLayout"])
        self.set2rowLayouts["freeze_Layout"] = cmds.rowLayout(nc=5, p=self.widgets["shelfTools_frameLayout"],
                                                              bgc=self.buttonColor2)

        cmds.iconTextButton(style='iconAndTextVertical', label='ResetT', image1=self.iconPath + "RT_icon.png",
                            w=self.buttonW5, h=self.iconButtonH, ann='Reset Transformations',
                            c="mel.eval('ResetTransformations;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='FreezeT', image1=self.iconPath + "FT_icon.png",
                            w=self.buttonW5, h=self.iconButtonH, ann='Freeze transforms for all channels',
                            c="mel.eval('makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='Trans', image1=self.iconPath + "FT_T_icon.png",
                            w=self.buttonW5, h=self.iconButtonH, ann='Freeze transforms for translate',
                            c="mel.eval('makeIdentity -apply true -t 1 -r 0 -s 0 -n 0 -pn 1;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='rot', image1=self.iconPath + "FT_R_icon.png",
                            w=self.buttonW5, h=self.iconButtonH, ann='Freeze transforms for rotate',
                            c="mel.eval('makeIdentity -apply true -t 0 -r 1 -s 0 -n 0 -pn 1;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='scale', image1=self.iconPath + "FT_S_icon.png",
                            w=self.buttonW5, h=self.iconButtonH, ann='Freeze transforms for scale',
                            c="mel.eval('makeIdentity -apply true -t 0 -r 0 -s 1 -n 0 -pn 1;')")

        cmds.text("Maya constraints:", align="left", p=self.widgets["shelfTools_frameLayout"])
        self.set2rowColumnLayouts["cns_main_Layout"] = cmds.rowColumnLayout(nc=1, bgc=self.buttonColor2,
                                                                            p=self.widgets["shelfTools_frameLayout"])
        pm.checkBox(label="Open Constraint's Options", cc=self.cnsOptions, value=True)
        cmds.rowLayout(nc=5)
        bColor = [.3, .3, .4]
        self.widgets["parCns"] = cmds.button("parent", w=self.buttonW5, bgc=bColor,
                                             c="mel.eval('ParentConstraintOptions')")
        self.widgets["poiCns"] = cmds.button("point", w=self.buttonW5, bgc=bColor,
                                             c="mel.eval('PointConstraintOptions')")
        self.widgets["oriCns"] = cmds.button("orient", w=self.buttonW5, bgc=bColor,
                                             c="mel.eval('OrientConstraintOptions')")
        self.widgets["sclCns"] = cmds.button("scale", w=self.buttonW5, bgc=bColor,
                                             c="mel.eval('ScaleConstraintOptions')")
        self.widgets["aimCns"] = cmds.button("aim", w=self.buttonW5, bgc=bColor, c="mel.eval('AimConstraintOptions')")

        # cmds.button('Freeze Trans', w=80, ann='Freeze transforms for all channels',
        #            c="mel.eval('makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;')")
        # cmds.button('Trans', w=43, c="mel.eval('makeIdentity -apply true -t 1 -r 0 -s 0 -n 0 -pn 1;')")
        # cmds.button('Rotate', w=43, c="mel.eval('makeIdentity -apply true -t 0 -r 1 -s 0 -n 0 -pn 1;')")
        # cmds.button('Scale', w=43, c="mel.eval('makeIdentity -apply true -t 0 -r 0 -s 1 -n 0 -pn 1;')")

    def cnsOptions(self, *args):
        if args[0]:
            cmds.button(self.widgets["parCns"], edit=True, c="mel.eval('ParentConstraintOptions')")
            cmds.button(self.widgets["poiCns"], edit=True, c="mel.eval('PointConstraintOptions')")
            cmds.button(self.widgets["oriCns"], edit=True, c="mel.eval('OrientConstraintOptions')")
            cmds.button(self.widgets["sclCns"], edit=True, c="mel.eval('ParentConstraintOptions')")
            cmds.button(self.widgets["aimCns"], edit=True, c="mel.eval('AimConstraintOptions')")
        else:
            cmds.button(self.widgets["parCns"], edit=True, c="mel.eval('ParentConstraint')")
            cmds.button(self.widgets["poiCns"], edit=True, c="mel.eval('PointConstraint')")
            cmds.button(self.widgets["oriCns"], edit=True, c="mel.eval('OrientConstraint')")
            cmds.button(self.widgets["sclCns"], edit=True, c="mel.eval('ScaleConstraint')")
            cmds.button(self.widgets["aimCns"], edit=True, c="mel.eval('AimConstraint')")

    def externalTools(self, parent):
        if parent == 'None':
            return "Can't load externalTools"
        self.widgets["externalTools_frameLayout"] = cmds.frameLayout(label="External Tools", collapsable=True,
                                                                     bgc=self.secFrames, p=parent)
        self.secFramesLayouts["externalTools_frameLayout"] = self.widgets["externalTools_frameLayout"]
        self.widgets["external_mainLayout"] = cmds.rowColumnLayout(nc=4, bgc=self.buttonColor2,
                                                                   parent=self.widgets["externalTools_frameLayout"])
        self.set2rowColumnLayouts["external_mainLayout"] = self.widgets["external_mainLayout"]
        cmds.iconTextButton(style='iconAndTextVertical', label='shapes', image1=self.iconPath + "Shapes_icon.png",
                            w=self.buttonW5, h=self.iconButtonH, ann='Opens "Shapes"',
                            c="from maya import mel; mel.eval('SHAPES;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='brush', image1=self.iconPath + "Shapes_icon.png",
                            w=self.buttonW5, h=self.iconButtonH, ann='Opens "SHAPESBrush"',
                            c="from maya import mel; mel.eval('SHAPESBrush;')")

        cmds.iconTextButton(style='iconAndTextVertical', label='NG', image1=self.iconPath + "NG-SkinTools_03_icon.png",
                            w=self.buttonW5, h=self.iconButtonH, ann='Opens "ng_skinTools"',
                            c="from ngSkinTools.ui.mainwindow import MainWindow; MainWindow.open()")
        self.mGearTools(self.widgets["externalTools_frameLayout"])

    def mGearTools(self, parent):
        if parent == 'None':
            return "Can't load mGearTools"
        self.widgets["mGearTools_frameLayout"] = cmds.frameLayout(label="mGear Tools", collapsable=True,
                                                                  bgc=self.buttonColor2, p=parent)
        self.widgets["mGear_layout"] = cmds.rowColumnLayout(nc=1, p=self.widgets["mGearTools_frameLayout"])
        h = 18
        cmds.rowColumnLayout(nc=2, p=self.widgets["mGear_layout"])
        cmds.button("Build Guide", w=self.buttonW4 * 2, h=h, ann="Build guide from selection", bgc=[0.8, 0.4, 0.15],
                    c="import mgear.maya.shifter as ms; ms.Rig().buildFromSelection()")
        # todo ? "from maya import mel;mel.eval('ScriptEditor;');"

        cmds.button("Settings", w=self.buttonW4 * 2, h=h, ann="Open settings window", bgc=[0.2, 0.4, .6],
                    c="import mgear; mgear.maya.shifter.gui.Guide_UI.inspectSettings()")

        cmds.rowColumnLayout(nc=3, p=self.widgets["mGear_layout"])
        cmds.button("Dupl.", w=self.buttonW3, h=h, ann="Duplicate mGear controller", bgc=[0.2, 0.6, .2],
                    c=partial(mgm.mGearDuplicate, False))
        cmds.button("Dupl. Sym", w=self.buttonW3 - 1, h=h, ann="Duplicate mGear controller with symmetry",
                    bgc=[0.4, 0.7, .3],
                    c=partial(mgm.mGearDuplicate, True))
        # todo: check if the extract command can work from an mGear command
        cmds.button("Extr. Ctl", w=self.buttonW3, h=h, ann="Extract mGear controller shape", bgc=[0.78, 0.7, .0],
                    c=partial(mgm.extractControls), enable=True)

        cmds.rowColumnLayout(nc=2, p=self.widgets["mGear_layout"])
        cmds.button("Import Skin", w=self.buttonW4 * 2, h=h, ann="Open settings window", bgc=[.6, .5, .8],
                    c="import mgear; mgear.maya.skin.importSkin()")
        cmds.button("Export Skin", w=self.buttonW4 * 2, h=h, ann="Open settings window", bgc=[.55, .45, .8],
                    c="import mgear; mgear.maya.skin.exportSkin()")

        cmds.rowColumnLayout(nc=3, p=self.widgets["mGear_layout"])
        cmds.button(label="reload", w=self.buttonW4, h=h, bgc=[0.45, 0.6, .6],
                    c=partial(mgear.reloadModule, "mgear"))
        cmds.button(label="Compile PyQt ui", w=self.buttonW4 * 2, h=h, bgc=[0.4, 0.55, .6])  # ,
        # c=partial(mGear_utils.ui2py, None))
        cmds.button(label="Synoptic", w=self.buttonW4, h=h, bgc=[0.35, 0.5, .6],
                    c=partial(syn.open))

    def handyRiggingTools(self, parent='None'):
        if parent == 'None':
            return "Can't load handyRiggingTools"
        self.widgets["handyTools_frameLayout"] = cmds.frameLayout(label="Handy Tools", collapsable=True,
                                                                  bgc=self.secFrames, p=parent)
        self.secFramesLayouts["handyTools_frameLayout"] = self.widgets["handyTools_frameLayout"]
        self.widgets["handy_mainLayout"] = cmds.rowColumnLayout(nc=1,
                                                                parent=self.widgets["handyTools_frameLayout"])

        # handy_Layout2
        self.widgets["handy_Layout2"] = cmds.rowColumnLayout(numberOfColumns=3, bgc=self.buttonColor1,
                                                             parent=self.widgets["handy_mainLayout"])
        self.set1rowColumnLayouts["handy_Layout2"] = self.widgets["handy_Layout2"]
        cmds.button(l='Bind and\nCopy Skin', w=self.buttonW3, h=self.buttonH, c=gmt.bindAndCopy, bgc=[0.2, 0.6, .2],
                    ann='select source, then target.\nbinds to the relevant joints and copy weights')
        cmds.button(l='Bind Skin', w=self.buttonW3, h=self.buttonH, c=gmt.bindAndName, bgc=[0.4, 0.7, .3],
                    ann='Binds to selected joints and names the skinClusters')
        cmds.button(l='Select\nSkin/s', w=self.buttonW3, c=gmt.selectSkin, bgc=[.37, .48, .7],
                    ann='select all skins for selection')
        cmds.button(l='Add to\nbShape', w=self.buttonW3, c=partial(gmt.createBsp, True), bgc=[0.7, .4, .37],
                    ann='Adds blend shapes to existing blend shape on last selected mesh\n*Possible to select multiple meshes:\nthe last selected mesh will be affected')
        cmds.button(l='Create\nbShape', w=self.buttonW3, c=gmt.createBsp, bgc=[0.7, .45, .4],
                    ann='Create Blend Shape from selection')
        cmds.button(l='Select\nBsp/s', w=self.buttonW3, c=gmt.selectBsp, bgc=[.4, .5, .7],
                    ann="Select the blend shape from selected mesh")
        cmds.button(l='Create crv\nfrom verts', w=self.buttonW3, c=partial(gmt.createCrvFromSelection, True),
                    ann="Select the verts in the desired order and click button\n"
                        "This creates a curve with controlling locators")
        cmds.button(l='Parent\nShape', w=self.buttonW3, c=gmt.parentShape,
                    ann="Select shape, then select the transform that will receive the shape")
        cmds.button(l='Hammer\nWeights', w=self.buttonW3, c="mel.eval('weightHammerVerts')",
                    ann="Hammer skin weights")
        cmds.iconTextButton(style='iconAndTextVertical', label='lockAttr', image1=self.iconPath + "LA_icon.png",
                            w=40, h=self.iconButtonH, ann="Lock translate, rotate and scale for selection",
                            c=partial(gmt.lockAttributes, True))
        cmds.iconTextButton(style='iconAndTextVertical', label='unlockAttr', image1=self.iconPath + "ULA_icon.png",
                            w=40, h=self.iconButtonH, ann="Unlock translate, rotate and scale for selection",
                            c=partial(gmt.lockAttributes, False))
        cmds.button(l='Unbind\nSkin', w=self.buttonW3, c='mel.eval(\'doDetachSkin "2" {"1", "1"};\')',
                    ann="Unbind Skin")

        cmds.separator(parent=self.widgets["handy_mainLayout"], h=1)

        # handy_Layout
        bColor = [.55, .45, .8]
        bColor2 = [.6, .5, .8]
        pm.text('Create and delete constraints:', p=self.widgets["handy_mainLayout"])
        self.widgets["handy_Layout"] = cmds.rowColumnLayout(numberOfColumns=4, bgc=self.buttonColor2,
                                                            rowSpacing=[1, 4],
                                                            parent=self.widgets["handy_mainLayout"])
        self.set2rowColumnLayouts["handy_Layout"] = self.widgets["handy_Layout"]
        # constraints + delete

        cmds.iconTextButton(style='iconAndTextVertical', label='DelParent', w=self.buttonW4, h=self.iconButtonH,
                            image1=self.iconPath + "const_parentCon_003_icon.png",
                            ann='create and delete Parent constraint', c="mel.eval('delete `parentConstraint`;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='DelPoint', w=self.buttonW4, h=self.iconButtonH,
                            image1=self.iconPath + "const_pointCon_003_icon.png",
                            ann='create and delete Point constraint', c="mel.eval('delete `pointConstraint`;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='DelOrient', w=self.buttonW4, h=self.iconButtonH,
                            image1=self.iconPath + "const_orientCon_003_icon.png",
                            ann='create and delete Orient constraint', c="mel.eval('delete `orientConstraint`;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='DelScale', w=self.buttonW4, h=self.iconButtonH,
                            image1=self.iconPath + "const_scaleCon_003_icon.png",
                            ann='create and delete Scale constraint', c="mel.eval('delete `scaleConstraint`;')")
        cmds.iconTextButton(style='iconAndTextVertical', label='DelAllCns', w=self.buttonW4, h=self.iconButtonH,
                            image1=self.iconPath + "const_noCon_002_icon.png",
                            ann='delete constraints from selection', c=gmt.deleteConstraints)
        cmds.iconTextButton(style='textOnly', label='create\nParent+\nScale\nCns', w=self.buttonW4, h=self.iconButtonH,
                            ann='Create parent and scale constraint',
                            c="pm.parentConstraint(mo=True);pm.scaleConstraint(mo=True)")

        # TODO make instead of parent constraint, transfer position by xform?
        '''
        cmds.button(l='Lock all\nattributes', h=self.buttonH, w=self.buttonW4, c=partial(gmt.lockAttributes, True),
                    ann="Lock translate, rotate and scale for selection")
        cmds.button(l='Unlock all\nattributes', h=self.buttonH, w=self.buttonW4, c=partial(gmt.lockAttributes, False),
                    ann="Unlock translate, rotate and scale for selection")
        '''

        # cmds.separator(parent=self.widgets[("handy_mainLayout")], h=5)
        cmds.separator(parent=self.widgets["handy_mainLayout"], h=1)

        # jnt tools
        # moveJnts_Layout
        self.widgets["moveJnts_Layout"] = cmds.rowLayout(numberOfColumns=3,  # columnWidth3=(80, 42, 42),
                                                         adjustableColumn=1, bgc=self.buttonColor1,
                                                         parent=self.widgets["handy_mainLayout"])
        self.set1rowLayouts["moveJnts_Layout"] = self.widgets["moveJnts_Layout"]
        cmds.text('move bound joint:', h=20, w=70)

        cmds.button(l='on', w=45, h=20, c='mel.eval("moveJointsMode 1;")', bgc=[0.4, 0.7, .3])
        cmds.button(l='off', w=45, h=20, c='mel.eval("moveJointsMode 0;")', bgc=[0.7, .4, .37])
        self.widgets["jntOrients_layout"] = cmds.rowColumnLayout(nc=2, p=self.widgets["handy_mainLayout"])
        self.set2buttons["jntTransferRots"] = cmds.button(label='rotate to jnt Orient',
                                                          bgc=bColor, w=self.buttonW4 * 2,
                                                          ann="Transfer rotate values to joint orient",
                                                          c=gmt.rotateToJntOrient)
        self.set2buttons["jntTransferRots"] = cmds.button(label='jnt orient to rotate ',
                                                          bgc=bColor2, w=self.buttonW4 * 2,
                                                          ann="Transfer joint orient to rotation",
                                                          c=partial(gmt.rotateToJntOrient, True))
        self.set2buttons["jntOrients"] = cmds.button(label='Zero joint Orients', bgc=bColor2,
                                                     ann="Zero joint rotate and joint orient.", w=self.buttonW4 * 2,
                                                     c=gmt.zeroJntOrients)

        # color override
        self.widgets["ColorOvRd_frameLayout"] = cmds.frameLayout(label="Color Override", collapsable=True,
                                                                 bgc=self.buttonColor2,
                                                                 parent=self.widgets["handy_mainLayout"])
        self.set2frameLayouts["ColorOvRd_frameLayout"] = self.widgets["ColorOvRd_frameLayout"]

        # self.widgets["colorOvRd_Layout"] = cmds.rowColumnLayout(numberOfColumns=1,
        #                                                adjustableColumn=1, bgc=self.buttonColor2,
        #                                                parent=self.widgets[("handy_mainLayout")])
        # self.widgets["colorOverride"] = cmds.text('color override:', h=20, w=70, p=self.widgets["colorOvRd_Layout"])
        self.widgets["colorOvRdButtons_Layout"] = cmds.rowColumnLayout(numberOfColumns=8, adjustableColumn=1,
                                                                       parent=self.widgets["ColorOvRd_frameLayout"])
        # self.set2rowColumnLayouts["colorOvRdButtons_Layout"] = self.widgets["colorOvRdButtons_Layout"]
        colOvrd = [[0, 'gray', [0.188, 0.188, 0.188]], [1, 'black', [0, 0, 0]], [2, 'darkGray', [0.051, 0.051, 0.051]],
                   [3, 'lightGray', [0.319, 0.319, 0.319]], [4, 'paleRed', [0.328, 0.0, 0.021]],
                   [5, 'navyBlue', [0.0, 0.001, 0.117]], [6, 'blue', [0, 0, 1]],
                   [7, 'darkGreen', [0.000, 0.061, 0.010]],
                   [8, 'purple', [0.019, 0.0, 0.056]], [9, 'pink', [0.578, 0.0, 0.578]],
                   [10, 'brown', [0.254, 0.065, 0.033]],
                   [11, 'darkBrown', [0.050, 0.017, 0.014]], [12, 'otherRed', [0.319, 0.019, 0.0]],
                   [13, 'red', [1, 0, 0]],
                   [14, 'green', [0, 1, 0]], [15, 'paleBlue', [0.0, 0.053, 0.319]], [16, 'white', [1, 1, 1]],
                   [17, 'yellow', [1, 1, 0]], [18, 'azure', [0.127, 0.716, 1.0]],
                   [19, 'paleGreen', [0.056, 1.000, 0.366]],
                   [20, 'palePink', [1.000, 0.434, 0.434]], [21, 'skin', [0.776, 0.413, 0.191]],
                   [22, 'paleYellow', [1.000, 1.000, 0.125]], [23, 'paleGreen2', [0.000, 0.319, 0.089]],
                   [24, 'orange', [0.356, 0.144, 0.030]], [25, 'paleYellow2', [0.342, 0.356, 0.030]],
                   [26, 'paleGreen2', [0.138, 0.356, 0.030]], [27, 'paleGreen3', [0.030, 0.356, 0.109]],
                   [28, 'paleAzure', [0.030, 0.356, 0.356]], [29, 'paleBlue2', [0.030, 0.136, 0.356]],
                   [30, 'palePurple', [0.159, 0.030, 0.356]], [31, 'palePink', [0.356, 0.030, 0.144]]]

        for item in colOvrd:
            cmds.button(l='', w=26, h=11, bgc=item[2], c=partial(gmt.colorOverride, item[0]),
                        ann='%s is number %s by script' % (item[1], item[0]))

        # cmds.button(l='', w=21, h=15, bgc=(0, 0, 1), c=partial(gmt.colorOverride, 1))

    def cleanupTools(self, parent="None"):
        if parent == 'None':
            return "Can't load cleanupTools"
        bColor = [.9, .45, .5]
        bColor2 = [.37, .48, .7]
        self.widgets["cleanup_frameLayout"] = cmds.frameLayout(label="Cleanup Tools", collapsable=True,
                                                               bgc=self.secFrames, p=parent)
        self.secFramesLayouts["cleanup_frameLayout"] = self.widgets["cleanup_frameLayout"]
        self.widgets["cleanup_Layout"] = cmds.rowColumnLayout(numberOfColumns=3, bgc=self.buttonColor2,
                                                              parent=self.widgets["cleanup_frameLayout"])
        self.set2rowColumnLayouts["cleanup_Layout"] = self.widgets["cleanup_Layout"]
        cmds.button(l='instance\nto object', w=self.buttonW3, bgc=bColor, h=self.buttonH,
                    c=gmt.instanceToObject, ann="converts selection from instances to objects")

    def handyPrints(self, parent="None"):
        if parent == 'None':
            return "Can't load handyPrints"
        # handyPrints_frameLayout
        bColor = [.4, .5, .7]
        bColor2 = [.37, .48, .7]
        self.widgets["handyPrints_frameLayout"] = cmds.frameLayout(label="Handy Prints", collapsable=True,
                                                                   bgc=self.secFrames, p=parent)
        self.secFramesLayouts["handyPrints_frameLayout"] = self.widgets["handyPrints_frameLayout"]
        self.widgets["handyPrints_Layout"] = cmds.rowColumnLayout(numberOfColumns=3, bgc=self.buttonColor2,
                                                                  parent=self.widgets["handyPrints_frameLayout"])
        self.set2rowColumnLayouts["handyPrints_Layout"] = self.widgets["handyPrints_Layout"]
        cmds.button(l='print\nselected', w=self.buttonW3, h=self.buttonH, bgc=bColor,
                    c=partial(gmp.printSelected), ann="print a list of the selected objects / components")
        cmds.button(l='print only\ncomponents', w=self.buttonW3, h=self.buttonH, bgc=bColor2,
                    c=partial(gmp.componentLister, True),
                    ann="print a list of the selected vertices/edges/faces\n(without the object's name)")
        cmds.button(l='print WS\nxform', w=self.buttonW3, h=self.buttonH, bgc=bColor,
                    c=partial(gmp.printXform, True), ann="print world space translate, rotate and scale")
        cmds.button(l='color pick\nprint', w=self.buttonW3, h=self.buttonH, bgc=bColor2,
                    c=gmp.colorPickerPrint, ann="opens a color picker and prints the selected color")
        cmds.button(l='print Unique\nAttrs', w=self.buttonW3, h=self.buttonH, bgc=bColor,
                    c=gmp.printUniqueAttrs, ann="Prints the unique attributes on the selected object")
        cmds.button(l='print\nDeformers', w=self.buttonW3, h=self.buttonH, bgc=bColor2,
                    c=gmp.analyzeDeformers, ann="Prints the Deformers for current selection")
        cmds.button(l='print\nInfuences', w=self.buttonW3, h=self.buttonH, bgc=bColor,
                    c=partial(gmp.getInfluList, True), ann="Prints the influence list for current selection")
        cmds.button(l='print\nSkins', w=self.buttonW3, h=self.buttonH, bgc=bColor2,
                    c=gmp.printSkinClusters, ann="Prints the blend shapes for current selection")
        cmds.button(l='print\nBsps', w=self.buttonW3, h=self.buttonH, bgc=bColor,
                    c=gmp.printBlendShapes, ann="Prints the blend shapes for current selection")

    # TODO create an attr edit window?
    # TODO make a free input method for changing attrs on selected. CONCEPT:
    '''
    sel = cmds.ls(sl=True, s=checkBoxInput)
    for obj in sel:
        cmds.setAttr("%s.%s", %s) %obj, freeTextInput, valueInput
    '''

    def funkyTools(self, parent="None"):
        if parent == 'None':
            return "Can't load funkyTools"
        # handyPrints_frameLayout
        self.widgets["funkyTools_frameLayout"] = cmds.frameLayout(label="Funky Tools", collapsable=True,
                                                                  bgc=self.secFrames, p=parent)
        self.secFramesLayouts["funkyTools_frameLayout"] = self.widgets["funkyTools_frameLayout"]
        self.widgets["funkyTools_Layout"] = cmds.rowColumnLayout(numberOfColumns=4, bgc=self.buttonColor1,
                                                                 parent=self.widgets["funkyTools_frameLayout"])
        self.set1rowColumnLayouts["funkyTools_Layout"] = self.widgets["funkyTools_Layout"]
        cmds.iconTextButton(style='iconAndTextVertical', label='liteWrap', image1=self.iconPath + "LWT_icon.png",
                            w=self.buttonW4, ann="Create a lite wrap deformer.",
                            c=self.openLiteWrap)
        # cmds.button(l='Lite Wrap\nTool', w=self.buttonW3, h=self.buttonH, c=self.openLiteWrap,
        #            ann="Create a lite wrap deformer")
        cmds.iconTextButton(style='iconAndTextVertical', label='Rename', image1=self.iconPath + "RN_T_icon.png",
                            w=self.buttonW4, ann="rename or remove or add prefix/suffix",
                            c=self.openRenameTool)
        cmds.iconTextButton(style='iconAndTextVertical', label='SkinWorks', w=self.buttonW4, h=self.iconButtonH,
                            image1=self.iconPath + "SkinToVerts_icon.png",
                            ann="Various tools for skinning",
                            c=self.openSkinWorks)
        cmds.iconTextButton(style='iconAndTextVertical', label='Skin\nTo Verts', w=self.buttonW4, h=self.iconButtonH,
                            image1=self.iconPath + "SkinToVerts_icon.png",
                            ann="Tool for copying skin from an object to verts selection (or set) easily",
                            c=self.openCopySkinToVerts)
        cmds.iconTextButton(style='iconAndTextVertical', label='ScriptIt!', image1=self.iconPath + "Script_it_icon.png",
                            w=self.buttonW4, ann="Opens Scipt It! A script creation tool",
                            c=self.openScripIt)
        cmds.iconTextButton(style='iconAndTextVertical', label='GroupIt', image1=self.iconPath + "GrpIt_icon.png",
                            w=self.buttonW4, ann="grouping tool - works for selection.",
                            c=self.openGroupIt)
        cmds.iconTextButton(style='iconAndTextVertical', label='Collider', image1=self.iconPath + "Collider_2_icon.png",
                            w=self.buttonW4, ann="Opens collider creation tool",
                            c=self.openColliderTool)
        cmds.iconTextButton(style='iconAndTextVertical', label='Spring\nCollider',
                            image1=self.iconPath + "Collider_2_icon.png",
                            w=self.buttonW4, ann="Opens Springs Collider creation tool",
                            c=self.openSpringsColliderTool)
        cmds.iconTextButton(style='iconAndTextVertical', label='BspDup', image1=self.iconPath + "bspDup_icon_02.png",
                            w=self.buttonW4, ann="Opens Bsp Duplicator tool",
                            c=self.openBspDuplicator)
        # cmds.iconTextButton(style='iconAndTextVertical', label='ScriptIt2!',
        #                    image1=self.iconPath + "Script_it_icon.png",
        #                    w=self.buttonW4, ann="Opens Scipt It! A script creation tool",
        #                    c=self.openScriptItMaster)
        cmds.iconTextButton(style='iconAndTextVertical', label='Curves\nToolbox',
                            w=self.buttonW4, c=self.openCurveRigTool, image1='pencil.png',
                            # image1=self.iconPath + "Script_it_icon.png",
                            ann="Opens Rigging Curves Toolbox")
        cmds.iconTextButton(style='iconAndTextVertical', label='Color\nSwitcher', image1="colorProfile.png",
                            w=self.buttonW4, ann="Opens Color Switcher creator window",
                            c=self.openColorSwitcher)
        cmds.iconTextButton(style='iconAndTextVertical', label='ScriptIt2!', image1=self.iconPath + "Script_it_icon.png",
                            w=self.buttonW4, ann="Opens Scipt It! A script creation tool",
                            c=self.openScriptItMaster)
        cmds.iconTextButton(style='iconAndTextVertical', label='UV Trans\nMaster', image1=self.iconPath + "UVtoolKit.png",
                            w=self.buttonW4, ann="",
                            c=self.openUVtransMaster)
        cmds.iconTextButton(style='iconAndTextVertical', label='window\ntest', image1=self.iconPath + "question.png",
                            w=self.buttonW4, ann="",
                            c=self.openWinTest)

    def snowballToolsFrame(self, parent='None'):
        if parent == 'None':
            return "Can't load snowballToolsFrame"
        self.widgets["snowTools_frameLayout"] = cmds.frameLayout(label="Snowball_Tools", collapsable=True,
                                                                 bgc=self.secFrames, p=parent)
        self.secFramesLayouts["snowTools_frameLayout"] = self.widgets["snowTools_frameLayout"]
        self.widgets["rigItTools_mainLayout"] = cmds.rowColumnLayout(nc=1, w=200,
                                                                    parent=self.widgets["snowTools_frameLayout"])
        '''
        cmds.rowColumnLayout(nc=2, cs=[2, 2])
        cmds.iconTextButton(l='P i p e l i n e', h=21, w=99, bgc=[0.4, 0.55, .6], font='boldLabelFont', st='textOnly',
                            c=self.openPipeline)
        cmds.iconTextButton(l='D r e s s e r', h=21, w=99, bgc=[0.4, 0.55, .6], font='boldLabelFont', st='textOnly',
                            c=self.openDresser)
'''
        cmds.text("Override:", align="left", p=self.widgets["rigItTools_mainLayout"])
        self.widgets["snowTools_Layout1"] = cmds.rowColumnLayout(numberOfColumns=4,
                                                                 bgc=self.buttonColor1,
                                                                 parent=self.widgets["rigItTools_mainLayout"])
        self.set1rowColumnLayouts["snowTools_Layout1"] = self.widgets["snowTools_Layout1"]
        h = 48
        cmds.iconTextButton(style='iconAndTextVertical', label='Off all', image1=self.iconPath + "OR_on_icon.png",
                            ann="Disable override high_grp and all\ntransforms and shapes under it.",
                            w=self.buttonW4, h=h, c=sbt.disableOverrideAllOff)
        cmds.iconTextButton(style='iconAndTextVertical', label='selection', image1=self.iconPath + "OR_on_icon.png",
                            ann="Disable override for selection\nand to it's shape's (if exists).",
                            w=self.buttonW4, h=h, c=sbt.disableOverride)
        cmds.iconTextButton(style='iconAndTextVertical', label='On all', image1=self.iconPath + "OR_off_icon.png",
                            ann="Enable override on high_grp\nand all transforms under it.",
                            w=self.buttonW4, h=h, c=sbt.disableOverrideAllOn)
        cmds.iconTextButton(style='iconAndTextVertical', label='highGrp', image1=self.iconPath + "OR_slc_icon.png",
                            ann="Disable override for selection\nand to it's shape's (if exists).",
                            w=self.buttonW4, h=h, c=partial(sbt.disableOverrideAllOn, True))
        cmds.text("Rig Tools:", align="left", p=self.widgets["rigItTools_mainLayout"])
        # Snowball tools
        self.widgets["snowTools_Layout2"] = cmds.rowColumnLayout(numberOfColumns=4,
                                                                 bgc=self.buttonColor1,
                                                                 parent=self.widgets["rigItTools_mainLayout"])
        self.set1rowColumnLayouts["snowTools_Layout2"] = self.widgets["snowTools_Layout2"]
        h = 48
        cmds.iconTextButton(style='iconAndTextVertical', image1=self.iconPath + "FinRig_icon_02.png",
                            ann="Finalize rig for props - make cns, check hierarchy and enable override.",
                            w=self.buttonW4, h=h, c=self.openFinalizeRig_snowball)
        cmds.iconTextButton(style='iconAndTextVertical', image1=self.iconPath + "cns_icon_001.png",
                            ann="Opens Cns maker window.",
                            w=self.buttonW4, h=h, c=self.openCnsTool)
        cmds.iconTextButton(style='textOnly', l='Scale\nReader', bgc=[.3, .3, .3],  # image1=self.iconPath + "icon.png",
                            ann="Opens Scale Reader maker window.",
                            w=self.buttonW4, h=h, c=self.openScaleReaderTool)
        cmds.iconTextButton(style='iconAndTextVertical', l='Mass\ntools',
                            image1=self.iconPath + "mass_tools_icon_02.png",
                            ann="Opens Mass tools window - tools to help with mass repetitions.",
                            w=self.buttonW4, h=h + 10, c=self.openMassTools)

    def openPipeline(self, *args):
        import pipeline_maya
        pipeline_maya.start()

    def openDresser(self, *args):
        from pipeline_maya.dresser import app
        app.start_publisher_app()

    def openDresserBeta(self, *args):
        from MBA_SE02.dresser import app
        app.start_publisher_app()

    def addPythonButton(self, addFile):
        cmds.button(l=addFile, h=self.buttonH, w=self.buttonW3, c="import %s; reload(%s)" % (addFile, addFile),
                    ann="Run " + addFile + ".")

    def addMelButton(self, name, addFile):  # ToDo check if addMelButton works
        cmds.button(l=name, h=self.buttonH, w=self.buttonW3, c="mel.eval('source \"%s\"')" % addFile,
                    ann="Run " + name + " file.")

    def collectiveTools(self, parent='None'):
        if parent == 'None':
            return "Can't load rigItToolsFrame"
        # todo make icon options for this IconPath = scriptsPath + "/RigIt/Icons"
        # Getting files from collectiveTools folders
        pyExFiles, melExFiles = rim.getFilesForButtons(self.scriptsPath + "/collectiveTools/externalTools")
        # create buttons assigned to all scripts
        pyMaFiles, melMaFiles = rim.getFilesForButtons(self.scriptsPath + "/collectiveTools/mayaTools")
        self.widgets["collectiveTools_frameLayout"] = cmds.frameLayout(label="Collective Tools", collapsable=True,
                                                                       bgc=self.secFrames, p=parent)
        self.secFramesLayouts["collectiveTools_frameLayout"] = self.widgets["collectiveTools_frameLayout"]
        self.widgets["collectiveTools_mainLayout"] = cmds.rowColumnLayout(nc=1, w=200,
                                                                          parent=self.widgets[
                                                                              "collectiveTools_frameLayout"])
        self.widgets["externalTools_Layout1"] = cmds.rowColumnLayout(numberOfColumns=3, bgc=self.buttonColor1,
                                                                     parent=self.widgets[
                                                                         "collectiveTools_mainLayout"])
        self.set1rowColumnLayouts["externalTools_Layout1"] = self.widgets["externalTools_Layout1"]
        for pyFile in pyExFiles:
            self.addPythonButton(pyFile)
        for melFile in melExFiles:
            self.addMelButton(melFile[0], melFile[1])
        self.widgets["mayaTools_Layout1"] = cmds.rowColumnLayout(numberOfColumns=3, bgc=self.buttonColor1,
                                                                 parent=self.widgets[
                                                                     "collectiveTools_mainLayout"])
        self.set1rowColumnLayouts["mayaTools_Layout1"] = self.widgets["mayaTools_Layout1"]
        for pyFile in pyMaFiles:
            self.addPythonButton(pyFile)
        for melFile in melMaFiles:
            self.addMelButton(melFile[0], melFile[1])

    # todo check if possible to make one smart method for all tools
    ''' # example:
    def toolLauncher(tool, *args):
        import tool
        reload(tool)
        tool.tool()
    '''

    @staticmethod
    def openFinalizeRig_snowball(*args):
        import FinalizeRig_snowball
        reload(FinalizeRig_snowball)
        FinalizeRig_snowball.FinalizeRig_snowball()

    @staticmethod
    def openLiteWrap(*args):
        import LiteWrap
        reload(LiteWrap)
        LiteWrap.LiteWrap()

    @staticmethod
    def openRenameTool(*args):
        import RenameTool
        reload(RenameTool)
        RenameTool.RenameTool()

    @staticmethod
    def openGroupIt(*args):
        import GroupIt
        reload(GroupIt)
        GroupIt.GroupIt()

    @staticmethod
    def openCopySkinToVerts(*args):
        import CopySkinToVerts
        reload(CopySkinToVerts)
        CopySkinToVerts.CopySkinToVerts()

    @staticmethod
    def openCurveRigTool(*args):
        import CurveRigTool
        reload(CurveRigTool)
        CurveRigTool.CurveRigTool()

    @staticmethod
    def openSkinWorks(*args):
        import SkinWorks
        reload(SkinWorks)
        SkinWorks.SkinWorks()

    def openScripIt(self, *args):
        import ScriptIt
        reload(ScriptIt)
        ScriptIt.ScriptIt(self.scriptsPath)

    @staticmethod
    def openCnsTool(*args):
        import CnsTool
        reload(CnsTool)
        CnsTool.CnsTool()

    @staticmethod
    def openScaleReaderTool(*args):
        import ScaleReader
        reload(ScaleReader)
        ScaleReader.ScaleReader()

    @staticmethod
    def openMassTools(*args):
        import MassTools
        reload(MassTools)
        MassTools.MassTools()

    @staticmethod
    def openColorSwitcher(*args):
        import ColorSwitcher
        reload(ColorSwitcher)
        ColorSwitcher.ColorSwitcher()

    @staticmethod
    def openUVtransMaster(*args):
        import UVtransMaster
        reload(UVtransMaster)
        UVtransMaster.UVtransMaster(scriptIt=True)

    def openWinTest(self, *args):
        import WinTest
        reload(WinTest)
        WinTest.WinTest()#'testName', 'Test Name')

    def openScriptItMaster(self, *args):
        scriptItPath = self.scriptsPath + "/ScriptItMaster"
        if os.path.exists(scriptItPath):
            if not scriptItPath in sys.path:
                sys.path.append(scriptItPath)

        import ScriptItMaster
        reload(ScriptItMaster)
        ScriptItMaster.ScriptItMaster(self.scriptsPath)

    @staticmethod
    def openColliderTool(*args):
        import ColliderTool
        reload(ColliderTool)
        ColliderTool.ColliderTool()

    @staticmethod
    def openSpringsColliderTool(*args):
        import SpringsCollider
        reload(SpringsCollider)
        SpringsCollider.SpringsCollider()

    @staticmethod
    def openBspDuplicator(*args):
        import BspDuplicator
        reload(BspDuplicator)
        BspDuplicator.BspDuplicator()

    def queryLocation(self):
        return self.scriptsPath

    # todo check if any of the following is needed
    '''
    def cleanupTools(self, parent='None'):
        if parent == 'None':
            return "Can't load Function"
        self.widgets[("cleaupTools_frameLayout")] = cmds.frameLayout(label="cleanup tools", collapsable=True,
                                                                     collapse=True, bgc=self.mainBGC, parent=parent)
        self.widgets[("handy_mainLayout")] = cmds.columnLayout(columnAttach=('both', 1), rowSpacing=2, columnWidth=200,
                                                              bgc=self.mediumGreen,
                                                              parent=self.widgets[("cleaupTools_frameLayout")])
        cmds.button(l='delete empty groups', w=105, h=26)
        cmds.button(l='delete empty layers', w=105, h=26)
        cmds.button(l='delete empty layers', w=105, h=26)


    def bottomToolsPopulate(self):
        cmds.separator(height=6, style='out', parent=self.widgets["mainLayout"])

        self.easyCodingReferences(parent=self.widgets["mainLayout"])

        cmds.separator(height=6, style='out', parent=self.widgets["mainLayout"])


    def easyCodingReferences(self, parent='None'):
        if parent == 'None':
            return "Can't load Function"
        self.widgets["codingReferences_frameLayout"] = cmds.frameLayout(label="Easy coding references",
                                                                        bgc=self.darkGreen, collapsable=True, cl=0,
                                                                        parent=parent)
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


    def checkInitMaterial(self):
        material = self.initMaterial
        return material


    def saveSR_Preset(self, *args):
        return 'None'


    def loadSR_Preset(self, *args):
        return 'None'


    def tabSwitcher(self, tab, *args):
        # example to call this function:
        # for tab in range(len(self.tabs)):
        # self.widgets[self.tabs[tab]] = cmds.button()
        #	 cmds.button( self.widgets[self.tabs[tab]], edit = True , c = partial(self.tabSwitcher, tab) )
        cmds.tabLayout(self.widgets["tabLayout"], edit=True, selectTabIndex=tab + 1)

    # this is for a sinoptic selection (should have a working version in original rigamir)
    def selectControls(self, controls, buttonInfo, *args):
        # buttonInfo = {[buttonName, buttonBGC]}
        # if you have shift held down = 1, ctl = 4, alt = 8
        mods = cmds.getModifiers()
        if (mods & 1) > 0:

            for i in range(len(controls)):
                cmds.select(controls[i], tgl=True)

                buttonName = buttonInfo[i][0]
                buttonBGC = buttonInfo[i][1]

                cmds.button(buttonName, edit=True, bgc=[1.0, 1.0, 1.0])
                ++i

                # call out script job
                self.createSelectionScriptJob(controls[i], buttonName, buttonBGC)

        # if no modifiers:
        else:
            cmds.select(clear=True)

            for i in range(len(controls)):
                cmds.select(controls[i], tgl=True)

                buttonName = buttonInfo[i][0]
                buttonBGC = buttonInfo[i][1]

                cmds.button(buttonName, edit=True, bgc=[1.0, 1.0, 1.0])
                ++i

                # call out script job
                self.createSelectionScriptJob(controls[i], buttonName, buttonBGC)


    def createSelectionScriptJob(self, control, buttonName, buttonBGC):
        scriptJobNum = cmds.scriptJob(
            event=["SelectionChanged", partial(self.deselectButton, control, buttonName, buttonBGC)],
            runOnce=True, parent=self.widgets["window"])


    def deselectButton(self, control, buttonName, buttonBGC):
        selection = cmds.ls(sl=True)

        if control not in selection:
            cmds.button(buttonName, edit=True, bgc=buttonBGC)

        else:
            self.createSelectionScriptJob(control, buttonName, buttonBGC)


    def sliderToFieldUpdater(self, slider, field):
        value = cmds.floatSlider(slider, q=True, v=True)
        cmds.floatField(field, value=value, e=True)

        # for name in categoryNames:
        # create a frame layout
        widgets["first_frameLayout"] = cmds.frameLayout(label = name, collapsable = True, 
                                                parent = widgets["mainLayout"])
        widgets["second_frameLayout"] = cmds.rowColumnLayout(nc = 3,
                                                parent = widgets[(name + "_frameLayout")])

        #for icon in iconsToShow:
        niceName = icon.partition(".")[0]
        category = icon.partition("__")[0]
        command = icon.partition("__")[2].partition(".")[0]

        widgets[(icon + "_button")] = cmds.symbolButton(w = 50, h = 50,
                                    image = (IconPath + icon), parent = widgets[(category + "_mainLayout")])
    '''
    '''
    def populateIcons(self):
        icons = os.listdir(self.IconPath)

        categories = []
        iconsToShow = []
        for icon in icons:
            if "__" in icon:
                iconsToShow.append(icon)
                categoryName = icon.partition("__")[0]
                categories.append(categoryName)

        categoryNames = list(set(categories))

        for name in categoryNames:
            # create a frame layout
            self.widgets[(name + "_frameLayout")] = cmds.frameLayout(label = name, collapsable = True,
                                                                     parent = self.widgets["mainLayout"])
            self.widgets[(name + "_mainLayout")] = cmds.rowColumnLayout(nc = 3,
                                                                        parent = self.widgets[(name + "_frameLayout")])

        for icon in iconsToShow:
            niceName = icon.partition(".")[0]
            category = icon.partition("__")[0]
            command = icon.partition("__")[2].partition(".")[0]

            self.widgets[(icon + "_button")] = cmds.symbolButton(w = 50, h = 50, image = (IconPath + icon),
                                                            parent = self.widgets[(category + "_mainLayout")],
                                                            c = partial(runMethod, command))
    '''
