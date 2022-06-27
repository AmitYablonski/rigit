from maya import cmds, mel
import pymel.core as pm
from functools import partial
import UI_modules as uim
import RigItMethodsUI as rim

reload(uim)


class LiteWrap:
    def __init__(self, par='', scriptIt=False):
        self.widgets = {}
        self.heavy = ''
        self.faces = []
        self.followObj = ''
        self.feedbackName = 'Lite Wrap'
        
        topLay, mainLay = self.winBase('LiteWrap', self.feedbackName, par)
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def liteWrap(self, objToWrap, heavyMesh, deleteFaces):
        heavyMesh = pm.PyNode(heavyMesh)
        simpleGeo = pm.duplicate(heavyMesh, n=objToWrap + '_wrapper')[0]
        # delete faces
        pm.select(cl=True)
        for faces in deleteFaces:
            pm.select(heavyMesh + faces, add=True)
        pm.delete(pm.ls(sl=True))
        # find deleteComponent node to reconnect it with the new shape
        heavyMeshShp = heavyMesh.listRelatives(s=True)[0]
        deleteComponentNode = pm.listConnections(heavyMeshShp, c=True, type='deleteComponent')[0][1]
        deleteComponentNode.rename('deleteComponent_' + objToWrap)
        # reconnect heavy geo
        attrOrigin = pm.connectionInfo(deleteComponentNode + '.inputGeometry', sfd=True)
        pm.connectAttr(attrOrigin, heavyMeshShp + '.inMesh', f=True)
        pm.connectAttr(heavyMeshShp + '.worldMesh[0]', deleteComponentNode + '.inputGeometry', f=True)
        # connect deleteComponentNode to new geo and wrap it
        simpleGeoShp = simpleGeo.listRelatives(s=True)[0]
        pm.connectAttr(deleteComponentNode + '.outputGeometry', simpleGeoShp + '.inMesh', f=True)
        pm.select(objToWrap, simpleGeo)
        cmds.CreateWrap()
        newWrap = pm.listConnections(simpleGeoShp, c=True, type='wrap')[0][1]
        newWrap.rename('wrap_' + objToWrap)
        return simpleGeo, newWrap

    def execute(self, *args):
        self.defaultFeedback()
        heavyMesh, deleteFaces, objToWrap = self.getUiData()
        if not heavyMesh and self.validObjects([heavyMesh, objToWrap]):
            return
        wrapObj, wrapNode = self.liteWrap(objToWrap, heavyMesh, deleteFaces)
        pm.select(wrapObj)

    def scriptIt(self, *args):
        self.defaultFeedback()
        heavyMesh, deleteFaces, objToWrap = self.getUiData()
        if not heavyMesh:
            return
        script = 'import pymel.core as pm\nfrom maya import cmds, mel\n\n\n'
        script += self.getLiteWrapDef() + "\n"
        script += 'objToWrap = "%s"\n' % objToWrap
        script += 'heavyMesh = "%s"\n' % heavyMesh
        script += 'deleteFaces = %s\n' % deleteFaces
        script += 'wrapObj, wrapNode = liteWrap(objToWrap, heavyMesh, deleteFaces)\n'
        global script
        self.changeFeedback("Compiled!", "green")
        rim.showScript(script)

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

    def validObjects(self, toValidate):
        if isinstance(toValidate, list) or isinstance(toValidate, tuple):
            for obj in toValidate:
                if not pm.objExists(obj):
                    self.printFeedback('Error finding objs: %s' % obj)
                    return False
        else:
            if not pm.objExists(toValidate):
                self.printFeedback('Error finding objs: %s' % toValidate)
                return False
        return True

    def getUiData(self):
        heavy = cmds.textField(self.widgets["heavy_text"], q=True, tx=True)
        faces = cmds.textField(self.widgets["faces_text"], q=True, tx=True)
        followObj = cmds.textField(self.widgets["follow_text"], q=True, tx=True)
        if not heavy:
            self.changeFeedback("No heavy mesh is selected (mesh to follow)", 'red')
            return False, False, False
        if not faces:
            self.changeFeedback("No faces were selected (faces to delete from the heavy mesh)", 'red')
            return False, False, False
        if not followObj:
            self.changeFeedback("No follow mesh is selected (mesh to wrap)", 'red')
            return False, False, False
        return heavy, faces, followObj

    def populateUI(self, mainLay, scriptIt):

        pm.separator(h=7, p=mainLay)
        pm.text(l='Create a Lite Wrap deformer', font='boldLabelFont', p=mainLay)
        pm.separator(h=7, p=mainLay)
        pm.text("Step 1: Select the main mesh to follow", p=mainLay)#, font='boldLabelFont'

        self.widgets["heavy_text"] = uim.selectAndAddToField(self, mainLay, 'Select heavy mesh', 'transform')

        # faces selection
        #cmds.separator(h=4, p=mainLay)#, style='none')
        cmds.text("Step 2: Select the faces to remove", p=mainLay)#, font='boldLabelFont')

        self.widgets["faces_Layout"] = cmds.rowColumnLayout(nc=3, cs=[[2, 5], [3, 5]], p=mainLay)
        self.widgets["faces_button"] = cmds.button(l='Select faces', c=lambda *_: self.faceLister(add=False))
        self.widgets["add_faces"] = cmds.button(l='Add faces', c=lambda *_: self.faceLister(add=True))
        self.widgets['faces_text'] = cmds.textField(w=268)

        # object to wrap
        cmds.separator(h=4, p=mainLay, style='none')
        cmds.text("Step 3: Select the mesh to wrap", p=mainLay)#, font='boldLabelFont')

        self.widgets["follow_text"] = uim.selectAndAddToField(self, mainLay, 'Select follow mesh', 'transform')

        # buttons
        cmds.separator(h=15, p=mainLay)#, style='none')
        cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
        cmds.button(l='Execute', h=28, c=self.execute)
        if scriptIt:
            cmds.button(l='Script it', w=100, c=self.scriptIt)
        else:
            pm.separator(w=100, style='none')
        cmds.separator(h=3, p=mainLay, style='none')

    # list faces names by selection (u'obj.f[2:5]' ==> u'.f[2:5]')
    def faceLister(self, add=False, *args):
        self.defaultFeedback()
        selection = cmds.ls(sl=True)
        if len(selection) == 0:
            self.printFeedback("Please make a selection and try again")
            return
        if ".f[" not in selection[0]:
            self.printFeedback("Invalid selection. Please select polygon faces.")
            return
        if not self.heavy:
            self.heavy = selection[0].rpartition(".f[")[0]
            cmds.textField(self.widgets['heavy_text'], e=True, tx=self.heavy)
        if selection[0].rpartition(".f[")[0] != self.heavy:
            self.printFeedback("Selected faces aren't part of the heavy mesh")
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
        self.printFeedback("Selected faces are %s" % faceList, 'none')


    def winBase(self, name, title, par):
        winName = name + "_window"
        mainLay = "mainLay"
        topLay = "topLay"
        asWindow = True
        if par:
            print(' // %s - creating Layout under parent' % self.feedbackName)
            asWindow = False
        if asWindow:
            if cmds.window(winName, exists=True):
                cmds.deleteUI(winName)
            self.widgets[winName] = cmds.window(winName, title=title, sizeable=1, rtf=True)
            self.widgets[topLay] = cmds.columnLayout(adj=True)
        else:
            self.widgets[topLay] = cmds.columnLayout(title, adj=True, p=par)
        self.widgets[mainLay] = cmds.columnLayout(adj=True)
        pm.separator(h=7, p=self.widgets[topLay])
        self.widgets["feedback"] = cmds.textField(tx="", editable=False, p=self.widgets[topLay])
        if asWindow:
            cmds.showWindow()
        self.defaultFeedback()
        return self.widgets[topLay], self.widgets[mainLay]

    def greenFeedback(self, text):
        self.printFeedback(text, 'green')

    def orangeFeedback(self, text):
        self.printFeedback(text, 'orange')

    def printFeedback(self, text, color=''):
        error = ' // %s : %s' % (self.feedbackName, text)
        print(error)
        fColor = 'red'
        if color:
            fColor = color
        self.changeFeedback(error, fColor)

    def defaultFeedback(self):
        self.changeFeedback('// %s' % self.feedbackName)

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.7, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedback"], e=True, bgc=bg, tx=messege)
