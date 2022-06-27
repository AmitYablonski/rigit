import pymel.core as pm


globalAttr = "local_C0_ctl.GlobalSpringVolume"
uiCtl = 'hatUI_C0_ctl'
axis = {0: 'x', 1: 'y', 2: 'z'}
for attr in ['feather_C0_spring_intensity', 'hatFlap_L0_spring_intensity']:
    conn = pm.listConnections(uiCtl + '.' + attr, c=True, p=True)
    i = 0
    for springAttr, springMult in conn:
        if not i:
            multNode = pm.shadingNode('multiplyDivide', asUtility=True, name='multNode_' + attr)
            for ax in 'xyz':
                pm.connectAttr(globalAttr, multNode.attr('i1' + ax))
                pm.connectAttr(springAttr, multNode.attr('i2' + ax))
        multNode.attr('o' + axis[i]) >> springMult
        if i > 1:
            i = 0
        else:
            i += 1
