from maya import cmds, mel
import pymel.core as pm


# rivets setup
def edgeToCrvLoft(edges1, edges2, name, parent1, jntAmt=0, jntPos=''):
    pm.select(edges1)
    crv1 = pm.polyToCurve(n=name + "_crv1")
    pm.select(edges2)
    crv2 = pm.polyToCurve(n=name + "_crv2")
    loftObj = pm.loft(crv1, crv2, n=name + "_loft")[0]
    pm.select(d=True)
    if jntAmt:
        jnts = []
        if jntAmt is 1:
            jnts.append(pm.joint(position=jntPos, name=name + "_JNT", rad=.01))
            pm.select(d=True)
        else:
            i = 0
            for pos in jntPos:
                jnts.append(pm.joint(position=jntPos[i], name=name + "_" + str(i) + "_JNT", rad=.01))
                pm.select(d=True)
                i += 1
    grp = pm.group([crv1, crv2, loftObj, jnts], n=name + "_setup", p=parent1)
    # create rivets
    pm.select(jnts)
    pm.select(loftObj, add=True)
    mel.eval("djRivet()")
    return loftObj, jnts, grp


# example (will work on a default pSphere named pSphere1):
edgeToCrvLoft('pSphere1.e[656]', 'pSphere1.e[655]', name="rivetName", parent1="parentTransform",
              jntAmt=1, jntPos=[.316, .653, .647])
# multiple joints example:
edge1 = ['pSphere1.e[656]', 'pSphere1.e[636]', 'pSphere1.e[616]', 'pSphere1.e[596]']
edge2 = ['pSphere1.e[655]', 'pSphere1.e[635]', 'pSphere1.e[615]', 'pSphere1.e[595]']
edgeToCrvLoft(edge1, edge2, name="rivetNames", parent1="parentTransform", jntAmt=3,
              jntPos=[[.316, .653, .647], [.385, .459, .788], [.393, .23, .875]])

