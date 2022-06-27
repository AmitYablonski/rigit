import pymel.core as pm
import mgear.maya.rigbits.rivet as mgRivet

parent1 = pm.PyNode("rivetsParentObj")
mesh = pm.PyNode("meshToFollow")
name = "rivet_name"
# the edges indexes
edge1 = 9600
edge2 = 9674
newRivet = mgRivet.rivet().create(mesh, edge1, edge2, parent=parent1, name=name)
