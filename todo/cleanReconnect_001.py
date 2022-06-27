import pymel.core as pm

#clean are reconnect constraint from selected objects

sel_list = pm.ls(sl=True)
parDict = {}
for obj in sel_list:
    objName = str(obj.name())
    parents = []
    parentCns = False
    scaleCns = False
    con_list = pm.listRelatives(obj, typ='constraint')
    for con in con_list:
        plug_list = pm.listConnections(con, d=False, p=True)
        # get parList
        parList = []
        for plug in plug_list:
            plugName = plug.partition('.')[0]
            pType = pm.PyNode(plugName).type()
            print pType
            
            if 'parentConstraint' in pType:
                parentCns = True
                
            if 'scaleConstraint' in pType:
                scaleCns = True
            
            if plugName not in parList and plugName not in objName and not 'onstraint' in pType:
                parList.append(plugName)

    if objName not in parDict.keys():
        parDict[objName] = [[], parentCns, scaleCns]
        
    parDict[objName][0] = parList

print parDict

#clean vlaues
for obj in parDict:
    ctl = parDict[obj][0]
    con_list = pm.listRelatives(obj, typ='constraint')
    pm.delete(con_list)
    pm.makeIdentity(obj, a=True)
    
    #reconstraint
    if parDict[obj][1] == True:
        print parDict[obj][1]
        pm.parentConstraint(ctl, obj, mo=True)
        
    if parDict[obj][2] == True:
        print parDict[obj][2]
        pm.scaleConstraint(ctl, obj, mo=True)
    
