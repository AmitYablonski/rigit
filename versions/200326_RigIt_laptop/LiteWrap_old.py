from maya import cmds, mel
import pymel.core as pm
import generalMayaTools as gmt
import re
import os, sys

__author__ = 'Amir Ronen'


####        ##    create lite wrap deformers    ##        ####


class LiteWrap():

    def __init__(self):

        self.heavy = ''
        self.faces = []
        self.followObj = ''
        self.widgets = {}
        self.liteWrapTool()

    def liteWrapTool(self):
        if cmds.window("liteWrap_window", exists=True):
            cmds.deleteUI("liteWrap_window")
        self.widgets["liteWrap_window"] = cmds.window("liteWrap_window", title="Lite Wrap Tool", sizeable=1,
                                                      rtf=True, w=400)  # w=SnowRigUI.buttonW3*6+10)
        # widgets["settingsMenuBar"] = cmds.menuBarLayout()
        self.widgets["liteWrap_mainLayout"] = cmds.rowColumnLayout(nc=1,
                                                                   p=self.widgets["liteWrap_window"])
        # heavy object
        cmds.text("Create a Lite Wrap deformer.", font='boldLabelFont')
        cmds.separator(h=7, vis=False)
        cmds.text("Step 1: Select the main mesh to follow", font='boldLabelFont')
        self.widgets["heavyObj_Layout"] = cmds.rowColumnLayout(nc=2, cs=[2, 5],  # rs=[2, 2], # bgc=self.darkGreen,
                                                               p=self.widgets["liteWrap_mainLayout"])
        self.widgets["heavy_button"] = cmds.button(l='Select heavy mesh',  # w=SnowRigUI.buttonW3,
                                                   c=lambda *_: self.updateTextField(
                                                       'heavy_text'))  # bgc=SnowRigUI.dockBGC,
        self.widgets['heavy_text'] = cmds.textField(w=300, tcc=lambda *_:self.updateObject('heavy_text'))
        # faces selection
        cmds.separator(h=4, p=self.widgets["liteWrap_mainLayout"], vis=False)
        cmds.text("Step 2: Select the faces to remove", p=self.widgets["liteWrap_mainLayout"], font='boldLabelFont')

        self.widgets["faces_Layout"] = cmds.rowColumnLayout(nc=3, cs=[2, 5],  # rs=[2, 2], # bgc=self.darkGreen,
                                                            p=self.widgets["liteWrap_mainLayout"])
        cmds.rowColumnLayout(self.widgets["faces_Layout"], e=True, cs=[3, 5])
        self.widgets["faces_button"] = cmds.button(l='Select faces',  # w=SnowRigUI.buttonW3,
                                                   c=lambda *_: self.faceLister(add=False))  # bgc=SnowRigUI.dockBGC,
        self.widgets["add_faces"] = cmds.button(l='Add faces',  # w=SnowRigUI.buttonW3,
                                                c=lambda *_: self.faceLister(add=True))  # bgc=SnowRigUI.dockBGC,
        # object to wrap
        self.widgets['faces_text'] = cmds.textField(w=268)
        cmds.separator(h=4, p=self.widgets["liteWrap_mainLayout"], vis=False)
        cmds.text("Step 3: Select the mesh to wrap", p=self.widgets["liteWrap_mainLayout"], font='boldLabelFont')
        self.widgets["follow_Layout"] = cmds.rowColumnLayout(nc=2, cs=[2, 5],  # rs=[2, 2], # bgc=self.darkGreen,
                                                             p=self.widgets["liteWrap_mainLayout"])
        self.widgets["follow_button"] = cmds.button(l='Select follow mesh',  # w=SnowRigUI.buttonW3,
                                                    c=lambda *_: self.updateTextField(
                                                        'follow_text'))  # bgc=SnowRigUI.dockBGC,
        self.widgets['follow_text'] = cmds.textField(w=299, tcc=lambda *_:self.updateObject('follow_text'))
        cmds.separator(h=4, p=self.widgets["liteWrap_mainLayout"], vis=False)
        cmds.rowColumnLayout(nc=2, p=self.widgets["liteWrap_mainLayout"])
        cmds.button(w=130, vis=False)
        cmds.button(l='Execute', w=150, h=50, c=self.liteWrap)  # w=SnowRigUI.buttonW3, bgc=SnowRigUI.dockBGC,
        cmds.separator(h=4, p=self.widgets["liteWrap_mainLayout"], vis=False)

        cmds.separator(h=7, p=self.widgets["liteWrap_mainLayout"])
        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False,
                                                           p=self.widgets["liteWrap_mainLayout"])
        self.defaultFeedback()
        cmds.showWindow()

    def updateObject(self, field='', *args):
        self.defaultFeedback()
        if field == '': return
        if field == 'heavy_text':
            self.heavy = cmds.textField(self.widgets[field], q=True, tx=True)
        else:
            self.followObj = cmds.textField(self.widgets[field], q=True, tx=True)

    def liteWrap(self, *args):
        self.defaultFeedback()
        if self.heavy == '':
            self.changeFeedback("No heavy mesh is selected (mesh to follow)", 'red')
            return
        if self.faces == '':
            self.changeFeedback("No faces were selected (faces to delete from the heavy mesh)", 'red')
            return
        if self.followObj == '':
            self.changeFeedback("No follow mesh is selected (mesh to wrap)", 'red')
            return
        simpleGeo = pm.duplicate(self.heavy)[0]
        pm.rename(simpleGeo, self.followObj + "_wrapper")
        # delete faces
        pm.select(cl=True)
        for face in self.faces:
            pm.select(self.heavy + face, add=True)
        sel = pm.ls(sl=True)
        pm.delete(sel)
        # find deleteComponent node and reconnect it with the new shape
        heavyShape = cmds.listRelatives(self.heavy, type="shape")[0]
        deleteComponentNode = pm.listConnections(heavyShape, c=True, type="deleteComponent")[0][1]
        heavyMeshAttr = heavyShape + ".inMesh"
        pm.rename(deleteComponentNode, "deleteComponent_" + self.followObj)
        # connect deleteComponentNode to new geo
        #simpleShape = cmds.listRelatives(simpleGeo, type="shape")[0]
        cmds.connectAttr(deleteComponentNode + ".outputGeometry", simpleGeo + "Shape.inMesh", f=True)
        # reconnect heavy geo
        attrOrigin = pm.connectionInfo(deleteComponentNode + ".inputGeometry", sfd=True)
        cmds.connectAttr(attrOrigin, heavyMeshAttr, f=True)
        cmds.connectAttr(heavyShape + ".worldMesh[0]", deleteComponentNode + ".inputGeometry", f=True)
        # Wrap it up!
        pm.select(self.followObj, simpleGeo)
        cmds.CreateWrap()
        newWrap = pm.listConnections(simpleGeo + "Shape", c=True, type="wrap")[0][1]
        temp = "%s" % newWrap
        pm.rename(newWrap, "wrap_" + self.followObj)
        print("LiteWrap => renamed "+temp+" to "+newWrap)
        print("LiteWrap => Wrapped " +self.followObj+ " on " +self.heavy+ " using " +simpleGeo)
        return simpleGeo, newWrap

    def updateTextField(self, field, *args):
        self.defaultFeedback()
        selection = cmds.ls(sl=True)
        if len(selection) == 1:
            cmds.textField(self.widgets[field], e=True, tx=selection[0])
            if field == 'heavy_text':
                self.heavy = selection[0]
            else:
                self.followObj = selection[0]
            return
        self.changeFeedback('Select a single mesh for the heavy/follow object', 'red')
        return

    # list faces names by selection (u'obj.f[2:5]' ==> u'.f[2:5]')
    def faceLister(self, add=False, *args):
        self.defaultFeedback()
        selection = cmds.ls(sl=True)
        if len(selection) == 0:
            self.changeFeedback("Please make a selection and try again", 'red')
            return
        if ".f[" not in selection[0]:
            self.changeFeedback("Invalid selection. Please select polygon faces.", 'red')
            return
        if not self.heavy:
            self.heavy = selection[0].rpartition(".f[")[0]
            cmds.textField(self.widgets['heavy_text'], e=True, tx=self.heavy)
        if selection[0].rpartition(".f[")[0] != self.heavy:
            self.changeFeedback("Selected faces aren't part of the heavy mesh", 'red')
            return
        if add:
            pm.select(cl=True)
            for face in self.faces:
                pm.select(self.heavy + face, add=True)
            cmds.select(selection, add=True)
            selection = cmds.ls(sl=True)
        # clean it for the text line
        faceList = []
        for item in selection:
            parts = item.rpartition(".f[")
            faceList.append(parts[1] + parts[2])
        cmds.textField(self.widgets['faces_text'], e=True, tx="%s" % faceList)
        self.faces = faceList
        self.changeFeedback("Selected faces are %s" % faceList)
        print("LiteWrap => Selected faces are %s" % faceList)

    def defaultFeedback(self):
        self.changeFeedback("Lite Wrap")

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)
