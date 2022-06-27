choiceNode = pm.shadingNode('choice', asUtility=True, name='choice_' + name)

# inputs:
grp = pm.group(em=True)  # for the example
obj.attribute >> choiceNode.selector  # i = input
pm.connectAttr(obj.attribute, choiceNode + ".selector")

choiceNode + ".input[0]"

choiceNode + ".output"