from maya import cmds, mel
import pymel.core as pm
import mgear.maya.skin as mSkin


def addCollideMesh(obj, fat):
    pm.select(obj)
    # should possibly add:
    # mel.eval('catch(`loadPlugin "C:/Program Files/Autodesk/Maya2017/bin/plug-ins/MayaMuscle.mll"`)')
    muscleMesh = pm.PyNode(mel.eval('cMuscle_makeMuscle(0)')[0])
    muscleMesh.setAttr("fat", fat)
    return muscleMesh


def addCollider(obj, xDir, yDir, zDir, name=''):
    pm.select(obj)
    keepOut, keepOutShape, driven = mel.eval('cMuscle_rigKeepOutSel()')
    pm.setAttr(keepOut + ".inDirectionX", xDir)
    pm.setAttr(keepOut + ".inDirectionY", yDir)
    pm.setAttr(keepOut + ".inDirectionZ", zDir)
    keepOut, driven = pm.PyNode(keepOut), pm.PyNode(driven)
    if name != '':
        pm.rename(keepOut, name)
        pm.rename(driven, name + '_cMuscleKeepOutDriven')
    return keepOut, driven


def flipColliderParents(obj, keepout, driven):
    objParent = obj.getParent()
    if objParent:
        pm.parent(keepout, objParent)
    else:
        pm.parent(keepout, w=True)
    pm.parent(obj, driven)


def connectKeepOut(keepOut, collideMesh):
    pm.select(keepOut, collideMesh)
    mel.eval('cMuscle_keepOutAddRemMuscle(1)')


def addParent(obj, suffix):
    objParent = obj.listRelatives(p=True)
    if objParent:
        newParent = pm.group(n=obj.name() + suffix, em=True, p=objParent[0])
    else:
        newParent = pm.group(n=obj.name() + suffix, em=True, w=True)
    pm.delete(pm.parentConstraint(obj, newParent))
    pm.parent(obj, newParent)
    return newParent


def get_mGearCtlFromNpo(ctl):
    childs = ctl.listRelatives(c=True, type="transform")
    if childs:
        for ch in childs:
            if '_cns' in ch.name():
                return ch.listRelatives(type='transform', c=True)[0]


def get_mGearChild(ctl):
    childs = ctl.listRelatives(c=True, type="transform")
    if childs:
        for ch in childs:
            baseName = ctl.rpartition('_')[0]
            print 'baseName : %s' % baseName
            number = baseName.rpartition('_fk')[2]
            print 'number : %s' % number
            ver = int(number)
            length = len(baseName)
            if ver > 9 and ver < 100:
                print "ver is between 9 and 100"
                testName = baseName[:length - 2] + str(ver + 1)
            elif ver < 10:
                print "ver is under 9"
                testName = baseName[:length - 1] + str(ver + 1)
            if testName + '_npo' == ch.name():
                return get_mGearCtlFromNpo(ch)
    else:
        return ''


def find_mGearChildren(ctl, childList):
    collideChild = get_mGearChild(ctl)
    if collideChild:
        print 'new found child : %s' % collideChild
        childList.append(collideChild)
        childList = find_mGearChildren(collideChild, childList)
        return childList
    else:
        print 'no more children found'
        return childList


def duplicate_mGearHierarchy(ctl, newParent='', ctlCopyList=[], collideObjects=[], aimPairs=[], lastSize=3):
    if newParent:
        collideParent = pm.group(n=ctl + '_collider', em=True, p=newParent)
    else:
        collideParent = pm.group(n=ctl + '_collider', em=True, w=True)
    ctlCopyList.append(collideParent.name())
    cnsGrp = addParent(collideParent, "_cns")
    pm.parentConstraint(ctl.getParent(), cnsGrp)
    targetGrp = pm.group(n=collideParent.name() + "_target", p=cnsGrp, em=True)
    collideObjects.append(targetGrp.name())
    aimGrp = pm.group(n=collideParent.name() + "_aim", p=cnsGrp, em=True)
    pm.delete(pm.pointConstraint(collideParent, aimGrp))  # <-- necessary?
    pm.parent(collideParent, aimGrp)
    # make ctrl connections
    for attr in "trs":
        ctl.attr(attr) >> collideParent.attr(attr)
    aimPairs.append([ctl.name(), aimGrp.name(), targetGrp.name()])
    # search for more children
    collideChild = get_mGearChild(ctl)
    if collideChild:
        pm.delete(pm.pointConstraint(collideChild, targetGrp))
        print 'new found child : %s' % collideChild
        ctlCopyList, collideObjects, aimPairs = duplicate_mGearHierarchy(collideChild, collideParent,
                                                                         ctlCopyList, collideObjects, aimPairs,
                                                                         targetGrp.attr('tx').get())
        return ctlCopyList, collideObjects, aimPairs
    else:
        print 'no more children found'
        targetGrp.attr("tx").set(lastSize)
        return ctlCopyList, collideObjects, aimPairs


