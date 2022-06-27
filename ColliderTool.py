from maya import cmds, mel
import pymel.core as pm
from functools import partial
import generalMayaTools as gmt

reload(gmt)


class ColliderTool:

    def __init__(self):

        self.selection = []
        self.widgets = {}
        self.collideMesh = ''
        self.collideObject = ''
        self.xDir = 0
        self.yDir = -1
        self.zDir = 0
        self.fat = 0.1
        self.colliderWin()

    def colliderWin(self):
        if cmds.window("colliderTool_window", exists=True):
            cmds.deleteUI("colliderTool_window")
        self.widgets["colliderTool_window"] = cmds.window("colliderTool_window", title="Collider", sizeable=1, rtf=True)
        self.widgets["collider_topMain_Layout"] = cmds.rowColumnLayout(numberOfColumns=1, adj=True)
        self.widgets["collider_main_Layout"] = cmds.rowColumnLayout(numberOfColumns=1, adj=True)
        colW = 100
        cmds.separator(h=7, p=self.widgets["collider_main_Layout"])
        cmds.text("Step 1 - Select mesh to collide with.", p=self.widgets["collider_main_Layout"])
        self.widgets["collider_meshLayout"] = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2,
                                                             p=self.widgets["collider_main_Layout"])
        cmds.button("Collider Mesh/s:", w=colW, c=partial(self.setMesh, "collider_mesh"))
        self.widgets["collider_mesh"] = cmds.textField(text="")

        cmds.separator(h=7, p=self.widgets["collider_main_Layout"])
        cmds.text("Step 2 - Select collider Object/s.", p=self.widgets["collider_main_Layout"])
        self.widgets["collider_objectLayout"] = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2,
                                                               p=self.widgets["collider_main_Layout"])
        cmds.button("Collider Object/s: ", w=colW, c=partial(self.setMesh, "collider_object"))
        self.widgets["collider_object"] = cmds.textField(text="")

        cmds.separator(h=7, p=self.widgets["collider_main_Layout"])
        cmds.text("Step 3 - Choose axis for collider to move along.", p=self.widgets["collider_main_Layout"])
        # radio buttons
        self.widgets["collider_axisLayout"] = cmds.rowColumnLayout(nc=2, adjustableColumn=2,
                                                                   p=self.widgets["collider_main_Layout"])
        cmds.text("     axis:    ")
        self.widgets["axis_floatFieldGrp"] = cmds.floatFieldGrp(numberOfFields=3, value2=-1.0, cc=self.updateAxis)

        cmds.separator(h=7, p=self.widgets["collider_main_Layout"])
        self.widgets["fatFloat"] = cmds.floatSliderGrp(l="fat:", field=True, min=0, max=2, v=0.1,
                                                       fieldMinValue=-100.0, fieldMaxValue=100.0, cc=self.fatFloat,
                                                       p=self.widgets["collider_main_Layout"])

        cmds.separator(h=7, p=self.widgets["collider_main_Layout"])
        cmds.button(l="Make Collider", c=self.makeCollider, p=self.widgets["collider_main_Layout"])
        # layout for controllers after collider creation
        self.widgets["colliderCtrls_Layout"] = cmds.rowColumnLayout(numberOfColumns=1, adj=True,
                                                                    p=self.widgets["collider_topMain_Layout"])
        cmds.separator(h=7, p=self.widgets["collider_topMain_Layout"])

        self.widgets["feedbackTextField"] = cmds.textField(tx="Attr Maker", editable=False,
                                                           p=self.widgets["collider_topMain_Layout"])
        self.defaultFeedback()

        cmds.showWindow()

        self.colliderControl()

    def fatFloat(self, *args):
        self.fat = cmds.floatSliderGrp(self.widgets["fatFloat"], q=True, v=True)

    def updateAxis(self, *args):
        self.xDir = cmds.floatFieldGrp(self.widgets["axis_floatFieldGrp"], q=True, value1=True)
        self.yDir = cmds.floatFieldGrp(self.widgets["axis_floatFieldGrp"], q=True, value2=True)
        self.zDir = cmds.floatFieldGrp(self.widgets["axis_floatFieldGrp"], q=True, value3=True)

    def setMesh(self, field, *args):
        sel = pm.ls(sl=True)
        mesh = sel[0].name()
        for i in range(1, len(sel)):
            mesh += ", " + sel[i].name()
        if "mesh" in field:
            self.collideMesh = sel
        else:
            self.collideObject = sel
        cmds.textField(self.widgets[field], e=True, tx=mesh)

    def makeCollider(self, *args):
        # initial checks
        if self.collideMesh == '':
            self.changeFeedback("No collide mesh selected")
            return
        if self.collideObject == '':
            self.changeFeedback("No collide object selected")
            return
        # add colliders (make muscles)
        if isinstance(self.collideMesh, (list, tuple)):
            for obj in self.collideMesh:
                # check if object is already a muscle object
                relatives = obj.listRelatives()
                for rel in relatives:
                    if isinstance(rel, pm.nodetypes.CMuscleObject):
                        print("Collider --> %s already connected" % obj.name())
                    else:
                        self.addCollideMesh(obj)
        else:
            if isinstance(self.collideMesh, pm.nodetypes.CMuscleObject):
                print("Collider --> %s already connected" % self.collideMesh.name())
            else:
                self.addCollideMesh(self.collideMesh.name())

        # create colliding objects
        keepOuts = {}
        if isinstance(self.collideObject, (list, tuple)):
            for obj in self.collideObject:
                keepOuts[obj] = self.addCollider(obj, name=obj.name() + '_coll')
        else:
            obj = self.collideObject
            keepOuts[obj.name()] = self.addCollider(obj, name=obj.name() + '_coll')
        for i in keepOuts:
            print "flipColliderParents(%s, %s, %s)" %(i, keepOuts[i][0], keepOuts[i][1])
            self.flipColliderParents(i, keepOuts[i][0], keepOuts[i][1])
            for colMesh in self.collideMesh:
                self.connectKeepOut(keepOuts[i][0], colMesh)
        # output messege
        messege = "Finished! [%s" % self.collideObject[0].name()
        for i in range(1, len(self.collideObject)):
            messege += ", " + self.collideObject[i].name()
        messege += "] are now colliding with [%s" % self.collideMesh[0].name()
        for i in range(1, len(self.collideMesh)):
            messege += ", " + self.collideMesh[i].name()
        self.changeFeedback(messege + "]", False)
        # give controller for the created colliders
        self.colliderControl(keepOuts)
        pm.select(d=True)

    def flipColliderParents(self, obj, keepout, driven):
        objParent = obj.listRelatives(p=True)
        if objParent:
            pm.parent(keepout, objParent[0])
            pm.parent(obj, driven)
        else:
            pm.parent(keepout, w=True)
            pm.parent(obj, driven)

    def addCollideMesh(self, obj):
        pm.select(obj)
        # should possibly add:
        # mel.eval('catch(`loadPlugin "C:/Program Files/Autodesk/Maya2017/bin/plug-ins/MayaMuscle.mll"`)')
        muscleMesh = pm.PyNode(mel.eval('cMuscle_makeMuscle(0)')[0])
        muscleMesh.setAttr("fat", self.fat)
        return muscleMesh

    def addCollider(self, obj, name=''):
        pm.select(obj)
        keepOut, keepOutShape, driven = mel.eval('cMuscle_rigKeepOutSel()')
        pm.setAttr(keepOut+".inDirectionX", self.xDir)
        pm.setAttr(keepOut+".inDirectionY", self.yDir)
        pm.setAttr(keepOut+".inDirectionZ", self.zDir)
        keepOut, driven = pm.PyNode(keepOut), pm.PyNode(driven)
        if name != '':
            pm.rename(keepOut, name)
            pm.rename(driven, name + '_cMuscleKeepOutDriven')
        return (keepOut, driven)

    def connectKeepOut(self, keepOut, collideMesh):
        pm.select(keepOut, collideMesh)
        mel.eval('cMuscle_keepOutAddRemMuscle(1)')

    def defaultFeedback(self):
        cmds.textField(self.widgets["feedbackTextField"], e=True, tx="Collider Tool")

    def changeFeedback(self, messege, error=True):
        bg = (.6, .3, .3)
        if not error:
            bg = (.3, .6, .3)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)

    def colliderControl(self, keepOuts):
        i = 0
        winName = "colliderCtrl_window"
        while cmds.window(winName + str(i), exists=True):
            i += 1
        cmds.window(winName + str(i), title="Collider Settings", sizeable=1, rtf=True)
        mainLayout = cmds.rowColumnLayout(numberOfColumns=1, adj=True)
        cmds.separator(h=7)
        # set header with proper names:
        '''
        colStr = gmt.stringMyPmList(self.collideObject)
        meshStr = gmt.stringMyPmList(self.collideMesh)
        if not colStr:
            colStr = ""
        if not meshStr:
            meshStr = ""
        '''

        cmds.text('Settings for the new collider/s and Muscle object/s', font='boldLabelFont')
        cmds.separator(h=7)
        fatLayout = cmds.rowColumnLayout(nc=1, p=mainLayout)
        cmds.separator(h=7, p=mainLayout)
        axisLayout = cmds.rowColumnLayout(nc=1, p=mainLayout)

        self.connectColliderAttrs(fatLayout, axisLayout, keepOuts)

        cmds.showWindow()

    def connectColliderAttrs(self, fatLayout, axisLayout, keepOuts):
        # connect meshes
        if isinstance(self.collideMesh, (list, tuple)):
            for obj in self.collideMesh:
                self.colliderMeshConnect(obj, fatLayout)
                print("connect %s collider attrs" % obj)
        else:
            self.colliderMeshConnect(self.collideMesh, fatLayout)
            print("connect %s collider attrs" % self.collideMesh)
        # connect objects
        for obj in keepOuts:
            self.colliderObjConnect(keepOuts[obj][0], obj, axisLayout)
            print("connect %s collider attrs" % obj)

    def colliderMeshConnect(self, obj, layoutP):
        relatives = obj.listRelatives()
        muscles = []
        for rel in relatives:
            if isinstance(rel, pm.nodetypes.CMuscleObject):
                muscles.append(rel)
        for mus in muscles:
            cmds.text('muscle object "' + obj.name() + '":', p=layoutP, align="left")
            pm.attrFieldSliderGrp(at='%s.fat' % mus, p=layoutP,
                                  min=0, max=5, fieldMinValue=-100.0, fieldMaxValue=100.0)

    def colliderObjConnect(self, keepOut, obj, layoutP):
        cmds.text('collider object "%s":' % obj.name(), p=layoutP, align="left")
        field = pm.attrFieldGrp(p=layoutP)
        field.setAttribute(keepOut.inDirection)
        field.setLabel('axis')

