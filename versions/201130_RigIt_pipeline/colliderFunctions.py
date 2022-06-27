import pymel.core as pm
from maya import mel, cmds


def addCollideMesh(obj, fat):
    if isinstance(obj, (list, tuple)):
        muscleMeshes = []
        for o in obj:
            newMus = addMuscle(o, fat)
            if newMus:
                muscleMeshes.append(newMus)
        return muscleMeshes
    else:
        return addMuscle(obj, fat)


# todo should possibly add following line:
# mel.eval('catch(`loadPlugin "C:/Program Files/Autodesk/Maya2017/bin/plug-ins/MayaMuscle.mll"`)')
def addMuscle(obj, fat):
    # check if object is already a muscle object
    relatives = obj.listRelatives()
    for rel in relatives:
        if isinstance(rel, pm.nodetypes.CMuscleObject):
            print(' /#/ Collider --> %s already connected' % obj.name())
            return ''
    pm.select(obj)
    muscleMesh = pm.PyNode(mel.eval('cMuscle_makeMuscle(0)')[0])
    muscleMesh.setAttr('fat', fat)
    return muscleMesh


def addCollider(obj, xDir, yDir, zDir, name=''):
    pm.select(obj)
    tempList = mel.eval('cMuscle_rigKeepOutSel()')
    if tempList:
        keepOut, keepOutShape, driven = tempList
    else:
        pm.select(obj)
        print ' /*/ tempList is empty - check if the collider was made - LAST SELECTED: %s' % obj
    pm.setAttr(keepOut + '.inDirectionX', xDir)
    pm.setAttr(keepOut + '.inDirectionY', yDir)
    pm.setAttr(keepOut + '.inDirectionZ', zDir)
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


def is_mGearParent(ctl, name):
    ctlParent = ctl.getParent()
    if not ctlParent:
        return False
    if ctlParent.name() == name:
        return True
    else:
        return self.is_mGearParent(ctlParent, name)


def find_mGearChainParent(ctl):
    ctlParent = ctl.getParent()
    if not ctlParent:
        return ctl
    baseName = ctl.rpartition('_ctl')[0]
    number = baseName.rpartition('_fk')[2]
    ver = int(number)
    if ver == 0:
        return ctl
    name = baseName.rpartition(number)[0]
    testName = name + '0_ctl'
    if pm.objExists(testName):
        if is_mGearParent(ctl, testName):
            return pm.PyNode(testName)
    else:
        testName = name + str(ver - 1) + '_ctl'
        if pm.objExists(testName):
            if is_mGearParent(ctl, testName):
                if ver - 1 == 0:
                    return pm.PyNode(testName)
                return find_mGearChainParent(pm.PyNode(testName), name)
        else:
            print " // SpringsCollider.find_mGearChainParent() wasn't really expecting to get here..\n" \
                  " // returning the following ctl %s" \
                  " // line 291 in SpringsCollider.py" % ctl
            return pm.PyNode(ctl)


def get_mGearChild(ctl):
    childs = ctl.listRelatives(c=True, type='transform')
    if childs:
        for ch in childs:
            baseName = ctl.rpartition('_')[0]
            print 'baseName : %s' % baseName
            number = baseName.rpartition('_fk')[2]
            print 'number : %s' % number
            ver = int(number)
            length = len(baseName)
            if ver > 9 and ver < 100:
                print 'ver is between 9 and 100'
                testName = baseName[:length - 2] + str(ver + 1)
            elif ver < 10:
                print 'ver is under 9'
                testName = baseName[:length - 1] + str(ver + 1)
            if testName + '_npo' == ch.name():
                return get_mGearCtlFromNpo(ch)
    else:
        return ''


def get_mGearCtlFromNpo(ctl):
    childs = ctl.listRelatives(c=True, type='transform')
    if childs:
        for ch in childs:
            if '_cns' in ch.name():
                return ch.listRelatives(type='transform', c=True)[0]


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


