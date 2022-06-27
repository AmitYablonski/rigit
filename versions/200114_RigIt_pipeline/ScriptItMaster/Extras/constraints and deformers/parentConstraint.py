parent1 = "parentObj1"
parent2 = "parentObj2"
obj = "objName"
# single parent
parCns2 = pm.parentConstraint(parent1, obj, mo=True)

# multiple parents
parCns = pm.parentConstraint(parent1, parent2, obj, mo=True)
parCns.setAttr("interpType", 2)  # setting it to shortest reduces flips for multiple parents
parCns.setAttr(parent1 + "W0", .8)
parCns.setAttr(shoulder + "W1", .2)

# example for deleting a par cns (to snap to position)
pm.delete(pm.parentConstraint(obj1, obj2))

# example for parenting multiple controllers and assigning values
parAmt = {"0": 0.25, "1": 0.50, "2": 0.75}
for i in parAmt:
    ctl = "name_" + i + "_ctl_grp"
    parCns = pm.parentConstraint(parent1, parent2, ctl, mo=True)
    parCns.setAttr("interpType", 2)
    parCns.setAttr(parent1 + "W0", 1 - parAmt[i])
    parCns.setAttr(parent2 + "W1", parAmt[i])