import maya.cmds as cmds

selComp = cmds.ls(sl=True)
newClust = cmds.cluster()
newLoc = cmds.spaceLocator(n='point_loc_0#')
locShape = cmds.listRelatives(newLoc, s=True)
# make locator pink
for locS in locShape:
    cmds.setAttr(locS+'.overrideEnabled',1)
    cmds.setAttr(locS+'.overrideColor',9)
cmds.delete( cmds.pointConstraint(newClust, newLoc) )
cmds.delete(newClust)
cmds.delete( cmds.normalConstraint(selComp,newLoc) )