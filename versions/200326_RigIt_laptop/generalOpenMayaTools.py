import maya.OpenMaya as om
from maya import cmds, mel
import pymel.core as pm
from functools import partial
import fnmatch
import re
import os, sys

__author__ = 'Amir Ronen'

# -- find closest vtx/face
# your MFnMesh object
targetFn = om.MFnMesh(targetDag)

# your locator position
locPos = om.MPoint(1.2, 0.4, 0.2)

# returned closest point
closestPoint = om.MPoint()

# returned int ptr to closest face
mutil = om.MScriptUtil()
intPtr = mutil.asIntPtr()


# find the closest point and id
targetFn.getClosestPoint(locPos, closestPoint, om.MSpace.kWorld, intPtr)

# get the closest face
closestPolygonId = om.MScriptUtil(intPtr).asInt()


# setIndex requires a ptr to previous index
dummyPtr = mutil.asIntPtr()

polyIter = om.MItMeshPolygon(targetDag)
polyIter.setIndex(closestPolygonId, dummyPtr)

# get vertices from this face
pArray = om.MPointArray()
vArray = om.MIntArray()
polyIter.getPoints(pArray, om.MSpace.kWorld)
polyIter.getVertices(vArray)

