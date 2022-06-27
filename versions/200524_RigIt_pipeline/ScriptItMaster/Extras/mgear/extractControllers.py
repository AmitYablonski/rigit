import pymel.core as pm

def extractControls(*args):

    oSel = pm.selected()

    try:
        cGrp = pm.PyNode("controllers_org")
    except:
        cGrp = False
        mgear.log("Not controller group in the scene or the group is not unique", mgear.sev_error )
    for x in oSel:
        try:
            old = pm.PyNode(cGrp.name() + "|" + x.name().split("|")[-1] +"_controlBuffer")
            pm.delete(old)
        except:
            pass
        new = pm.duplicate(x)[0]
        pm.parent(new, cGrp, a=True)
        pm.rename(new, x.name() +"_controlBuffer")
        toDel = new.getChildren(type="transform")
        pm.delete(toDel)
        try:
            pm.sets( "rig_controllers_grp", remove=new )
        except:
            pass

extractControls()
