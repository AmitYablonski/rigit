reverse = pm.shadingNode('reverse', asUtility=True, name="revNode_" + name)

# inputs:
grp = pm.group(em=True)  # for the example
grp.t >> reverse.i  # i = input
pm.connectAttr(grp + ".t", reverse + ".i")  # connecting translate to ".input"
pm.connectAttr(grp + ".tx", reverse + ".ix")  # connecting translate to ".inputX"

# outputs:
reverse.o >> grp.r  # connect ".output" to rotate
reverse.ox >> grp.sx  # connect ".outputX" to scaleX
pm.connectAttr(reverse + ".o", grp + ".t")  # connect ".output" to translate
pm.connectAttr(reverse + ".ox", grp + ".tx")  # connect ".outputX" to translateX
