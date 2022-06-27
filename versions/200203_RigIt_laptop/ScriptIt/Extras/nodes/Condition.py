conNode = pm.shadingNode('condition', asUtility=True, name='conNode_' + "name")
pm.connectAttr(someCtrl + ".attribute", conNode + ".ft")  # first term
someCtrl.attribute >> conNode.ft  # pymel attr connection example
conNode.setAttr("st", 1)  # 2nd term
conNode.setAttr("colorIfTrue", (1, 1, 1))
conNode.setAttr("colorIfFalse", (0, 0, 0))
outAttr = conNode + ".outColorR"
