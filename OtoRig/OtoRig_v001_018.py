
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
    otoLocFix = pm.PyNode('OtoHightLoc_' + distNode.name().replace('_0_distShape', '') + '_fix')
    # delete constraints
    pm.delete(pm.listConnections(locWheel, s=True, d=False, p=False))
    pm.delete(pm.listConnections(locBody, s=True, d=False, p=False))
    # set pos
    pm.delete(pm.parentConstraint(otoLocFix, locWheel))
    pm.delete(pm.parentConstraint(otoLoc, locBody))
    # make constraints
    pm.parentConstraint(bodyCtl, locBody, mo=True)
    pm.scaleConstraint(bodyCtl, locBody, mo=True)
    pm.parentConstraint(root, locWheel, mo=True)
    pm.scaleConstraint(root, locWheel, mo=True)
    # set wheel new hight
    dist = distNode.distance.get()
    disntances[ctl] = [distNode, dist]
    multNode.input1X.set(round(dist, 3))

# set shapes
def reparentShapes(ctl, shpCtl):
    origShps = pm.listRelatives(ctl, s=True)
    dup = pm.duplicate(otoCtl)[0]
    dupShps = pm.listRelatives(dup, s=True)
    pm.parent(dup, ctl)
    pm.select(dup)
    mel.eval('makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;')
    for shp in dupShps:
        pm.select(shp, ctl)
        mel.eval('parent -r -s')
    pm.delete(origShps, dup)

for ctl, otoCtl in [['body_C0_ctl', 'OtoCtl_body_C0'],
                    ['wheelsUI_C0_ctl', 'OtoCtl_wheelsUI_C0']]:
    reparentShapes(ctl, otoCtl)


# todo check naming of pma / md / distance nodes
# - for now, everything must be the same hight to work well, to change it:
# todo ! saparate the mult node that recieves the distance for each wheel (md_wheels_size_and_upFix_input)
# todo ! make wheels match floor hight
# todo - OtoCtls for lattive deformer
# todo ? hide wheels_C0_0_jnt ?


pm.setAttr('OtoRig_main.v', 1)
pm.setAttr('OtoCtl_local_C0.v', 0)
pm.setAttr('OtoRig_rig.jnt_vis', 1)
# pm.setAttr('OtoRig_rig.jnt_vis', 0)
'''
for i in range(1, 15):
    ver = str(format(i, '0' + str(2)))
    cns = pm.PyNode('seatbelt_B_00 ' + ver + ':global_C0_ctl_cns')
    pm.parentConstraint('body_C0_ctl', cns, mo=True)
    pm.scaleConstraint('body_C0_ctl', cns, mo=True)


# select original top cluster group and new cluster (for wheel squash)
orig, clust = pm.selected()
par = clust.getParent()
npo = pm.group(n=orig.name() + '_npo', em=True, p=par)
pm.delete(pm.parentConstraint(orig, npo))
pm.select(npo)
mel.eval('makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1;')
pm.parent(orig, npo)
pm.delete(pm.parentConstraint(clust, npo))
oldClust = pm.listRelatives(orig, ad=True, type='clusterHandle')[0].getParent()
clustPar = oldClust.getParent()
name = str(oldClust.name())
pm.delete(oldClust)
pm.parent(clust, clustPar)
clust.rename(name)

'''
