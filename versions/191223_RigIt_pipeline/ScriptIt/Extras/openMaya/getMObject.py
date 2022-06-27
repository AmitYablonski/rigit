from maya import OpenMaya

sellist = OpenMaya.MSelectionList()
sellist.add("pCube1") #Can't initialize a list with items.
mobj = OpenMaya.MObject()
sellist.getDependNode(0, mobj) #Pass by reference
jntdepnode = OpenMaya.MFnDependencyNode(mobj) #Function sets
print jntdepnode.name()
