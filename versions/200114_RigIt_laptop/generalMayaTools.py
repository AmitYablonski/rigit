from maya import cmds, mel
import pymel.core as pm
from functools import partial
import fnmatch
import re
import os, sys

__author__ = 'Amir Ronen'


def listSelection(selItem):
    if not selItem:
        return
    if isinstance(selItem, (list, tuple)):
        for sel in selItem:
            listSelection(sel)
    else:
        pm.select(selItem, add=True)


def listCheckAdd(obj, checkList):
    if checkList:
        for item in checkList:
            if item.name() == obj.name():
                return checkList
    checkList.append(obj)
    return checkList


def unifyList(listItem, newList=[]):
    if not listItem:
        return
    tempList = []
    if isinstance(listItem, (list, tuple)):
        for item in listItem:
            item = unifyList(item, newList)
    else:
        if listItem:
            print
            listItem
            tempList.append(listItem)
    if tempList:
        for item in tempList:
            newList = listCheckAdd(listItem, newList)
    return newList


def searchTypeBySetOrId(shape1, searchType, type1, returnList):
    conList = pm.listConnections(shape1, type=searchType)
    for obj in conList:
        if type1 in obj.name():
            conn = pm.listConnections(obj, type=type1)
            if conn:
                for con in conn:
                    returnList = listCheckAdd(con, returnList)
    return returnList


def getTypeFromShape(shape1, type1):
    returnList = []
    conn = pm.listConnections(shape1, type=type1)
    if conn:
        for con in conn:
            returnList.append(con)
    returnList = searchTypeBySetOrId(shape1, 'objectSet', type1, returnList)
    returnList = searchTypeBySetOrId(shape1, 'groupId', type1, returnList)
    return returnList


def getSkin(shape1, *args):
    return mel.eval("findRelatedSkinCluster %s" % shape1)


def selectSkin(*args):
    selection = pm.ls(sl=True)
    skins = []
    for sel in selection:
        try:
            shape1 = sel.listRelatives(s=True)[0]
        except:
            print(sel + " - invalid object - has no shape")
            continue
        skins.append(getSkin(shape1))
    if skins:
        pm.select(skins)
        print("selected the following skin/s: %s" % skins)
        return
    print("no skin/s found")


def bindAndName(*args):
    selection = pm.ls(sl=True)
    jnts = []
    geos = []
    for sel in selection:
        if sel.type() == 'joint':
            jnts.append(sel)
        else:
            if sel.type() == "transform" or sel.type() == "shape":
                geos.append(sel)
    for geo in geos:
        pm.select(geo, jnts)
        skin = pm.skinCluster(toSelectedBones=True)
        skin.rename(geo.name() + "_skinCluster")
    pm.select(selection)


def selectInflu(*args):
    sele = pm.ls(sl=True)
    if not sele:
        print('please select a bound object and try again')
        return
    skinInflu = []
    pm.select(cl=True)
    for sel in sele:
        try:
            shape1 = pm.listRelatives(sel, type="shape")[0]
        except:
            print("// ERROR! - " + sel + " - invalid object - has no shape")
            continue
        skinInflu.append(getSkinInflu(shape1))
    pm.select(skinInflu, add=True)


def getSkinInflu(shape):
    skin = getSkin(shape)
    if isinstance(skin, (list, tuple)):
        skin = skin[0]
    skinInflu = pm.skinCluster(skin, query=True, inf=True)
    return skinInflu


def transferWeights(*args):
    verts = pm.ls(fl=True, os=True)
    mainVtx = verts[0]
    shp = pm.listRelatives(mainVtx, p=True)[0]
    skinInflu = getSkinInflu(shp)
    skin = getSkin(shp)

    transVal = []
    for jnt in skinInflu:
        val = cmds.skinPercent(skin, mainVtx.name(), transform=jnt.name(), query=True)
        if round(val, 3):
            transVal.append([jnt.name(), val])
    print
    mainVtx
    print
    transVal
    print
    verts
    print
    'len %s' % len(verts)
    # assign weights
    for i in range(1, len(verts)):
        print
        verts[i].name()
        cmds.skinPercent(skin, verts[i].name(), transformValue=transVal)


