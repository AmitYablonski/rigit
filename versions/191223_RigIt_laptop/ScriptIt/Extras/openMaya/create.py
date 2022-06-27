from maya import OpenMaya

# differences between three MObject.create()
MObject create(
    int numVertices,
    int numPolygons,
    const MPointArray &vertexArray,
    const MIntArray &polygonCounts,
    const MintArray &polygonConnects,
    MObjeect parentOrOwner=MObject::kNullObj,
    Mstatus *ReturnStatus=NULL)

MObject create(
    int numVertices,
    int numPolygons,
    const MFloatPointArray &vertexArray,  # <- difference
    const MIntArray &polygonCounts,
    const MintArray &polygonConnects,
    MObject parentOrOwner=MObject::kNullObj,
    Mstatus *ReturnStatus=NULL)

MObject create(
    int numVertices,
    int numPolygons,
    const MPointArray &vertexArray,
    const MIntArray &polygonCounts,
    const MintArray &polygonConnects,
    const MFloatArray &uArray,  # <- difference
    const MFloatArray &vArray,  # <- difference
    MObject parentOrOwner=MObject::kNullObj,
    Mstatus *ReturnStatus=NULL)
