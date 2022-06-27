# source: http://austinjbaker.com/manipulating-objects-part-2

import maya.OpenMaya as OpenMaya

mfn_mesh = OpenMaya.MFnMesh()

# Total number of vertices.
numVertices = 8

# Vertex array.
vertexArray = OpenMaya.MFloatPointArray()

# Positions for each vertex.
vertex_0 = OpenMaya.MFloatPoint(1.0, -1.0, 1.0)
vertex_1 = OpenMaya.MFloatPoint(1.0, -1.0, -1.0)
vertex_2 = OpenMaya.MFloatPoint(-1.0, -1.0, -1.0)
vertex_3 = OpenMaya.MFloatPoint(-1.0, -1.0, 1.0)
vertex_4 = OpenMaya.MFloatPoint(1.0, 1.0, 1.0)
vertex_5 = OpenMaya.MFloatPoint(1.0, 1.0, -1.0)
vertex_6 = OpenMaya.MFloatPoint(-1.0, 1.0, -1.0)
vertex_7 = OpenMaya.MFloatPoint(-1.0, 1.0, 1.0)

# Add the vertex positions to the array.
vertexArray.append(vertex_0)
vertexArray.append(vertex_1)
vertexArray.append(vertex_2)
vertexArray.append(vertex_3)
vertexArray.append(vertex_4)
vertexArray.append(vertex_5)
vertexArray.append(vertex_6)
vertexArray.append(vertex_7)

# Total number of faces.
numPolygons = 6

# Number of vertices per polygon face.
vertsPerPolyList = [4, 4, 4, 4, 4, 4]
polygonCounts = OpenMaya.MIntArray()
OpenMaya.MScriptUtil.createIntArrayFromList(vertsPerPolyList, polygonCounts)

# Polygon connections.
vertPolyConnectsList = [0, 1, 2, 3,
                        4, 5, 6, 7,
                        1, 5, 4, 0,
                        1, 5, 6, 2,
                        2, 6, 7, 3,
                        0, 4, 7, 3]
PolygonConnects = OpenMaya.MIntArray()
OpenMaya.MScriptUtil.createIntArrayFromList(vertPolyConnectsList, PolygonConnects)

# Cube MObject.
objCube = OpenMaya.MObject()

mfn_mesh.create(numVertices, numPolygons, vertexArray, polygonCounts, PolygonConnects, objCube)