## query skin influences and transfer weights to second selection
def bindAndCopy(*args):
    sel = pm.ls(sl=True)
    try:
        shape1 = pm.listRelatives(sel[0], type="shape")[0]
    except:
        print(sel[0] + " - invalid object - has no shape")
        # return
    skin1 = getSkin(shape1)
    if isinstance(skin1, (list, tuple)):
        skin1 = skin1[0]
    skinInflu = pm.skinCluster(skin1, query=True, inf=True)
    # make the selection to bind
    # pm.select(cl=True)
    for i in range(1, len(sel)):
        pm.select(sel[i])
        for jnt in skinInflu:
            pm.select(jnt, add=True)
        pm.skinCluster(toSelectedBones=True)
        # transfer weights
    for i in range(1, len(sel)):
        shape2 = pm.listRelatives(sel[i], type="shape")[0]
        skin2 = getSkin(shape2)
        if isinstance(skin2, (list, tuple)):
            skin2 = skin2[0]
        pm.copySkinWeights(ss=skin1, ds=skin2, sa="closestPoint", ia="oneToOne", noMirror=True)
        pm.rename(skin2, sel[i] + "_skinCluster")
    pm.select(sel)


def projectsList():
    projectsDir = cmds.workspace(q=True, dir=True).partition('projects/')
    projectsDir = projectsDir[0] + projectsDir[1]
    projects = os.listdir(projectsDir)
    for repitition in range(2):
        for item in projects:
            if '.' in item:
                projects.remove(item)
    return projectsDir, projects


def jointCurvesCreation(namePosition):
    # for namePosition, pass a dictionary with a name as key and position as the value
    # example: namePosition = [('name1', [(-1.0, 1.0, 1.0)]),
    #                          ('zwatan', [(2.0, -2.0, 2.0)]),
    #                          ('anotherName', [(3.0, 3.0, -3.0)])]

    curvelist = []
    for circleSet in newList:
        # Create curves
        cv1 = cmds.circle(nr=[0, 1, 0], sw=360, ch=1)
        cv2 = cmds.circle(nr=[0, 1, 0], sw=360, ch=1)
        cv3 = cmds.circle(nr=[0, 1, 0], sw=360, ch=1)
        # Rotate curves to look like a joint
        cmds.rotate(90, 0, 0, cv2[0])
        cmds.rotate(0, 0, 90, cv3[0])
        # Freeze the rotated curves
        cmds.select(cv2[0])
        cmds.select(cv3[0], add=1)
        cmds.makeIdentity(apply=1, t=1, r=1, s=1)
        # Parent shapes of curves 2 and 3 to curve 1
        relCrv2 = cmds.listRelatives(cv2[0], shapes=1)
        relCrv3 = cmds.listRelatives(cv3[0], shapes=1)
        cmds.parent(relCrv2[0], cv1[0], r=1, shape=1)
        cmds.parent(relCrv3[0], cv1[0], r=1, shape=1)
        # Delete the trns node of curves 2 and 3
        cmds.select(cv2[0])
        cmds.select(cv3[0], add=1)
        cmds.delete()
        # Rename the joint curve
        newCurve = cmds.rename(cv1[0], circleSet[0])
        # Delete history on joint curve
        cmds.select(newCurve)
        cmds.DeleteHistory()
        cmds.setAttr(newCurve + ".tx", circleSet[1][0][0])
        cmds.setAttr(newCurve + ".ty", circleSet[1][0][1])
        cmds.setAttr(newCurve + ".tz", circleSet[1][0][2])
        curvelist.append(newCurve)

        curveList.append(newCurve)

    return curveList


def namespaceFinder():
    namespacseInSel = []
    list = cmds.ls(sl=True)
    if list == []:
        makeSelectionWin()
    for item in list:
        currentNamespace = item.partition(':')[0]
        if currentNamespace not in namespacseInSel:
            namespacseInSel.append(currentNamespace)
    return namespacseInSel


def makeSelectionWin():
    if cmds.window("Make_Selection", exists=True):
        cmds.deleteUI("Make_Selection")
    Make_SelectionUI = cmds.window("Make_Selection", t="Make Selection", rtf=True)
    mainLayout = cmds.columnLayout()
    cmds.text(label="Make a selection and try again", h=40, w=170)
    buttonLayout = cmds.rowLayout(parent=mainLayout, numberOfColumns=2)
    cmds.button(label='OK', h=30, w=170, parent=buttonLayout,
                command=('cmds.deleteUI(\"' + Make_SelectionUI + '\", window=True)'))
    cmds.showWindow(Make_SelectionUI)


