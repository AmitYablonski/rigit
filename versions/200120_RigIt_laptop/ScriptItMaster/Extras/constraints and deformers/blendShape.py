# new blend shape
bShape = pm.blendShape('bShape1', 'bShape2', 'object', n="bsp_name")[0]  # object will get the node

# Apply 80% deformation - envelope set to 0.8
pm.blendShape(bShape, edit=True, en=0.8)
bShape.setAttr("en", 1)

# Set frist target to 0.6 and 2nd bsp to 0.1
pm.blendShape(bShape, edit=True, w=[(0, 0.6), (1, 0.2)])
# or set the attr
bShape.setAttr('bShape1', .2)
bShape.setAttr('bShape2', .6)

#
# Add a target (target3) to the blendShape
pm.blendShape(bShape, edit=True, t=('object', 2, 'target3', 1.0))

# add inbetween for target3 (position 2) when weight set to 0.2
pm.blendShape(bShape, edit=True, ib=True, t=('object', 2, 'newBsp', 0.2))


# example for adding a bsp geo to an existing bsp node:
# find the first available index in bsp
def bspFreeIndex(bsp):
    targetList = pm.aliasAttr(bsp, query=True)
    targetNums = []
    for i in targetList[1::2]:
        num = i.split("[")[-1][:-1]
        targetNums.append(int(num))
    i = 0
    while (i < 200):
        if i not in targetNums:
            break
        i += 1
    return i

# add shapes to existing blend shape
bShapeName = pm.PyNode('blendShape_node')
geometry = 'geo_high'  # geo with the bsp node
bShapeGeo = 'geo_pose_blendShape'  # the bsp to add
position = bspFreeIndex(bShapeName)

# number after geometry is the position in the node (to add the new bsp)
pm.blendShape(bShapeName, edit=True, t=[geometry, position, bShapeGeo, 1.0])
bShapeName.setAttr(bShapeGeo, 1)
pm.delete(bShapeGeo)

# for use with cmds
bShapeAttr = bShapeName + '.' + bShapeGeo
cmds.setAttr(bShapeAttr, 1)
