def distanceCreateConnect(object1, object2, objectAttr): # name
    distNode = pm.shadingNode("distanceBetween", asUtility=True) #, n="dist_" + name
    object1.worldMatrix >> distNode.inMatrix1
    object2.worldMatrix >> distNode.inMatrix2
    pm.connectAttr(distNode.distance, objectAttr)
    return (distNode)

# create dinstanceNode between 2 object and connect the distance to a multiply divide
obj1 = pm.PyNode("nurbsCircle1")
obj2 = pm.PyNode("nurbsCircle2")
objectAttr = pm.PyNode("multiplyDivide1").i1x  # input1X
distanceCreateConnect(obj1, obj2, objectAttr)

# can be called in one line
distanceCreateConnect(pm.PyNode("obj1"), pm.PyNode("obj2"), "multiplyDivide1.i1x")