# Todo: symmetryFunc - decide what it should do or if it should be a tool
def symmetryFunc(fromObj, toObj):
    print
    fromObj, toObj
    return 'None'


def colorOverride(color, *args):
    selection = pm.ls(sl=True)
    for item in selection:
        item.setAttr("overrideEnabled", 1)
        item.setAttr("overrideRGBColors", 0)
        item.setAttr("overrideColor", color)
        shapes = item.listRelatives(type='shape')
        for shp in shapes:
            shp.setAttr("overrideRGBColors", 0)
            shp.setAttr("overrideColor", color)


def rotateToJntOrient(toRotate=False, *args):
    print
    'updated'
    selection = pm.ls(sl=True)
    for item in selection:
        if pm.objectType(item) == 'joint':
            rotation = pm.xform(item, ro=True, ws=True, q=True)
            item.setAttr('jointOrient', [0, 0, 0])
            pm.xform(item, ro=rotation, ws=True)
            rotation = pm.xform(item, ro=True, os=True, q=True)
            if toRotate:
                item.setAttr('jointOrient', [0, 0, 0])
                item.setAttr('r', rotation)
            else:
                item.setAttr('r', [0, 0, 0])
                item.setAttr('jointOrient', rotation)
        else:
            print
            'skipping - "%s" is not a joint'


def zeroJntOrients(*args):
    selection = pm.ls(sl=True)
    for item in selection:
        if pm.objectType(item) == 'joint':
            item.setAttr('jointOrient', [0, 0, 0])
        else:
            print
            'skipping - "%s" is not a joint'


def grpIt(prefix='None', new_prefix='None'):  # todo take the grpIt from Summer explorer
    selection = cmds.ls(sl=True)
    groups = []
    for item in selection:
        cmds.select(item)
        translate = cmds.xform(t=True, q=True, ws=True)
        rotate = cmds.xform(ro=True, q=True, ws=True)
        originalParent = cmds.listRelatives(parent=True, fullPath=True)
        group = cmds.group(em=True)
        groups.append(group)
        cmds.xform(t=translate, ws=True)
        cmds.xform(ro=rotate, ws=True)
        cmds.parent(item, group)
        if originalParent:
            cmds.parent(group, originalParent)

        # temp solution:
        name = 'grp_' + item
        cmds.rename(group, name)


def createChannelBox(colors=True, window=True):
    if window:
        cmds.window()
    formLay = cmds.formLayout()
    cBox = cmds.channelBox()
    cmds.formLayout(formLay, e=True,
                    af=((cBox, 'top', 0), (cBox, 'left', 0), (cBox, 'right', 0), (cBox, 'bottom', 0)))
    if colors:
        # Color attributes according to name search
        # cmds.channelBox(cBox, attrRegex='T*', attrColor=(1.0, 1.0, 1.0), attrBgColor=(0.0, 0.0, 0.0))
        cmds.channelBox(cBox, e=True, attrRegex='*X', attrBgColor=(1, .6, 0.6), attrColor=(.0, .0, .0))
        cmds.channelBox(cBox, e=True, attrRegex='*Y', attrBgColor=(0.6, 1, 0.6), attrColor=(.0, .0, .0))
        cmds.channelBox(cBox, e=True, attrRegex='*Z', attrBgColor=(0.6, .6, 1), attrColor=(.0, .0, .0))
    if not window:
        return formLay, cBox
    cmds.showWindow()


def printVal(pport):
    print(pm.palettePort(pport, query=True, rgb=True))


def createColorPallet(h=50, w=100, palletColumn=70, palletRow=1, window=True):
    if window:
        cmds.window()
    portLay = cmds.frameLayout(labelVisible=0, h=h, w=w)
    pport = pm.palettePort('palette', dim=(palletColumn, palletRow))
    pm.palettePort(pport, edit=True, cc=partial(printVal, pport))
    # select cell #30
    pm.palettePort(pport, edit=True, scc=30)
    # make cell #100 transparent and blue
    # cmds.palettePort('palette', edit=True, transparent=100, rgb=(100, 0.0, 0.0, 1.0))
    # cmds.palettePort('palette', edit=True, redraw=True)
    #
    # returns the current transparent cell (there can be only one)
    # cmds.palettePort('palette', query=True, transparent=True)
    if not window:
        return portLay
    cmds.showWindow()


