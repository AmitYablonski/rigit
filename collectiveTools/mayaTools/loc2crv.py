import pymel.core as pm
import maya.cmds as mc
from functools import partial

def ui ():
    if pm.window('loc2crvTool', exists = True):
        pm.deleteUI('loc2crvTool')
    myWin = pm.window('loc2crvTool', t='loc2crv_Tool', mb=True, tlb=True, s=False)
    topLay = pm.columnLayout(adj=True)
    
    #row 0 - top text
    pm.separator(vis=False, h=2)
    pm.text(l='create a chain of locs on a curve')
    pm.separator(st='none', h=2)
    
    mainLay = pm.rowColumnLayout(nc=2, cat=[(1,'right', 2),(2,'left', 2)], rs=[(1,2),(2,2)])
    
    #row 1 -  add
    buttonTemp = pm.button(l='add', w=50)
    textF = pm.textField('tFld_sel', w=130)
    pm.button(buttonTemp, e=True, c=partial(selCrv, textF))
    
    #row 2 - amnout
    pm.text(l='Amount :')
    intF = pm.intField('tFld_sel', w=130)
    
    #row 3 - name
    pm.text(l='Name :')
    nameF = pm.textField('nFld', tx='point',w=130)
    
    pm.separator(st='none', h=5, p=topLay)
    
    #row 4 - end
    pm.button(l='execute', c=partial(execute, textF, intF, nameF), p=topLay)
    
    
    
    pm.showWindow('loc2crvTool')

def selCrv(textF, *args):
    sel = pm.ls(sl=True)
    add = pm.textField(textF, edit=True, tx=sel[0])
    
def execute(textF, intF, nameF, *args):
    
    name = pm.textField(nameF, query=True, tx=True)
    sourceCrv = pm.textField(textF, query=True, tx=True)
    num_input = pm.intField(intF, q=True, v=True)
    
    print '\n'
    print ' >> ' + 'selected curve : ', sourceCrv
    print ' >> ' + 'amount of locs : ', num_input
    print ' >> ' + 'locs name : ', name
    
    spans = pm.getAttr(sourceCrv+'.spans')
    loc_list = []
    
    #rebuild curve
    pm.rebuildCurve(sourceCrv, ch=True, rpo=False, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=spans, d=3, tol=0.01, n=sourceCrv+'_rd')
    crv = sourceCrv+'_rd'
    print '\n curve rebuild : done'
    
    print '\n [step 01 - create locs]'
    for i in range(num_input):
        loc = pm.spaceLocator(n=name+'_'+str(i))
        loc_list.append(loc)
        print '\n', loc, '- created'
        mp = pm.pathAnimation(loc, c=crv, n='mPath_'+str(i))
        mp_cons = pm.listConnections(mp)
    
        step = 1.0/(num_input-1)
        place = 0.0
        if not i == 0.0:
            place = step*i
        
        print 'place : ', place
     
        for con in mp_cons:
            if 'uValue' in str(con):
                pm.disconnectAttr(con)
                print "uValue - disconnected "
                break
    
        pm.setAttr(mp+'.uValue', place)
    
    pm.delete(crv)
    par = pm.group(n=sourceCrv+'_locs_grp', em=True)
    print '\n [step 02 - aim constraint]'
    for i in range(len(loc_list)):
        pm.setAttr(loc_list[i]+'Shape.overrideEnabled', 1)
        pm.setAttr(loc_list[i]+'Shape.overrideColor', 16)
        pm.parent(loc_list[i], par)
        if i == (len(loc_list))-1:
            pm.delete(pm.orientConstraint(loc_list[i-1], loc_list[i]))
        else:
            pm.delete(pm.aimConstraint(loc_list[i+1], loc_list[i]))
        
        print loc_list[i], ' : done'
    
    
    pm.select(par)
    print "\n [PROCESS - COMPLETED]"

ui()











