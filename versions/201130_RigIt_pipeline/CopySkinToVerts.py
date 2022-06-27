from maya import cmds, mel
import pymel.core as pm
import generalMayaTools as gmt
import re
import os, sys

__author__ = 'Amir Ronen'


class CopySkinToVerts():

    def __init__(self):

        self.mainMesh = ''
        self.verts = []
        self.followObj = ''
        self.widgets = {}
        self.copySkinToVertsWin()

    def copySkinToVertsWin(self):
        if cmds.window("cstv_window", exists=True):
            cmds.deleteUI("cstv_window")
        self.widgets["cstv_window"] = cmds.window("cstv_window", title="Copy Skin To Verts", sizeable=1,
                                                  rtf=True, w=400)
        # widgets["settingsMenuBar"] = cmds.menuBarLayout()
        self.widgets["cstv_mainLayout"] = cmds.rowColumnLayout(nc=1,
                                                               p=self.widgets["cstv_window"])
        # heavy object
        cmds.separator(h=5, vis=True)
        cmds.text("Copy skin from geo to verts.", font='boldLabelFont')
        cmds.separator(h=7, vis=True)
        cmds.text("Step 1: Select the main mesh\n(with the desired weights)", font='boldLabelFont')
        self.widgets["mainMesh_Layout"] = cmds.rowColumnLayout(nc=2, cs=[2, 5],  # rs=[2, 2],
                                                               p=self.widgets["cstv_mainLayout"])
        self.widgets["mainMesh_button"] = cmds.button(l='Select main mesh',
                                                      c=lambda *_: self.updateTextField('mainMesh_text'))
        self.widgets['mainMesh_text'] = cmds.textField(w=300, tcc=lambda *_: self.updateObject('mainMesh_text'))
        # faces selection
        cmds.separator(h=4, p=self.widgets["cstv_mainLayout"], vis=True)
        cmds.text("Step 2: Select the vertecies to copy the weights to\n(can select by faces/edges)", p=self.widgets["cstv_mainLayout"],
                  font='boldLabelFont')

        self.widgets["verts_Layout"] = cmds.rowColumnLayout(nc=3, cs=[2, 5],  # rs=[2, 2],
                                                            p=self.widgets["cstv_mainLayout"])
        cmds.rowColumnLayout(self.widgets["verts_Layout"], e=True, cs=[3, 5])
        self.widgets["verts_button"] = cmds.button(l='Select verts',
                                                   c=lambda *_: self.vertsLister(add=False))
        self.widgets["add_verts"] = cmds.button(l='Add verts',
                                                c=lambda *_: self.vertsLister(add=True))
        # verts to transfer weights to
        self.widgets['verts_text'] = cmds.textField(w=268)
        cmds.separator(h=7, p=self.widgets["cstv_mainLayout"], vis=True)
        cmds.text("Step 3: Copy weights from main mesh to selected verts", p=self.widgets["cstv_mainLayout"], font='boldLabelFont')
        cmds.rowColumnLayout(nc=2, p=self.widgets["cstv_mainLayout"])
        cmds.button(w=130, vis=False)
        cmds.button(l='Execute', w=150, h=50, c=self.copyToVerts)  # w=SnowRigUI.buttonW3, bgc=SnowRigUI.dockBGC,
        cmds.separator(h=5, p=self.widgets["cstv_mainLayout"], vis=True)

        cmds.showWindow()


    def updateObject(self, field='', *args):
        if field == '': return
        if field == 'mainMesh_text':
            self.mainMesh = cmds.textField(self.widgets[field], q=True, tx=True)


    def copyToVerts(self, *args):
        if self.mainMesh == '':
            print(" => No Main Mesh is selected (mesh to take skin from)")
            return
        if self.verts == '':
            print(" => No vertecies were selected (verts to copy the weights to)")
            return
        if self.verts[0].partition(".")[0] == self.mainMesh:
            print(" => Selected vertecies are on the main mesh,"
                  "will create a duplicate to transfer weights to and back")
            dup = pm.duplicate(self.mainMesh)[0]
            pm.select(cl=True)
            for vert in self.verts:
                temp = vert.partition(".vtx[")
                dupVert = dup + ".vtx[" + temp[2]
                pm.select(dupVert, add=True)
            #print("dup Selection: %s" %pm.ls(sl=True))
            mel.eval('ConvertSelectionToFaces')
            pm.delete()
            # copy weights from mainMesh to duplicate
            pm.select(self.mainMesh, dup)
            gmt.bindAndCopy()
            # copy weights from duplicate to verts
            pm.select(dup, self.verts)
            pm.copySkinWeights(sa="closestPoint", ia="oneToOne", noMirror=True)
            pm.delete(dup)
        else:
            pm.select(self.mainMesh, self.verts)
            pm.copySkinWeights(sa="closestPoint", ia="oneToOne", noMirror=True)



    def updateTextField(self, field, *args):
        selection = cmds.ls(sl=True)
        if len(selection) == 1:
            cmds.textField(self.widgets[field], e=True, tx=selection[0])
            if field == 'verts_text':
                self.mainMesh = selection[0]
        else:
            print(' => Please select a single mesh for the Main Mesh')


    def vertsLister(self, add=False, *args):
        selection = cmds.ls(sl=True)
        if len(selection) == 0:
            print("=> Please make a selection and try again")
            return
        if ".f[" in selection[0] or ".e[" in selection[0]:
            mel.eval('ConvertSelectionToVertices')
            selection = cmds.ls(sl=True)
            # todo convert selection to verts
        if not self.mainMesh:
            # todo give appropriate error
            print("No main mesh is selected to transfer weights from")
            # self.mainMesh = selection[0].rpartition(".f[")[0]
            # cmds.textField(self.widgets['mainMesh_text'], e=True, tx=self.mainMesh)
        if add:
            pm.select(self.verts)
            cmds.select(selection, add=True)
            selection = cmds.ls(sl=True)
        # clean it for the text line
        self.verts = selection
        '''
        vertsList = []
        for item in selection:
            parts = item.rpartition(".vtx[")
            vertsList.append(parts[1] + parts[2])
        self.verts = vertsList
        '''
        cmds.textField(self.widgets['verts_text'], e=True, tx="%s" % self.verts)
        print("=> Selected verts are %s" % self.verts)