'''
def nextNamespaceByPrefix(prefix, digitFormat="\d+$"):
    listNameSpace = cmds.namespaceInfo(":", lon=True)
    namePattern = re.compile("{0}{1}".format(prefix, digitFormat))
    if prefix + '01' in listNameSpace:
        digitPattern = re.compile(digitFormat)
        foundIndexes = []
        for item in listNameSpace:
            if not namePattern.match(item):
                continue
            match = digitPattern.findall(item)
            if match:
                foundIndexes.append(int(match[-1]))
        maxIndex = max(foundIndexes)
        pattern = "{0}{{:0{1}d}}".format(prefix, 2)

        return pattern.format(maxIndex + 1)
    return prefix + '01'


def createGroupsFromList(list, loc=False):
    #upperGroup = cmds.group(name='grp_createGroupsFromList', em=True)
    groups = []
    for item in list:
        cmds.select(item)
        position = cmds.xform(q=True, t=True, ws=True)
        cmds.select(cl=True)
        if loc == True:
            if 'be_' in item:
                newObj = cmds.spaceLocator(name='loc_' + item)
            else:
                newObj = cmds.spaceLocator(name=item.replace('jnt_', 'loc_'))
        else:
            if 'be_' in item:
                newObj = cmds.group(name='grp_' + item, em=True)
            else:
                newObj = cmds.group(name=item.replace('jnt_', 'grp_'), em=True)
        cmds.xform(t=position, ws=True)
        groups.append(newObj)
        #cmds.parent(newObj, upperGroup)
    return groups


def jointCurveTool(newName='None', radius=1):
    # Create curves
    cv1 = cmds.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=radius, d=3, ut=0, ch=1)
    cv2 = cmds.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=radius, d=3, ut=0, ch=1)
    cv3 = cmds.circle(c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=radius, d=3, ut=0, ch=1)
    # Parent shapes of curves 2 and 3 to curve 1
    relCrv2 = cmds.listRelatives(cv2[0], shapes=True)
    relCrv3 = cmds.listRelatives(cv3[0], shapes=True)
    cmds.parent(relCrv2[0], cv1[0], r=True, shape=True)
    cmds.parent(relCrv3[0], cv1[0], r=True, shape=True)
    # Delete the trans node of curves 2 and 3
    cmds.delete(cv2[0], cv3[0])
    # Rename the joint curve
    if newName == 'None':
        newCrv = cmds.rename(cv1[0], "jntCrv")
    else:
        newCrv = cmds.rename(cv1[0], newName)
    # Delete history on joint curve
    cmds.select(newCrv)
    cmds.DeleteHistory()
    return newCrv
'''


# ToDo: make a tool out of this (distance tool)
def distanceCreateConnect(object1, object2, objectAttr, *args):
    distNode = pm.shadingNode("distanceBetween", asUtility=True)
    object1.worldMatrix >> distNode.inMatrix1
    object2.worldMatrix >> distNode.inMatrix2
    pm.connectAttr(distNode.distance, objectAttr)
    return (distNode)


def deleteConstraints(*args):
    selection = pm.ls(sl=True)
    for sel in selection:
        con = pm.listRelatives(sel, typ='constraint')
        if not con:
            print("No constraints found on => " + sel)
        else:
            pm.delete(con)
            print("deleted constraints from " + sel + " => %s" % con)


def lockAttributes(lock, attrs='', *args):
    selection = pm.ls(sl=True)
    for sel in selection:
        if attrs:
            if isinstance(attrs, list) or isinstance(attrs, tuple):
                for attr in attrs:
                    sel.setAttr(attr, l=lock)
            else:
                sel.setAttr(attrs, l=lock)
        else:
            for i in "xyz":
                sel.setAttr("t" + i, l=lock)
                sel.setAttr("r" + i, l=lock)
                sel.setAttr("s" + i, l=lock)


# usage examples:
# lockAttributes(True)
# lockAttributes(False)
# lockAttributes(True, ["tx", "rz"])
# lockAttributes(True, "rx")