def duplicate_mGearHierarchy(ctl, newParent='', ctlCopyList=[], collideObjects=[], aimPairs=[], lastSize=3,
                             offsetLocs=False):
    print '/*//*/ doing duplicate_mGearHierarchy with %s' % ctl
    print 'ctl = %s\nnewParent = %s\nctlCopyList = %s\ncollideObjects = %s\naimPairs = %s\nlastSize = %s' % \
          (ctl, newParent, ctlCopyList, collideObjects, aimPairs, lastSize)
    if newParent:
        collideParent = pm.group(n=ctl + '_collider', em=True, p=newParent)
    else:
        collideParent = pm.group(n=ctl + '_collider', em=True, w=True)
    ctlCopyList.append(collideParent.name())
    cnsGrp = addParent(collideParent, '_cns')
    pm.parentConstraint(ctl.getParent(), cnsGrp)
    targetGrp = pm.group(n=collideParent.name() + '_target', p=cnsGrp, em=True)
    collideObjects.append(targetGrp.name())
    aimGrp = pm.group(n=collideParent.name() + '_aim', p=cnsGrp, em=True)
    pm.delete(pm.pointConstraint(collideParent, aimGrp))  # <-- necessary?
    pm.parent(collideParent, aimGrp)
    # make ctrl connections
    for attr in 'trs':
        ctl.attr(attr) >> collideParent.attr(attr)
    aimPairs.append([ctl.name(), aimGrp.name(), targetGrp.name()])
    # search for more children
    collideChild = get_mGearChild(ctl)
    if collideChild:
        if offsetLocs:
            setOffsetForCollider(ctl, targetGrp)
        else:
            pm.delete(pm.pointConstraint(collideChild, targetGrp))
        print 'new found child : %s' % collideChild
        ctlCopyList, collideObjects, aimPairs = duplicate_mGearHierarchy(collideChild, collideParent,
                                                                         ctlCopyList, collideObjects, aimPairs,
                                                                         targetGrp.attr('tx').get())
        return ctlCopyList, collideObjects, aimPairs
    else:
        print 'no more children found'
        if offsetLocs:
            setOffsetForCollider(ctl, targetGrp)
            return
        else:
            targetGrp.attr('tx').set(lastSize)
        return ctlCopyList, collideObjects, aimPairs


def setOffsetForCollider(ctl, targetGrp):
    # find the associated locator
    baseName = ctl.rpartition('_')[0]
    print 'baseName : %s' % baseName
    number = baseName.rpartition('_fk')[2]
    print 'number : %s' % number
    ver = int(number)
    length = len(baseName)
    if ver > 9 and ver < 100:
        print 'ver is between 9 and 100'
        testName = baseName[:length - 2] + str(ver + 1)
    elif ver < 10:
        print 'ver is under 9'
        testName = baseName[:length - 1] + str(ver + 1)


def createSpringColliderSetup(collideObject, collideMesh, offsetDict, fat=0.1,
                              setupGrpName='new_collide_setup', updateTargets=False,
                              xDirection=0.0, yDirection=0.0, zDirection=1.0,
                              flipForR_X=False, flipForR_Y=False, flipForR_Z=False):
    setupGrp = pm.group(n=setupGrpName, em=True, w=True)  # don't forget to parent this group

    # make colliderMesh object a muscle object (multiple meshes work well)
    addCollideMesh(collideMesh, fat)

    doneCtls = []
    allKeepOuts = []
    # create the new hierarchy
    for ctl in collideObject:
        print "\n /****/ start of new spring chain collider setup for - %s" % ctl
        ctlCopyList, collideObjects, aimPairs = duplicate_mGearHierarchy(ctl, setupGrp, [], [], [])
        print '\n // ctlCopyList: //'
        print ctlCopyList
        print ' // collideObjects: //'
        print collideObjects
        print ' // aimPairs: //'
        for pair in aimPairs:
            print pair
        # create colliding objects
        keepOuts = {}
        for obj in collideObjects:
            obj = pm.PyNode(obj)
            locCtl = ''
            if updateTargets:  # setting up the offset
                locCtl = obj.name().rpartition('_collider_target')[0]
                trans, rot = offsetDict[locCtl]
                print 'Repositioning obj "%s" according to offsetDict' % (obj)
                obj.attr('t').set(trans)
                obj.attr('r').set(rot)
            if not obj.name() in doneCtls:
                print '// adding %s as a collider (keepOut stage)' % obj
                xDir = xDirection
                yDir = yDirection
                zDir = zDirection
                if '_R' in obj.name():
                    if flipForR_X:
                        print 'flipping collider x direction for %s' % obj
                        xDir *= -1
                    if flipForR_Y:
                        print 'flipping collider y direction for %s' % obj
                        yDir *= -1
                    if flipForR_Z:
                        print 'flipping collider z direction for %s' % obj
                        zDir *= -1
                keepOuts[obj] = addCollider(obj, xDir, yDir, zDir, name=obj.name() + '_coll')
                allKeepOuts.append([obj, keepOuts[obj][0]])
                doneCtls.append(obj.name())
        print '/**/ finished adding colliders (keepout creation stage)\n'

        for i in keepOuts:
            flipColliderParents(i, keepOuts[i][0], keepOuts[i][1])  # flipColliderParents(obj, keepout, driven)
            print 'flipped parents for %s' % keepOuts[i][0]
            if isinstance(collideMesh, list) or isinstance(collideMesh, tuple):
                for mesh in collideMesh:
                    connectKeepOut(keepOuts[i][0], mesh)
            else:
                connectKeepOut(keepOuts[i][0], collideMesh)
        # Finished collider creation!

        # create aim constraints
        for pairCtl, aimGrp, target in aimPairs:
            pairCtl = pm.PyNode(pairCtl)
            aimGrp = pm.PyNode(aimGrp)
            target = pm.PyNode(target)
            keepOut = target.getParent()
            # setup the ctrl's aim grp
            ctlCnsParent = addParent(pairCtl, '_coll')
            aimGrp.rz >> ctlCnsParent.rz
            # create aim constraint
            # todo test that the aim contraint works well for right side.
            aim = 1
            if '_R' in aimGrp.name():
                aim *= -1
            aimCns = pm.aimConstraint(target, aimGrp, worldUpType='object', worldUpObject=aimGrp.getParent(),
                                      aimVector=(aim, 0, 0), upVector=(0, 1, 0), mo=True, skip=['x', 'y'])
            # create condition and connect to aimCns
            conNode = pm.shadingNode('condition', asUtility=True, name='conNode_' + aimGrp.name())
            keepOut.ty >> conNode.ft
            conNode.outColorR >> aimCns.attr(target + 'W0')
        ctlCopyList, collideObjects, aimPairs = [], [], []
        print "\n /****/ end of new spring chain collider setup for - %s" % ctl

    return setupGrp


