otoCtls = ['OtoCtl_local_C0',
           'OtoCtl_tilt_L', 'OtoCtl_tilt_R',
           'OtoCtl_tilt_back', 'OtoCtl_tilt_front',
           'OtoCtl_body_C0',
           'OtoCtl_wheelsUI_C0']
otoCtls = pm.ls(otoCtls)

roots = []
for otoCtl in otoCtls:
    oCtl = pm.PyNode(otoCtl)
    ctl = pm.PyNode(oCtl.name().partition('OtoCtl_')[2] + '_ctl')
    root = pm.PyNode(ctl.name().replace('_ctl', '_root'))
    roots.append(root)
    # query
    trans = pm.xform(oCtl, query=True, t=True, ws=True)
    rot = pm.xform(oCtl, query=True, ro=True, ws=True)
    # set
    pm.xform(root, t=trans, ws=True)
    pm.xform(root, ro=rot, ws=True)

# set wheels center ctl to match
bodyCtl = pm.PyNode('body_C0_ctl')
body_root = pm.PyNode('body_C0_root')
wheels_C = pm.PyNode('wheels_C0_root')
val = body_root.ty.get()
wheels_C.ty.set(val)

otoWheels = ['OtoCtl_wheelB_L0', 'OtoCtl_wheelB_R0', 'OtoCtl_wheelF_L0', 'OtoCtl_wheelF_R0']
otoWheels = pm.ls('OtoWheel_*', type='transform')
multNode = pm.PyNode('md_wheels_size_and_upFix_input')
disntances = {}
for wCtl in otoWheels:
    # wCtl = otoWheels[0]
    # oCtl = pm.PyNode(otoCtl)
    ctl = pm.PyNode(wCtl.name().partition('OtoWheel_')[2] + '_ctl')
    root = pm.PyNode(ctl.name().replace('_ctl', '_root'))
    roots.append(root)
    # query
    trans = pm.xform(wCtl, query=True, t=True, ws=True)
    rot = pm.xform(wCtl, query=True, ro=True, ws=True)
    # pma = pm.PyNode('pma_' + ctl.name().replace('_ctl', '_movement'))
    distNode = pm.PyNode(ctl.name().replace('_ctl', '_0_distShape'))
    # set
    pm.xform(root, t=trans, ws=True)
    pm.xform(root, ro=rot, ws=True)
    # match distance body locs
    distNode = pm.PyNode(ctl.name().replace('_ctl', '_0_distShape'))
    dist = distNode.distance.get()
    locWheel = pm.PyNode(distNode.name().replace('_distShape', '_wheel_loc'))
    locBody = pm.PyNode(distNode.name().replace('_distShape', '_wheel_body'))
    otoLoc = pm.PyNode('OtoHightLoc_' + distNode.name().replace('_0_distShape', ''))
    # delete constraints
    pm.delete(pm.listConnections(locBody, s=True, d=False, p=False))
    # set pos
    pm.delete(pm.parentConstraint(otoLoc, locBody))
    # make constraints
    pm.parentConstraint(bodyCtl, locBody, mo=True)
    pm.scaleConstraint(bodyCtl, locBody, mo=True)
    # set wheel new hight
    dist = distNode.distance.get()
    disntances[ctl] = [distNode, dist]
    multNode.input1X.set(dist)

# todo !!!!!!!!!!!!!!!!!!! rename other pma / md / distance nodes !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# todo !!!!!!!!! saparate the mult node that recieves the distance for each wheel (md_wheels_size_and_upFix_input)
# - for now, everything must be the same hight to work well
# todo ! make wheels match floor hight
# todo - OtoCtls for lattive deformer
# todo ? hide wheels_C0_0_jnt ?

pm.setAttr('OtoRig_main.v', 1)
pm.setAttr('OtoCtl_local_C0.v', 0)
pm.setAttr('OtoRig_rig.jnt_vis', 1)
# pm.setAttr('OtoRig_rig.jnt_vis', 0)