def colorPickerRGB(*args):
    cmds.colorEditor()
    if cmds.colorEditor(query=True, result=True):
        values = cmds.colorEditor(query=True, rgb=True)
        return values


def colorPickerHSV(*args):
    cmds.colorEditor()
    if cmds.colorEditor(query=True, result=True):
        values = cmds.colorEditor(query=True, hsv=True)
        return values


# create lite wrap deformers
def liteWrap(objToWrap, heavyMesh, deleteFaces):
    simpleGeo = pm.duplicate(heavyMesh)[0]
    simpleGeo.rename(objToWrap + "_wrapper")
    # select and delete faces
    pm.select(cl=True)
    for faces in deleteFaces:
        pm.select(heavyMesh + faces, add=True)
    sel = pm.ls(sl=True)
    pm.delete(sel)
    # find deleteComponent node and reconnect it with the new shape
    deleteComponentNode = pm.listConnections(heavyMesh + "Shape", c=True, type="deleteComponent")[0][1]
    heavyMeshAttr = heavyMesh + "Shape.inMesh"
    pm.rename(deleteComponentNode, "deleteComponent_" + objToWrap)
    # reconnect heavy geo
    attrOrigin = pm.connectionInfo(deleteComponentNode + ".inputGeometry", sfd=True)
    cmds.connectAttr(attrOrigin, heavyMeshAttr, f=True)
    cmds.connectAttr(heavyMesh + "Shape.worldMesh[0]", deleteComponentNode + ".inputGeometry", f=True)
    # connect deleteComponentNode to new geo and wrap it
    cmds.connectAttr(deleteComponentNode + ".outputGeometry", simpleGeo + "Shape.inMesh", f=True)
    pm.select(objToWrap, simpleGeo)
    cmds.CreateWrap()
    newWrap = pm.listConnections(simpleGeo + "Shape", c=True, type="wrap")[0][1]
    pm.rename(newWrap, "wrap_" + objToWrap)
    return simpleGeo, newWrap


def isShape(obj):
    if isinstance(obj, pm.nodetypes.Shape):
        return True
    return False


# ToDo: possibly check for more exceptions
def parentShape(*args):
    sel = pm.ls(sl=True)
    if len(sel) < 2:
        print("Must select at least two objects to reparent a shape")
        return
    newPar = sel[len(sel) - 1]
    origShapes = pm.listRelatives(newPar, type="shape")
    for i in range(0, len(sel) - 1):
        obj = sel[i]
        if obj.type() == 'shape':
            print
            'shape selected'
            shapes = [obj]
        else:
            shapes = pm.listRelatives(obj, type="shape")
        for shape in shapes:
            pm.select(shape, newPar)
            pm.parent(r=True, s=True)
        if origShapes:
            pm.delete(origShapes)
        print("Reparented following shapes under %s    =>    %s\nDeleted %s" % (newPar, shapes, sel[i]))


def parentShape_old(*args):
    sel = pm.ls(sl=True)
    if len(sel) < 2:
        print("Must select at least two objects to reparent a shape")
        return
    newPar = sel[len(sel) - 1]
    for i in range(0, len(sel) - 1):
        shapes = pm.listRelatives(sel[i], type="shape")
        for shape in shapes:
            pm.select(shape, newPar)
            pm.parent(r=True, s=True)
        pm.delete(sel[i])
        print("Reparented following shapes under %s    =>    %s\nDeleted %s" % (newPar, shapes, sel[i]))


def stringMyPmList(list, pyNode=False):
    if list:
        if pyNode:
            string = '[pm.PyNode("%s")' % list[0].name()
            for i in range(1, len(list)):
                string += ', pm.PyNode("%s")' % list[i].name()
        else:
            string = '["%s"' % list[0].name()
            for i in range(1, len(list)):
                string += ', "%s"' % list[i].name()
        return string + "]"


def getBsp(shape1, *args):
    '''
    Get the blend shape nodes from shape
    :param shape1:  shape object to get bsps
    :param args:
    :return: a list of list of blend shapes (return empty if none found)
    '''
    blendShapes = []
    blendShapes = getTypeFromShape(shape1, 'blendShape')
    return unifyList(blendShapes)


