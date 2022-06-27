aimCns = pm.aimConstraint(obj, aimGrp, mo=True, worldUpObject=upVector,
                          aimVector=(0, -1, 0), upVector=(0, 0, 1))

aimCns = pm.aimConstraint(target, aimGrp, skip=["x", "y"], worldUpObject=upVector,
                          aimVector=(1, 0, 0), upVector=(0, 1, 0))
