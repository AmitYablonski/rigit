import pumel.core as pm
import mGear_riggingTools as rt
import mgear.maya.icon as ic

## add cns ctrl

ctls = [pm.PyNode("global_C0_ctl"), pm.PyNode("local_C0_ctl")]

gloabl = pm.PyNode('global_C0_ctl')

try:
    pm.addAttr(gloabl, ln= "ShowCnsCtrls", at="double" ,dv=0, min = 0, max = 1)
    pm.setAttr ((gloabl + ".ShowCnsCtrls"),e = 1, keyable = False, cb=1)
    pm.setAttr ((gloabl + ".ShowCnsCtrls"), 0)
except:
    print traceback.print_exc()
    print '{} has cns show attribute'.format(gloabl.name())

for c in ctls:
    oParent = c.getParent()
    icon = ic.create(oParent, c.name() + "_cns", c.getMatrix(), [1, 0, 0], 'cross')
    icon.setTransformation(c.getMatrix())
    pm.parent(c, icon)
    iconShape = icon.getShape()
    pm.connectAttr(gloabl.ShowCnsCtrls,iconShape.visibility)

    print '[add cns controller] proccessed: {}'.format(c.name())