'''
# import file
cmds.file("P:/MBA_SE02/assets/characters/fozzie/rigging/fozzie/importFiles/tie_collide_setup.ma",
          i=True, typ="mayaAscii", ignoreVersion=True, rpr="tieCollide")

mSkin.importSkin("P:\\MBA_SE02\\assets\\characters\\fozzie\\rigging\\fozzie\\gSkin\\tie_collider_skin.gSkin")
'''
setupGrp = pm.group(n="new_collide_setup", em=True, w=True)
# create tie collider
chainLen = 3
chainCount = 1  # (how many chains)
name = 'chainSpring_'
side = 'C'
# for side in "LR":
#    for i in range(0, chainCount):
#        for j in range(0, chainLen):  # todo find how many children are in the chain
#            collideParent = pm.PyNode(name + side + str(i) + "_fk" + str(j) + "_ctl_collide")
#            ctl = pm.PyNode(name + side + str(i) + "_fk" + str(j) + "_ctl")
# wasn't used: jnt = pm.PyNode("tie_" + side + str(i) + "_" + str(j) + "_jnt")
ctl = pm.PyNode("chainSpring_C0_fk0_ctl")

# childList = find_mGearChildren(ctl, [ctl])
parent1 = setupGrp
ctlCopyList, collideObjects, aimPairs = [], [], []
ctlCopyList, collideObjects, aimPairs = duplicate_mGearHierarchy(ctl, parent1)
# print 'final print childList:\n', childList
print ' // ctlCopyList: //\n', ctlCopyList
print ' // collideObjects: //\n', collideObjects
print ' // aimPairs: //\n', aimPairs


# a way to find muscle objects and change the fat attr: (if needed)
def setFat(collideMesh, fat=1.5):
    relatives = collideMesh.listRelatives()
    muscles = []
    for rel in relatives:
        if isinstance(rel, pm.nodetypes.CMuscleObject):
            muscles.append(rel)
    for mus in muscles:
        mus.setAttr("fat", fat)


# movement direction for colliders
xDir = 0
yDir = 1
zDir = 0
fat = 1  # will be assigned to collideMesh (as a muscle object)
collideMesh = pm.PyNode("collide_mesh")
addCollideMesh(collideMesh, fat)

# create colliding objects
keepOuts = {}
for obj in collideObjects:
    obj = pm.PyNode(obj)
    keepOuts[obj] = addCollider(obj, xDir, yDir, zDir, name=obj.name() + '_coll')
# TODO this following part
for i in keepOuts:
    flipColliderParents(i, keepOuts[i][0], keepOuts[i][1])  # flipColliderParents(obj, keepout, driven)
    connectKeepOut(keepOuts[i][0], collideMesh)
# Finished collider creation!


# create aim constraints
for set in aimPairs:
    # for testing: set = aimPairs[0]
    ctl, aimGrp, target = pm.PyNode(set[0]), pm.PyNode(set[1]), pm.PyNode(set[2])

    keepOut = target.getParent()
    # setup the ctrl's aim grp
    ctlCnsParent = addParent(ctl, "_coll")
    aimGrp.rz >> ctlCnsParent.rz
    # create aim constraint
    aim = 1  # todo <-- check this
    if "_R0" in aimGrp.name():
        aim *= -1
    aimCns = pm.aimConstraint(target, aimGrp, worldUpType="object", worldUpObject=aimGrp.getParent(),
                              aimVector=(aim, 0, 0), upVector=(0, 1, 0), mo=True, skip=["x", "y"])
    # create condition and connect to aimCns
    conNode = pm.shadingNode('condition', asUtility=True, name='conNode_' + aimGrp.name())
    keepOut.ty >> conNode.ft
    conNode.outColorR >> aimCns.attr(target + "W0")

# Cleanup
pm.parent("tie_collide_setup", "setup")
pm.setAttr("tie_collide_setup.v", 0)
pm.setAttr(setupGrp.v, 0)

# pm.parent(setupGrp, "tieFront_C0_ctl")
# pm.parent("tie_collide_mesh", "Fozzie_bsp_grp")
# pm.setAttr("Fozzie_bsp_grp.v", 0)
