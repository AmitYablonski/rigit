import pymel.core as pm

def removeTarget(target,bsp): 
    targetList=pm.aliasAttr( bsp, query = True )
    i=0
    for tgr in targetList: 
        if (target == tgr):
            wanted_tar=targetList[i+1].split("[")[-1][:-1]
            print wanted_tar
        i+=1
    
    mel.eval('blendShapeDeleteTargetGroup '+bsp+' '+wanted_tar+';')
    

removeTarget()