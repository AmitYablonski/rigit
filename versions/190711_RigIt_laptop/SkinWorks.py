from maya import cmds, mel
import pymel.core as pm
import generalMayaTools as gmt
from functools import partial
import re
import os, sys

__author__ = 'Amir Ronen'


class SkinWorks():

    def __init__(self):

        self.mainMesh = ''
        self.verts = []
        self.followObj = ''
        self.widgets = {}
        mainLayout = self.mainWindow()
        self.generalSkinTools(mainLayout)
        self.copySkinToVertsLayout(mainLayout)
        cmds.rowColumnLayout(nc=2, p=mainLayout)

    def mainWindow(self):
        if cmds.window("skinWorks_window", exists=True):
            cmds.deleteUI("skinWorks_window")
        self.widgets["mainWindow"] = cmds.window("skinWorks_window", title="SkinWorks", sizeable=1,
                                                  rtf=True)
        # widgets["settingsMenuBar"] = cmds.menuBarLayout()
        self.widgets["mainLayout"] = cmds.rowColumnLayout(nc=2, p=self.widgets["mainWindow"], adj=True)
        return self.widgets["mainLayout"]

    def generalSkinTools(self, mainLayout):
        buttonBgc = [.4, .4, .4]
        skinToolsLayout = cmds.rowColumnLayout(nc=1, p=mainLayout, bgc=[.25, .25, .25])
        cmds.separator(h=5, vis=True)
        cmds.text("General skin tools.", font='boldLabelFont')

        cmds.separator(h=4, vis=True)
        cmds.separator(h=7, vis=True)

        # general tools
        otherToolsLayout = cmds.rowColumnLayout(nc=3, p=skinToolsLayout, columnSpacing=[2, 6], rowSpacing=[2, 6])
        cmds.rowColumnLayout(otherToolsLayout, edit=True, columnSpacing=[1, 14])
        cmds.rowColumnLayout(otherToolsLayout, edit=True, columnSpacing=[3, 6], rowSpacing=[3, 6])
        cmds.button(l='Hammer\nWeights', c="mel.eval('weightHammerVerts')",
                    ann="Hammer skin weights", bgc=buttonBgc)
        cmds.button(l='Bind and\nCopy Skin', c=gmt.bindAndCopy, bgc=[0.4, 0.7, .3],
                    ann='select source, then target.\nbinds to the relevant joints and copy weights')
        cmds.button(l='Bind Skin', c=gmt.bindAndName, bgc=[0.2, 0.6, .2],
                    ann='Binds to selected joints and names the skinClusters')
        cmds.button(l='Select\nSkin/s', c=gmt.selectSkin, bgc=buttonBgc,
                    ann='select all skins for selection')

        cmds.separator(h=7, vis=True, p=skinToolsLayout)
        cmds.text('mGear skin', font='boldLabelFont', p=skinToolsLayout)
        cmds.separator(h=7, vis=True, p=skinToolsLayout)
        cmds.rowColumnLayout(nc=2, p=skinToolsLayout, columnSpacing=[2, 3])
        cmds.button("Import Skin", h=20, w=110, ann="Open settings window", bgc=[.6, .5, .8],
                    c="import mgear; mgear.maya.skin.importSkin()")
        cmds.button("Export Skin", h=20, w=110, ann="Open settings window", bgc=[.55, .45, .8],
                    c="import mgear; mgear.maya.skin.exportSkin()")
        cmds.separator(h=7, vis=True, p=skinToolsLayout)

        # jnt tools
        # moveJnts_Layout
        cmds.text("Edit Joints tools", font='boldLabelFont', p=skinToolsLayout)
        cmds.separator(h=7, vis=True, p=skinToolsLayout)
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=1, p=skinToolsLayout)
        cmds.text('move bound joint:', h=20, w=70)
        cmds.button(l='on', w=45, h=20, c='mel.eval("moveJointsMode 1;")', bgc=buttonBgc)
        cmds.button(l='off', w=45, h=20, c='mel.eval("moveJointsMode 0;")', bgc=buttonBgc)
        cmds.separator(h=7, vis=True, p=skinToolsLayout)

        # joints orient
        cmds.rowColumnLayout(nc=2, p=skinToolsLayout, columnSpacing=[2, 2], rowSpacing=[2, 2])
        cmds.text('Jnt Orients:')#, font='boldLabelFont')
        cmds.button(label='Zero joint Orients', ann="Zero joint rotate and joint orient.", w=106, bgc=buttonBgc,
                    c=gmt.zeroJntOrients)
        cmds.button(label='rotate to jnt Orient', ann="Transfer rotate values to joint orient", w=106, bgc=buttonBgc,
                    c=gmt.rotateToJntOrient)
        cmds.button(label='jnt orient to rotate ', ann="Transfer joint orient to rotation", w=106, bgc=buttonBgc,
                    c=partial(gmt.rotateToJntOrient, True))

        cmds.separator(h=7, vis=True, p=skinToolsLayout)
        cmds.separator(h=4, vis=True, p=skinToolsLayout)


    def copySkinToVertsLayout(self, mainLayout):
        skinToVertsLayout = cmds.rowColumnLayout(nc=1, p=mainLayout)
        # heavy object
        cmds.separator(h=5, vis=True)
        cmds.text("Copy skin from geo to verts.", font='boldLabelFont')
        cmds.text('Tool for copying skin from an object to verts selection (or set) easily\n'
                  '*possible to copy to the same mesh (e.g. an inside of a shirt etc)*')
        cmds.separator(h=7, vis=True)
        cmds.text("Step 1: Select the main mesh\n(with the desired weights)", font='boldLabelFont')
        self.widgets["mainMesh_Layout"] = cmds.rowColumnLayout(nc=2, cs=[2, 5],  # rs=[2, 2],
                                                               p=skinToVertsLayout)
        self.widgets["mainMesh_button"] = cmds.button(l='Select main mesh',
                                                      c=lambda *_: self.updateTextField('mainMesh_text'))
        self.widgets['mainMesh_text'] = cmds.textField(w=300, tcc=lambda *_: self.updateObject('mainMesh_text'))
        # faces selection
        cmds.separator(h=4, p=skinToVertsLayout, vis=True)
        cmds.text("Step 2: Select the vertecies to copy the weights to\n(can select by faces/edges)", p=skinToVertsLayout,
                  font='boldLabelFont')

        self.widgets["verts_Layout"] = cmds.rowColumnLayout(nc=3, cs=[2, 5],  # rs=[2, 2],
                                                            p=skinToVertsLayout)
        cmds.rowColumnLayout(self.widgets["verts_Layout"], e=True, cs=[3, 5])
        self.widgets["verts_button"] = cmds.button(l='Select verts',
                                                   c=lambda *_: self.vertsLister(add=False))
        self.widgets["add_verts"] = cmds.button(l='Add verts',
                                                c=lambda *_: self.vertsLister(add=True))
        # verts to transfer weights to
        self.widgets['verts_text'] = cmds.textField(w=268)
        cmds.separator(h=7, p=skinToVertsLayout, vis=True)
        cmds.text("Step 3: Copy weights from main mesh to selected verts", p=skinToVertsLayout, font='boldLabelFont')
        cmds.rowColumnLayout(nc=2, p=skinToVertsLayout)
        cmds.button(w=130, vis=False)
        cmds.button(l='Execute', w=150, h=50, c=self.copyToVerts)  # w=SnowRigUI.buttonW3, bgc=SnowRigUI.dockBGC,
        cmds.separator(h=5, p=skinToVertsLayout, vis=True)

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
