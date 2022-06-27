from maya import cmds, mel
import pymel.core as pm


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
    return (keepOut, driven)


def flipColliderParents(obj, keepout, driven):
    try:
        objParent = pm.listRelatives(obj, p=True)[0]
    except:
        objParent = ''
    if objParent:
        pm.parent(keepout, objParent)
        pm.parent(obj, driven)
    else:
        pm.parent(keepout, w=True)
        pm.parent(obj, driven)


def connectKeepOut(keepOut, collideMesh):
    pm.select(keepOut, collideMesh)
    mel.eval('cMuscle_keepOutAddRemMuscle(1)')


collideMesh = pm.PyNode("pSphere1")  # can be a list of objects
collideObject = pm.PyNode("pCube1")  # can be a list of objects
xDir = 0  # movement direction for colliders
yDir = -1
zDir = 0
fat = 0.2  # will be assigned to meshCollider (as muscle object)

# add colliders (make muscles)
if isinstance(collideMesh, (list, tuple)):  # if more that one collider
    for obj in collideMesh:
        # check if object is already a muscle object
        relatives = obj.listRelatives()
        for rel in relatives:
            if isinstance(rel, pm.nodetypes.CMuscleObject):
                print("Collider --> %s already connected" % obj.name())
            else:
                addCollideMesh(obj, fat)
else:  # if one collider
    if isinstance(collideMesh, pm.nodetypes.CMuscleObject):
        print("Collider --> %s already connected" % collideMesh.name())
    else:
        addCollideMesh(collideMesh, fat)

# create colliding objects
keepOuts = {}
if isinstance(collideObject, (list, tuple)):  # if more that one collider
    for obj in collideObject:
        keepOuts[obj] = addCollider(obj, xDir, yDir, zDir, name=obj.name() + '_coll')
else:  # if one collider
    obj = collideObject
    keepOuts[obj.name()] = addCollider(obj, xDir, yDir, zDir, name=obj.name() + '_coll')
for i in keepOuts:
    flipColliderParents(i, keepOuts[i][0], keepOuts[i][1])  # flipColliderParents(obj, keepout, driven)-
    if isinstance(collideObject, (list, tuple)):  # if more that one collider
        for colMesh in collideMesh:
            connectKeepOut(keepOuts[i][0], colMesh)
    else:  # if one collider
        connectKeepOut(keepOuts[i][0], collideMesh)
# Finished creation!


# relevant attrs for muscle objects:
# keep out attribute example
keepOut.setAttr("inDirection", [0, -1, 0])
keepOut.setAttr("inDirectionX", 1)

# a way to find muscle objects and change the fat attr:
relatives = collideMesh.listRelatives()
muscles = []
for rel in relatives:
    if isinstance(rel, pm.nodetypes.CMuscleObject):
        muscles.append(rel)
for mus in muscles:
    mus.setAttr("fat", fat)
