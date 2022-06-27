# taken from: https://www.ngskintools.com/documentation/api/mll-interface.html

# basic example for mllInterface usage
from ngSkinTools.mllInterface import MllInterface

mll = MllInterface()
mll.setCurrentMesh('pCylinder1')  # Use None to operate on current selection instead.

if not mll.getLayersAvailable():  # returns True if layers available
    mll.initLayers()
    layerId = mll.createLayer('first layer')
else:
    layerId = 1  # first layer

# list influences idx and name
influList_idx = mll.listInfluenceIndexes()
influList_name = mll.listInfluencePaths()
for idx, jntName in zip(influList_idx, influList_name):
    print(idx, jntName)

allLayers = mll.listLayers()  # returns iterator to layer list of tuples: (layer ID, layer name)
for layId, name, arg in allLayers:
    print('layerID=%s, name="%s", arg=%s' % (layId, name, arg))

vtxCount = mll.getVertCount()

jnt_0 = 0  # first influence in skin
jnt_1 = 1  # 2nd influence in skin

# example for setting weights
weights_0 = []
weights_1 = []
for i in range(0, vtxCount):
    weights_0.append(.1)
    weights_1.append(.9)

mll.setInfluenceWeights(layerId, jnt_0, weights_0)  # available flag:, undoEnabled=True)
mll.setInfluenceWeights(layerId, jnt_1, weights_1)

# get weights
weights = mll.getInfluenceWeights(layerId, jnt_0)

# add layers and setup some hierarchy
weights = []
for i in range(0, vtxCount):
    weights.append(1)
mll.setInfluenceWeights(layerId, jnt_0, weights)  # available flag:, undoEnabled=True)

# 2nd layer
layerId_2 = mll.createLayer('second layer')
weights = []
for i in range(0, vtxCount):
    weights.append(1)
mll.setInfluenceWeights(layerId_2, jnt_1, weights)  # available flag:, undoEnabled=True)


# get/set layer name
name = mll.getLayerName(layerId)
mll.setLayerName(layerId, name)

# map mirror influences
mll.configureInfluencesMirrorMapping(dict)  # source - target


# a helper method to use in a “with” statement, e.g.:
with mll.batchUpdateContext():
    mll.setLayerWeights(...)
    mll.setLayerOpacity(...)

# this is the same as:
mll.beginDataUpdate()
try:
    mll.setLayerWeights(...)
    mll.setLayerOpacity(...)
finally:
    mll.endDataUpdate()