def createSpringColliderSetupY(collideObject, collideMesh, offsetDict, fat=0.1,
                              setupGrpName='new_collide_setup', updateTargets=False,
                              xDirection=0.0, yDirection=0.0, zDirection=1.0,
                              flipForR_X=False, flipForR_Y=False, flipForR_Z=False):
    setupGrp = pm.group(n=setupGrpName, em=True, w=True)  # don't forget to parent this group

    # make colliderMesh object a muscle object (multiple meshes work well)
    addCollideMesh(collideMesh, fat)

    doneCtls = []
    allKeepOuts = []
    # create the new hierarchy
    for ctl in collideObject:
        print "\n /****/ start of new spring chain collider setup for - %s" % ctl
        ctlCopyList, collideObjects, aimPairs = duplicate_mGearHierarchy(ctl, setupGrp, [], [], [])
        print '\n // ctlCopyList: //'
        print ctlCopyList
        print ' // collideObjects: //'
        print collideObjects
        print ' // aimPairs: //'
        for pair in aimPairs:
            print pair
        # create colliding objects
        keepOuts = {}
        for obj in collideObjects:
            obj = pm.PyNode(obj)
            locCtl = ''
            if updateTargets:  # setting up the offset
                locCtl = obj.name().rpartition('_collider_target')[0]
                trans, rot = offsetDict[locCtl]
                print 'Repositioning obj "%s" according to offsetDict' % (obj)
                obj.attr('t').set(trans)
                obj.attr('r').set(rot)
            if not obj.name() in doneCtls:
                print '// adding %s as a collider (keepOut stage)' % obj
                xDir = xDirection
                yDir = yDirection
                zDir = zDirection
                if '_R' in obj.name():
                    if flipForR_X:
                        print 'flipping collider x direction for %s' % obj
                        xDir *= -1
                    if flipForR_Y:
                        print 'flipping collider y direction for %s' % obj
                        yDir *= -1
                    if flipForR_Z:
                        print 'flipping collider z direction for %s' % obj
                        zDir *= -1
                keepOuts[obj] = addCollider(obj, xDir, yDir, zDir, name=obj.name() + '_coll')
                allKeepOuts.append([obj, keepOuts[obj][0]])
                doneCtls.append(obj.name())
        print '/**/ finished adding colliders (keepout creation stage)\n'

        for i in keepOuts:
            flipColliderParents(i, keepOuts[i][0], keepOuts[i][1])  # flipColliderParents(obj, keepout, driven)
            print 'flipped parents for %s' % keepOuts[i][0]
            if isinstance(collideMesh, list) or isinstance(collideMesh, tuple):
                for mesh in collideMesh:
                    connectKeepOut(keepOuts[i][0], mesh)
            else:
                connectKeepOut(keepOuts[i][0], collideMesh)
        # Finished collider creation!

        # create aim constraints
        for pairCtl, aimGrp, target in aimPairs:
            pairCtl = pm.PyNode(pairCtl)
            aimGrp = pm.PyNode(aimGrp)
            target = pm.PyNode(target)
            keepOut = target.getParent()
            # setup the ctrl's aim grp
            ctlCnsParent = addParent(pairCtl, '_coll')
            aimGrp.ry >> ctlCnsParent.ry
            # create aim constraint
            # todo test that the aim contraint works well for right side.
            aim = 1
            if '_R' in aimGrp.name():
                aim *= -1
            aimCns = pm.aimConstraint(target, aimGrp, worldUpType='object', worldUpObject=aimGrp.getParent(),
                                      aimVector=(aim, 0, 0), upVector=(0, 0, 1), mo=True, skip=['x', 'z'])
            # create condition and connect to aimCns
            conNode = pm.shadingNode('condition', asUtility=True, name='conNode_' + aimGrp.name())
            keepOut.tz >> conNode.ft
            conNode.op.set(5)
            conNode.outColorR >> aimCns.attr(target + 'W0')
        ctlCopyList, collideObjects, aimPairs = [], [], []
        print "\n /****/ end of new spring chain collider setup for - %s" % ctl

    return setupGrp
