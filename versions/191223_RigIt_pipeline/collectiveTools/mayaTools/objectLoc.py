import maya.cmds as cmds

objList = cmds.ls(sl=True)
print "|| "+str(len(objList))+" objects in the list:"
for obj in objList:
    dup = cmds.duplicate(obj)
    cmds.xform(dup, cp=True)
    newLocator = cmds.spaceLocator(n=obj+'_loc')
    locShape = cmds.listRelatives(newLocator, s=True)
    cmds.delete(cmds.parentConstraint(dup, newLocator))
    cmds.delete(dup)
    for locS in locShape:
        cmds.setAttr(locS+'.overrideEnabled',1)
        cmds.setAttr(locS+'.overrideColor',16)
    print newLocator
print '|| oLoc is done ||'