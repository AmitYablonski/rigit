import pymel.core as pm

#find out the first available index in bsp  
def bspFreeIndex(bsp):
    targetList=pm.aliasAttr( bsp, query = True )
    
    targetNums=[]
    
    for i in targetList[1::2]: 
        num=i.split("[")[-1][:-1]
        targetNums.append(int(num))
    i=0
    while (i<200):
        if i not in targetNums:
            break
        i+=1
    return i

