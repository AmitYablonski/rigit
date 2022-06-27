import pymel.core as pm
import mgear.maya.shifter as shifter


def guideNamer(obj):
    new_name = obj.name().replace('_grp', '').title().replace('_', '').replace(' ', '')
    return new_name[0].lower() + new_name[1:]


def createGuide(obj, parnt, index, ctlShape, ctlJnt, worldOri):  # obj - the object that will
    guide = shifter.guide.Rig()
    guideName = guideNamer(obj)
    guide.drawNewComponent(parnt, 'control_01')
    root = pm.PyNode("control_C0_root")
    pm.setAttr(root.icon, ctlShape)
    pm.setAttr(root.joint, ctlJnt)
    pm.setAttr(root.neutralRotation, worldOri)
    ComponentGuide = shifter.component.guide.ComponentGuide()
    ComponentGuide.rename(root, guideName, "C", index)
    nCon = pm.parentConstraint(obj, root, mo=0)
    pm.delete(nCon)


def connectCtl(obj):
    ctl = pm.PyNode(guideNamer(obj) + "_C0_ctl")
    pm.parentConstraint(ctl, obj, mo=True)
    pm.scaleConstraint(ctl, obj, mo=True)


def createLocal():
    guide = shifter.guide.Rig()
    guide.drawNewComponent(None, 'control_01')
    root = pm.PyNode('control_C0_root')
    pm.setAttr(root.icon, "square")
    ComponentGuide = shifter.component.guide.ComponentGuide()
    ComponentGuide.rename(root, "local", "C", 0)


# catch selected objects and sort them
def sortList(objects):
    # objects = pm.ls(sl=True)
    sortedList = []
    for obj in objects:
        sortedList.append(obj.longName())
    sortedList.sort()
    objects = []
    for obj in sortedList:
        objects.append(pm.PyNode(obj))


# create guides to objects
def createGuidesFromObjects(objects, ctlJnt, worldOri, ctlShape):
    if not pm.objExists("local_C0_root"):
        createLocal()
    local = pm.PyNode("guide|local_C0_root")
    for obj in objects:
        obj = pm.PyNode(obj)
        par = obj.getParent()
        parnt = local
        while par:
            if pm.objExists(guideNamer(par) + "_C0_root"):
                parnt = pm.PyNode(guideNamer(par) + "_C0_root")
                break
            par = par.getParent()
        createGuide(obj, parnt, 0, ctlShape, ctlJnt, worldOri)


shape = 'circle'
shape = 'cube'

jnt = False
ori = False
jnt = True

objects = pm.ls(sl=True)
createGuidesFromObjects(objects, jnt, ori, shape)
