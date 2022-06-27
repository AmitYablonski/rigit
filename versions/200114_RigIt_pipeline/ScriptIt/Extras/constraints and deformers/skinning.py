
# get skinCluster
shape1 = "objShape"
skinClusters = []
try:
    skinClust = pm.listConnections(shape1, type="skinCluster")[0]
    skinClusters.append(skinClust)
except:
    try:
        skinClustGrp = pm.listConnections(shape1, type="groupId")
        for skin in skinClustGrp:
            if "SkinCluster" in str(skin) or "skinCluster" in str(skin):
                skinClust = pm.listConnections(skin, type="skinCluster")[0]
                skinClusters.append(skinClust)



# copy weights - "ss" is source, "ds" is destination
pm.copySkinWeights(ss=skin1, ds=skin2, sa="closestPoint", ia="oneToOne", noMirror=True)


# query the influences associated to the skin
skinInflu = pm.skinCluster("skin", query=True, inf=True)


# skin an object
pm.select("obj3")
for jnt in skinInflu:
    pm.select(jnt, add=True)
pm.skinCluster(toSelectedBones=True)
