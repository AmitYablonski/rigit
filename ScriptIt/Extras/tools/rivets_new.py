from maya import cmds, mel
import pymel.core as pm


# rivets setup
def edgeToCrvLoft(edges1, edges2, rivObjs, name, parent1, noRot=False):
    renameRiv = True
    if pm.objExists('djRivetX'):
        renameRiv = False
    # create loft object
    pm.select(edges1)
    crv1 = pm.polyToCurve(n=name + "_crv1")
    pm.select(edges2)
    crv2 = pm.polyToCurve(n=name + "_crv2")
    loftObj = pm.loft(crv1, crv2, n=name + "_loft")[0]
    pm.select(d=True)
    # group rivet setup
    grp = pm.group([crv1, crv2, loftObj], n=name + "_setup", p=parent1)
    # create rivets
    pm.select(rivObjs)
    pm.select(loftObj, add=True)
    mel.eval("djRivet()")
    # disconnect attrs
    if noRot:
        for obj in rivObjs:
            for ax in 'xyz':
                pm.disconnectAttr(obj.attr('r' + ax))
    # rename rivets
    if renameRiv:
        if pm.objExists('djRivetX'):
            djRivet = pm.PyNode('djRivetX')
            djRivet.rename(name + '_djRivetX')
            pm.parent(djRivet, grp)
    return loftObj, grp


edges1 = ['mesh.e[0:10]']
edges2 = ['mesh.e[10:20]']
rivObjs = ['obj1', 'obj2', 'obj3']  # must be a list
name = "nameRivet"
parent1 = 'setup_grp'
loftObj, rivGrp = edgeToCrvLoft(edges1, edges2, rivObjs, name, parent1, noRot=True)
