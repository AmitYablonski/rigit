import pymel.core as pm
from maya import cmds

def lightWrap(objToWrap, heavyMesh, deleteFaces):
    heavyMesh = pm.PyNode(heavyMesh)
    simpleGeo = pm.duplicate(heavyMesh, n=objToWrap + "_wrapper")[0]
    # delete faces
    pm.select(cl=True)
    for faces in deleteFaces:
        pm.select(heavyMesh + faces, add=True)
    pm.delete(pm.ls(sl=True))
    # find deleteComponent node to reconnect it with the new shape
    heavyMeshShp = heavyMesh.listRelatives(s=True)[0]
    deleteComponentNode = pm.listConnections(heavyMeshShp, c=True, type="deleteComponent")[0][1]
    deleteComponentNode.rename("deleteComponent_" + objToWrap)
    # reconnect heavy geo
    attrOrigin = pm.connectionInfo(deleteComponentNode + ".inputGeometry", sfd=True)
    pm.connectAttr(attrOrigin, heavyMeshShp + ".inMesh", f=True)
    pm.connectAttr(heavyMeshShp + ".worldMesh[0]", deleteComponentNode + ".inputGeometry", f=True)
    # connect deleteComponentNode to new geo and wrap it
    simpleGeoShp = simpleGeo.listRelatives(s=True)[0]
    pm.connectAttr(deleteComponentNode + ".outputGeometry", simpleGeoShp + ".inMesh", f=True)
    pm.select(objToWrap, simpleGeo)
    cmds.CreateWrap()
    newWrap = pm.listConnections(simpleGeoShp, c=True, type="wrap")[0][1]
    newWrap.rename("wrap_" + objToWrap)
    return simpleGeo

objToWrap = "partOfSphere2"
heavyMesh = "pSphere1"
deleteFaces = [u'.f[260:359]', u'.f[380:399]']
wrappedObj = lightWrap(objToWrap, heavyMesh, deleteFaces)