def selectBsp(*args):
    sele = pm.selected()
    if len(sele) < 1:
        print
        ' // make a selection and try again'
        return
    allBsps = []
    for obj in sele:
        bShapes = findBlendShape(obj)
        if not bShapes:
            print
            ' // no Blend Shape node found on "%s"' % obj
        else:
            for bsp in bShapes:
                allBsps.append(bsp)
    pm.select(allBsps)


# find the first available index in bsp
def bspFreeIndex(bsp):
    targetList = pm.aliasAttr(bsp, query=True)
    targetNums = []
    for i in targetList[1::2]:
        num = i.split("weight[")[-1][:-1]
        targetNums.append(int(num))
    i = 0
    while (i < 200):
        if i not in targetNums:
            break
        i += 1
    return i


def findBlendShape(geometry):
    bShapes = []
    history = pm.listHistory(geometry)
    for hist in history:
        types = pm.nodeType(hist, inherited=True)
        if 'geometryFilter' in types:
            if 'BlendShape' in pm.nodeType(hist, apiType=True):
                if hist.type() == 'blendShape':
                    conn = pm.listConnections(hist, d=True, s=False)
                    for con in conn:
                        if geometry + '_blendShapeSet' in con.name():
                            # FOUND !
                            bShapes.append(hist)
                        elif con.type() == 'skinCluster':
                            conn2 = pm.listConnections(con, d=True, s=False)
                            for con2 in conn2:
                                if 'objectSet' == con2.type():
                                    conn3 = pm.listConnections(con2, d=True, s=False)
                                    if conn3:
                                        if conn3[0].name() == geometry:
                                            # FOUND !
                                            bShapes.append(hist)
    return bShapes


def createBsp(add=False, *args):
    sele = pm.selected()
    if len(sele) < 2:
        print
        ' // make a selection and try again'
        return
    bsps = []
    for i in range(0, len(sele) - 1):
        bsps.append(sele[i])
    obj = sele[len(sele) - 1]
    if not add:
        bShape = pm.blendShape(bsps, obj, n=obj.name() + '_blendShape', foc=True)
    else:
        bShapes = findBlendShape(obj)
        if not bShapes:
            print
            ' // no Blend Shape node found on "%s"' % obj
            return
        else:
            if len(bShapes) > 1:
                # todo make a selection window if found multiple blend shapes
                print(" // Can't deal with multiple blend shapes yet.\nblendShape nodes found: %s" % bShapes)
                return
            else:
                bShape = bShapes[0]
        for bsp in bsps:
            pos = bspFreeIndex(bShape)
            # print 'pm.blendShape(%s, edit=True, t=[%s, %s, %s, 1.0])' % (bShape,obj, pos, bsp)
            pm.blendShape(bShape, edit=True, t=[obj, pos, bsp, 1.0])
    pm.select(bShape)
    return bShape


def createCrvFromSelection(selection=True, vertsList=[], *args):
    """
    Creates a curve according to vertex selection.
    The curve creates locators that control the curve as well
    # if using selection, this must be used (already added to UI file): pm.selectPref(trackSelectionOrder=1)
    :param args:  works with a button (for selection)
    :param selection: if using a list of verts, this should be False.
    :param vertsList: a list of single verts in the order of creation.
    :return: list of locators that control the new curve's points
    """
    if selection:
        vertsList = pm.ls(fl=True, os=True)  # os = orderedSelection
    points = []
    for obj in vertsList:
        try:  # in case it's a PyNode
            name = obj.name()
        except:
            name = obj
        if ".vtx[" in name:
            pos = pm.xform(obj, query=True, t=True, ws=True)
            points.append(pos)
        else:
            print
            " // skipping: \"%s\". is it a vertex?" % obj
    name = name.rpartition('.vtx[')[0]
    if 'Shape' in name:
        name = name.rpartition('Shape')[0]
    crv = pm.curve(p=points, degree=1, n=name + "_crv")
    grp = pm.group(em=True, w=True, n=crv.name() + '_locCtl_grp')
    locs = []
    for i in range(0, (len(points))):
        loc = pm.pointCurveConstraint(crv + '.ep[%s]' % i, ch=True)[0]
        loc = pm.PyNode(loc)
        loc.rename('locCtl_%s_%s' % (crv.name(), i))
        pm.parent(loc, grp)
        pm.select(loc)
        mel.eval('CenterPivot;')
        locs.append(loc)
    return locs


