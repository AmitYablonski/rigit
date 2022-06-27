multNode = pm.shadingNode('multiplyDivide', asUtility=True, name="multNode_" + name)
multNode.setAttr("op", 2) #  set operation to divide
# inputs
# "input1" = "i1"
pm.connectAttr(obj + ".attribute", multNode + ".input1")
# "input1X" = "i1x"
obj.attributeY >> multNode.i2y  # connectAttr the pymel way
multNode.setAttr("input2", [1, 2, 3])
# outputs
multNode.ox >> obj.attributeX
multNode.o >> obj.attribute