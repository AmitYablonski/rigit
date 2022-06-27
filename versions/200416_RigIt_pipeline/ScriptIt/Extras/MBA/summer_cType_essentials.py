############ C-Type essentials - summer ################

modes = ["default", "captain_ice_cube", "summer_wizard", "detective", "sport", "pirate",
         "bellBoy", "stealthMode", "cowboy", "rock", "doctor", "hallowocka", "haunted", "the_great", "camp"]


#import Skates feet shrink blendshape
cmds.file( 'P:/MBA/assets/characters/summer/rigging/customSteps/Geometries/summer_shrunk_feet_bsp.ma' , i = True )
cmds.parent('summer_feet_shrunk_bsp','summer_bsp_grp')
cmds.select('summer_feet_shrunk_bsp', 'summer_feet_high')
cmds.blendShape(n='summer_feet_shrink_bsp')
cmds.reorderDeformers('summer_feet_high_SkinCluster', 'summer_feet_shrink_bsp', "main|high_grp|summer_feet_high")


###    ###    import cType skins    ###    ###
mSkin.importSkin(
    "\\\storage\\projects\\MBA\\assets\\characters\\summer\\rigging\\customSteps\\cType\\cType_skins.gSkin")


##################################################################
###########            summer hair offsets        ################

# update Bangs_C1_root childs rotation on modes summer_wizard, hallowocka and haunted
# lower is on cowboy and rock
# PonyTail positions:
ponyLowerTrans = (0, -5.611, -2.627)  # modes 2, 11 and 12
ponyLowerRotate = (-47.707, -0.663, -0.444)  # modes 2, 11 and 12
ponyLowTrans = (0, -5.027, -2.354)  # cowboy and rock - 8, 9
ponyLowRotate = (-42.745, -0.594, -0.398)  # cowboy and rock - 8, 9
# bangs positions:
Bangs_C0_rootRotate = (27.581, 2.07, 14.963)  # wizard - 2
Bangs_C2_rootRotate = (44.918, 0, 0)  # wizard - 2
Bangs_C1_rootRotate = (17.796, 17.076, 20.197)  # modes 2, 11 and 12 (summer_wizard, hallowocka and haunted)
Bangs_C1_rootRotateMore = (19.862, 19.058, 22.541)  # cowboy and rock - 8, 9

hairRotates = {
    "BowPonyTailMaster_C0": ["", [[2, 11, 12], ponyLowerTrans, ponyLowerRotate],
                             [[8, 9, 13], ponyLowTrans, ponyLowRotate]],
    "Bangs_C1": ["", [[2, 11, 12], "", Bangs_C1_rootRotateMore],
                 [[8, 9, 13], "", Bangs_C1_rootRotate]],
    "Bangs_C0": ["", [2, "", Bangs_C0_rootRotate]],
    "Bangs_C2": ["", [2, "", Bangs_C2_rootRotate]]

##########
for set in hairRotates:
    # create new group under the root and reparent the root's child objects to the group
    rootCtl = "faceAutoOri_C0_ctl|" + set + "_root"
    childs = pm.listRelatives(rootCtl, c=True, type="transform")
    newCtrl = pm.group(n=set + "_offset", p=rootCtl, em=True)
    for child in childs:
        pm.parent(child, newCtrl)
    transMult = []
    rotMult = []
    ### start creating the offsets for the modes
    for i in range(1, len(hairRotates[set])):
        modes = hairRotates[set][i][0]
        trans = hairRotates[set][i][1]
        rot = hairRotates[set][i][2]
        ### check if multiple modes required
        if type(modes) == int:  # only one mode
            outAttr = conNodes[modes] + ".outColorR"
        else:  # create plusMinus to collect relevant nodes when they're "On"
            plusMin = pm.shadingNode('plusMinusAverage', asUtility=True, name="plusMin_offsetModes_" + set)
            for ii in enumerate(modes):
                pm.connectAttr(conNodes[ii[1]] + ".outColorR", plusMin + ".i1%s" % [ii[0]])
            outAttr = plusMin + ".o1"
        ### if translate values list exist, create a condition node
        if trans != "":
            multNode = pm.shadingNode('multiplyDivide', asUtility=True, name="mult_trans_" + set)
            pm.setAttr(multNode + ".input1", trans)
            for i in "XYZ":
                pm.connectAttr(outAttr, multNode + ".input2" + i)
            # connect
            transMult.append(multNode)
        ### if rotate values list exist, create a condition node
        if rot != "":
            multNode = pm.shadingNode('multiplyDivide', asUtility=True, name="mult_rot_" + set)
            pm.setAttr(multNode + ".input1", rot)
            for i in "XYZ":
                pm.connectAttr(outAttr, multNode + ".input2" + i)
            # connect
            rotMult.append(multNode)
    ### connect translate - if several, add them to plusMin and then connect
    if (transMult != []):
        if (len(transMult) > 1):
            # create plus minus to add all translates
            plusMin = pm.shadingNode('plusMinusAverage', asUtility=True, name="plusMin_trans_" + set)
            for ii in enumerate(transMult):
                pm.connectAttr(ii[1] + ".o", plusMin + ".i3%s" % [ii[0]])
            pm.connectAttr(plusMin + ".o3", newCtrl + ".t")
        else:
            pm.connectAttr(transMult[0] + ".o", newCtrl + ".t")
    ### connect rotate - if several, add them to plusMin and then connect
    if (rotMult != []):
        if (len(rotMult) > 1):
            # create plus minus to add all rotates
            plusMin = pm.shadingNode('plusMinusAverage', asUtility=True, name="plusMin_rot_" + set)
            for ii in enumerate(rotMult):
                pm.connectAttr(ii[1] + ".o", plusMin + ".i3%s" % [ii[0]])
            pm.connectAttr(plusMin + ".o3", newCtrl + ".r")
        else:
            pm.connectAttr(rotMult[0] + ".o", newCtrl + ".r")