def instanceToObject(*args):
    instaList = pm.ls(sl=True)
    for ins in instaList:
        print
        '// # checking if "%s" is instance : ' % ins
        mel.eval('ConvertInstanceToObject')


def updateToHierarchy(trasformsList, *args):
    updatedList = []
    for obj in trasformsList:
        children = pm.listRelatives(obj, ad=True)
        for ch in children:
            if not isShape(ch) and ch not in updatedList:
                updatedList.append(ch)
        updatedList.append(obj)
    return updatedList


def filterMeshSelection(hierarchy=False, *args):
    selection = pm.selected()
    if hierarchy:
        selection = updateToHierarchy(selection)
    meshes = []
    for sel in selection:
        shps = pm.listRelatives(sel, s=True)
        if shps:
            meshes.append(sel)
    pm.select(meshes)


# todo check if this is necessary
class safeopen(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.f = None

    def __enter__(self):
        self.f = open(*self.args, **self.kwargs)
        return self.f

    def __exit__(self, *exc_info):  # exc_info = exception information
        if self.f:
            self.f.close()


def getChildrenFromFile(filePath, objParent):
    '''
    This method reads a file and searches for any items under a requested transform
    :param filePath: path for desired file
    :param objParent: the parent to search for
    :return: a list of items under the requested transform
    '''
    parList = []
    if cmds.file(filePath, query=True, exists=True):
        f = open(filePath, 'r')
        i = 1
        parentText = '" -p "%s";' % objParent
        parentText2 = '" -parent "%s";' % objParent
        for line in f:
            if parentText in line:
                obj = line.rpartition(parentText)[0].rpartition('-n "')[2]
                parList.append(obj)
            if parentText2 in line:
                obj = line.rpartition(parentText2)[0].rpartition('-name "')[2]
                parList.append(obj)
    else:
        print(' // failed reading file: %s' % filePath)
    return parList


def getAllUVmaps(obj):
    return pm.polyUVSet(obj, q=True, auv=True)


def hasSkin(obj):
    shp = pm.listRelatives(obj, s=True)
    if shp:
        skin = getSkin(shp[0])
        if skin:
            return True
    return False


def isValidMap(map1, obj1):
    if not pm.objExists(obj1):
        return
    maps = getAllUVmaps(obj1)
    if map1 not in maps:
        print('map %s not found for %s' % (map1, obj1))
        return False
    return True


def getAttrOutputs(attr):
    return pm.listConnections(attr, source=False, destination=True, plugs=True)  # , scn=True)?


def getAttrInputs(attr):
    return pm.listConnections(attr, source=True, destination=False, plugs=True)  # , scn=True)?


def setDrivenKey(driver, driven, driverVal, drivenVal):
    print(' -> doing sdk driver="%s", driven="%s", driverVal=%s, drivenVal=%s' % (driver, driven, driverVal, drivenVal))
    for val1, val2 in zip(driverVal, drivenVal):
        pm.setDrivenKeyframe(driven, cd=driver, dv=val1, v=val2)


def findNextBlendInput(blendNode):
    for i in range(0, 200):
        try:
            conn = getAttrInputs(blendNode.attr('input[%s]' % i))
            if not conn:
                return 'input[%s]' % i
        except:
            print(' // got to input[%s] and failed' % i)
            return ''


def getTimlineStartEnd():
    startKey = pm.playbackOptions(q=True, animationStartTime=True)
    endKey = pm.playbackOptions(q=True, animationEndTime=True)
    return startKey, endKey


def findFileTxNode(mtl):
    conn = pm.listConnections(mtl, s=True, d=False, p=True, c=True)
    cons = {}
    for mtl_attr, sourceAttr in conn:
        source = pm.PyNode(sourceAttr.name().rpartition('.')[0])
        attrName = str(mtl_attr.name().rpartition('.')[2])
        cons[attrName] = []
        if pm.uvLink(isValid=True, texture=source):
            name = str(source.name())
            if name not in cons[attrName]:
                cons[attrName].append(name)
        else:
            files = reFindTxNode(source)  # , 2) todo (already working) make it stop after 2 recursions?
            if files:
                for name in files:
                    if name not in cons[attrName]:
                        cons[attrName].append(name)
        if not cons[attrName]:
            del cons[attrName]
    return cons


def reFindTxNode(source):  # todo limit repeats? (depth of recursion)
    conn = pm.listConnections(source, s=True, d=False, p=True, c=True)
    cons = []
    for mtl_attr, sourceAttr in conn:
        source2 = pm.PyNode(sourceAttr.name().rpartition('.')[0])
        if pm.uvLink(isValid=True, texture=source2):
            name = str(source2.name())
            if name not in cons:
                cons.append(name)
        else:
            files = reFindTxNode(source2)
            if files:
                for name in files:
                    if name not in cons:
                        cons.append(name)
    return cons


def findMaterial(obj):
    shp = pm.listRelatives(obj, s=True)
    conn = pm.listConnections(shp)
    mtls = []
    for con in conn:
        if con.classification()[0] == 'shadingEngine':
            conn2 = pm.listConnections(con)
            for mtl in conn2:
                if 'shader' in mtl.classification()[0]:  # todo test for vray
                    if mtl not in mtls:
                        mtls.append(mtl)
    return mtls


def parentScaleConstraint(ctl, grp):
    pm.parentConstraint(ctl, grp, mo=True)
    pm.scaleConstraint(ctl, grp, mo=True)


def removeNgSkinTools():
    # remove ngSkinTools custom nodes
    from ngSkinTools.layerUtils import LayerUtils
    LayerUtils.deleteCustomNodes()


def hasBlendShape(obj):
    bShapes = []
    history = pm.listHistory(obj)
    # Search on object's history for blend shape nodes
    for hist in history:
        types = pm.nodeType(hist, inherited=True)
        if 'geometryFilter' in types:
            if 'BlendShape' in pm.nodeType(hist, apiType=True):
                return True
    return False


def isUnderPar(obj, parName, exactName=False):
    '''
    Searches for parent
    :param obj: PyNode object
    :param parName: string with the parent's name
    :param exactName: False is default and looks if parName is in the name
           if true, parName will have to match to return True
    :return: bool
    '''
    if not obj:
        return False
    if isinstance(obj, (str, unicode)):
        obj = pm.PyNode(obj)
    if exactName:
        if parName == obj.name():
            return True
    else:
        if parName in obj.name():
            return True
    par = pm.listRelatives(obj, p=True)
    if not par:
        return False
    return isUnderPar(par[0], parName, exactName)


'''
def findBlendShapes(obj):
    bShapes = []
    history = pm.listHistory(obj)
    # Search on object's history for blend shape nodes
    for hist in history:
        types = pm.nodeType(hist, inherited=True)
        if 'geometryFilter' in types:
            if 'BlendShape' in pm.nodeType(hist, apiType=True):
                bShapes.append(hist)
    if (len(bShapes) > 0):
        if (len(bShapes) > 1):
            self.bShapeSelectionWin(bShapes)
        else:
            self.bsp = bShapes[0]
        return self.bsp
    return False


def bShapeSelectionWin(bShapes):
    if pm.window("bspSel_win", exists=True):
        pm.deleteUI("bspSel_win")
    pm.window("bspSel_win", title="Select Blend Shape", sizeable=1, rtf=True)
    cmds.rowColumnLayout(numberOfColumns=1, adj=True)
    bShapeNames = []
    for bsp in bShapes:
        bShapeNames.append(bsp.name())
    hight = 20 * len(bShapes)
    if hight < 100:
        hight = 100
    bspScroll = pm.textScrollList(append=bShapeNames, allowMultiSelection=False,
                                                  sii=1, w=250, h=hight)
    pm.button(l="Select Blend Shape", h=40, c=partial(bspWinSelection, bShapes, bspScroll))
    pm.showWindow()
    #pm.window(self.widgets["bspSel_win"], e=True, h=100)


def bspWinSelection(bShapes, bspScroll, txField, *args):
    idx = pm.textScrollList(bspScroll, query=True, selectIndexedItem=True)[0]
    idx -= 1
    pm.textField(txField, e=True, text=bShapes[idx].name())
    bsp = bShapes[idx].name()
    sel = pm.ls(sl=True)
    pm.select(bShapes[idx])
    pm.select(sel)
    pm.deleteUI("bspSel_win")
'''
