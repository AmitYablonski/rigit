from maya import cmds, mel
import pymel.core as pm
import generalMayaTools as gmt
import re
import os, sys

__author__ = 'Amir Ronen'


####        ##    create lite wrap deformers    ##        ####


class LiteWrap:

    def __init__(self, parent):

        self.heavy = ''
        self.faces = []
        self.followObj = ''
        self.widgets = {}
        self.liteWrap(parent)

    def liteWrap(self, parent='None'):
        if parent == 'None':
            return ("Can't load LiteWrap")
        self.widgets["liteWrap_mainLayout"] = cmds.rowColumnLayout("Lite Wrap", nc=1, p=parent, adj=True)
        # rtf=True, w=400
        # widgets["settingsMenuBar"] = cmds.menuBarLayout()
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
        cmds.button(l='Compile ScriptIt!', w=150, h=50, c=self.scripIt)  # w=SnowRigUI.buttonW3, bgc=SnowRigUI.dockBGC,
        cmds.separator(h=4, p=self.widgets["liteWrap_mainLayout"], vis=False)

        cmds.separator(h=7, p=self.widgets["liteWrap_mainLayout"])
        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False,
                                                           p=self.widgets["liteWrap_mainLayout"])
        self.defaultFeedback()


    def updateObject(self, field='', *args):
        self.defaultFeedback()
        if field == '': return
        if field == 'heavy_text':
            self.heavy = cmds.textField(self.widgets[field], q=True, tx=True)
        else:
            self.followObj = cmds.textField(self.widgets[field], q=True, tx=True)

    @staticmethod
    def getScript(*args):
        if script:
            return script
        else:
            return False

    def scripIt(self, *args):
        self.defaultFeedback()
        heavy = cmds.textField(self.widgets["heavy_text"], q=True, tx=True)
        faces = cmds.textField(self.widgets["faces_text"], q=True, tx=True)
        followObj = cmds.textField(self.widgets["follow_text"], q=True, tx=True)
        if heavy == '':
            self.changeFeedback("No heavy mesh is selected (mesh to follow)", 'red')
            return
        if faces == '':
            self.changeFeedback("No faces were selected (faces to delete from the heavy mesh)", 'red')
            return
        if followObj == '':
            self.changeFeedback("No follow mesh is selected (mesh to wrap)", 'red')
            return
        script = self.getLiteWrapDef() + "\n"
        script += 'objToWrap = "%s"\n' % followObj
        script += 'heavyMesh = "%s"\n' % heavy
        script += 'deleteFaces = %s\n' % faces
        script += 'wrapObj, wrapNode = liteWrap(objToWrap, heavyMesh, deleteFaces)\n'
        global script
        self.changeFeedback("Compiled!", "green")

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
            self.changeFeedback("Please make a selection and try again", "red")
            return
        if ".f[" not in selection[0]:
            self.changeFeedback("Invalid selection. Please select polygon faces.", "red")
            return
        if not self.heavy:
            self.heavy = selection[0].rpartition(".f[")[0]
            cmds.textField(self.widgets['heavy_text'], e=True, tx=self.heavy)
        if selection[0].rpartition(".f[")[0] != self.heavy:
            self.changeFeedback("Selected faces aren't part of the heavy mesh", "red")
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

    def getLiteWrapDef(self):
        methodScript = "def liteWrap(objToWrap, heavyMesh, deleteFaces):\n\t" +\
                "heavyMesh = pm.PyNode(heavyMesh)\n\t" +\
                "simpleGeo = pm.duplicate(heavyMesh, n=objToWrap + '_wrapper')[0]\n\t" +\
                "# delete faces\n\t" +\
                "pm.select(cl=True)\n\t" +\
                "for faces in deleteFaces:\n\t\t" +\
                    "pm.select(heavyMesh + faces, add=True)\n\t" +\
                "pm.delete(pm.ls(sl=True))\n\t" +\
                "# find deleteComponent node to reconnect it with the new shape\n\t" +\
                "heavyMeshShp = heavyMesh.listRelatives(s=True)[0]\n\t" +\
                "deleteComponentNode = pm.listConnections(heavyMeshShp, c=True, type='deleteComponent')[0][1]\n\t" +\
                "deleteComponentNode.rename('deleteComponent_' + objToWrap)\n\t" +\
                "# reconnect heavy geo\n\t" +\
                "attrOrigin = pm.connectionInfo(deleteComponentNode + '.inputGeometry', sfd=True)\n\t" +\
                "pm.connectAttr(attrOrigin, heavyMeshShp + '.inMesh', f=True)\n\t" +\
                "pm.connectAttr(heavyMeshShp + '.worldMesh[0]', deleteComponentNode + '.inputGeometry', f=True)\n\t" +\
                "# connect deleteComponentNode to new geo and wrap it\n\t" +\
                "simpleGeoShp = simpleGeo.listRelatives(s=True)[0]\n\t" +\
                "pm.connectAttr(deleteComponentNode + '.outputGeometry', simpleGeoShp + '.inMesh', f=True)\n\t" +\
                "pm.select(objToWrap, simpleGeo)\n\t" +\
                "cmds.CreateWrap()\n\t" +\
                "newWrap = pm.listConnections(simpleGeoShp, c=True, type='wrap')[0][1]\n\t" +\
                "newWrap.rename('wrap_' + objToWrap)\n\t" +\
                "return simpleGeo, newWrap\n"
        return methodScript

    def defaultFeedback(self):
        self.changeFeedback("Lite Wrap")

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)
