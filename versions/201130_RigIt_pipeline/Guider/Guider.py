import pymel.core as pm
import mgear.maya.shifter as shifter


class Guider:
    def __init__(self):
        # super(guiderClass, self).__init__()
        self.ctlShape = "circle"
        self.ctlJnt = True
        self.worldOri = False

    def guideNamer(self, obj):
        new_name = obj.name().replace('_grp', '').title().replace('_', '').replace(' ', '')
        return new_name[0].lower() + new_name[1:]

    def createGuide(self, obj, parnt, index, ctlShape, ctlJnt, worldOri):  # obj - the object that will
        guide = shifter.guide.Rig()
        guideName = self.guideNamer(obj)
        guide.drawNewComponent(parnt, 'control_01')
        root = pm.PyNode("control_C0_root")
        pm.setAttr(root.icon, ctlShape)
        pm.setAttr(root.joint, ctlJnt)
        pm.setAttr(root.neutralRotation, worldOri)
        ComponentGuide = shifter.component.guide.ComponentGuide()
        ComponentGuide.rename(root, guideName, "C", index)
        nCon = pm.parentConstraint(obj, root, mo=0)
        pm.delete(nCon)

    def quickRig(self, obj):
        if not pm.objExists("local_C0_root"):
            self.createLocal()
        # local = pm.PyNode("guide|local_C0_root")
        self.createGuidesFromObjects(obj)
        pm.ls("guide")
        shifter.Rig().buildFromSelection()
        # jnt = self.guideNamer(obj)
        # print jnt
        # pm.select(obj)
        # pm.select(jnt, add=True)
        # pm.skinCluster()

    def connectCtl(self, obj):
        ctl = pm.PyNode(self.guideNamer(obj) + "_C0_ctl")
        pm.parentConstraint(ctl, obj, mo=True)
        pm.scaleConstraint(ctl, obj, mo=True)

    def createLocal(self):
        guide = shifter.guide.Rig()
        guide.drawNewComponent(None, 'control_01')
        root = pm.PyNode('control_C0_root')
        pm.setAttr(root.icon, "square")
        ComponentGuide = shifter.component.guide.ComponentGuide()
        ComponentGuide.rename(root, "local", "C", 0)

    # catch selected objects and sort them
    def sortList(self, objects):
        # objects = pm.ls(sl=True)
        sortedList = []
        for obj in objects:
            sortedList.append(obj.longName())
        sortedList.sort()
        objects = []
        for obj in sortedList:
            objects.append(pm.PyNode(obj))

    # create guides to objects
    def createGuidesFromObjects(self, objects, jnt=True, ori=False, shape="circle"):
        self.ctlJnt = jnt
        self.worldOri = ori
        self.ctlShape = shape
        if not pm.objExists("local_C0_root"):
            self.createLocal()
        local = pm.PyNode("guide|local_C0_root")
        for obj in objects:
            parnt = self.checkParent(obj,local)
            self.createGuide(obj, parnt, 0, self.ctlShape, self.ctlJnt, self.worldOri)

    def checkParent(self, obj,local):
        obj = pm.PyNode(obj)
        par = obj.getParent()
        parnt = local
        while par:
            if pm.objExists(self.guideNamer(par) + "_C0_root"):
                parnt = pm.PyNode(self.guideNamer(par) + "_C0_root")
                break
            par = par.getParent()
        return parnt
