from maya import cmds, mel
import pymel.core as pm
import generalMayaTools as gmt
import fnmatch
import re
import os, sys

__author__ = 'Amir Ronen'


def cleanListForPrint(inList):
    printStr = "['%s'" % inList[0]
    for i in range(1, len(inList)):
        printStr += ", '%s'" % inList[i]
    printStr += "]"
    return printStr


def isSelectionOk(sel):
    if len(sel) < 1:
        print "Please make a selection and try again"
        return False
    return True


def printSelected(*args):
    sel = pm.ls(sl=True)
    if not isSelectionOk(sel):
        return
    print cleanListForPrint(sel)


def printBlendShapes(*args):
    sele = pm.ls(sl=True)
    if len(sele) < 1:
        print "Please make a selection and try again"
        return
    allBsps = []
    for sel in sele:
        bsps = gmt.getBsp(sel.getShape())
        if bsps:
            for bsp in bsps:
                allBsps.append(bsp.name())
    if allBsps:
        print allBsps
    else:
        print 'No Blend Shapes found for selection'


def printSkinClusters(*args):
    sele = pm.ls(sl=True)
    if len(sele) < 1:
        print "Please make a selection and try again"
        return
    allSkins = []
    for sel in sele:
        skins = gmt.getSkin(sel.getShape())
        if isinstance(skins, (list, tuple)):
            for skin in skins:
                allSkins.append(skin.name())
        else:
            allSkins.append(skins)
    if allSkins:
        print allSkins
    else:
        print 'No Skin Clusters found for selection'


def printXformSelected(sel, ws):
    cmds.select(sel)
    if not isSelectionOk(sel):
        return
    selTrans = pm.xform(query=True, t=True, ws=ws)
    selRotate = pm.xform(query=True, ro=True, ws=ws)
    selScale = pm.xform(query=True, s=True, ws=ws)
    for set in [["translate", selTrans], ["rotate", selRotate], ["scale", selScale]]:
        vector = set[1]
        print("%s = [%0.3f, %0.3f, %0.3f]" % (set[0], vector[0], vector[1], vector[2]))


def printXform(ws, *args):
    selection = cmds.ls(sl=True)
    if not isSelectionOk(selection):
        return
    for sel in selection:
        component = ""
        if ".vtx[" in sel:
            component = ".vtx["
        elif ".f[" in sel:
            component = ".f["
        elif ".e[" in sel:
            component = ".e["
        if component:
            object = sel.rpartition(component)
            if ":" in object[2]:
                object = object[0]
                parts = sel.rpartition(component)[2].rpartition(":")
                start = int(parts[0])
                end = int(parts[2].rpartition("]")[0])
                for i in range(start, end + 1):
                    comp = object + component + str(i) + "]"
                    print("    =>    print xform (ws=" + str(ws) + ") for: " + comp)
                    printXformSelected(comp, ws)
            else:
                print("    =>    print xform (ws=" + str(ws) + ") for: " + sel)
                printXformSelected(sel, ws)
        else:
            print("    =>    print xform (ws=" + str(ws) + ") for: " + sel)
            printXformSelected(sel, ws)
    pm.select(selection)


# list faces names by selection (u'obj.f[2:5]' ==> u'.f[2:5]')
def componentLister(p=True, *args):
    selection = cmds.ls(sl=True)
    if not isSelectionOk(selection):
        return
    component = ""
    if len(selection) > 0:
        if ".vtx[" in selection[0]:
            component = ".vtx["
        elif ".f[" in selection[0]:
            component = ".f["
        elif ".e[" in selection[0]:
            component = ".e["
    if component:
        compList = []
        for item in selection:
            parts = item.rpartition(component)
            compList.append(parts[1] + parts[2])
        if p:
            print cleanListForPrint(compList)
        return compList
    else:
        print("No component selected, Select either faces, vertices or edges and try again")


def colorPickerPrint(printAlpha=False, *args):
    cmds.colorEditor()
    if cmds.colorEditor(query=True, result=True):
        print("// Color Picker Print //")
        values = cmds.colorEditor(query=True, rgb=True)
        print("RGB = [%0.3f, %0.3f, %0.3f]" % (values[0], values[1], values[2]))
        values = cmds.colorEditor(query=True, hsv=True)
        print("HSV = [%0.3f, %0.3f, %0.3f]" % (values[0], values[1], values[2]))
        if printAlpha:
            alpha = cmds.colorEditor(query=True, alpha=True)
            print("Alpha = " + str(alpha))
        return
    else:
        return


def printUniqueAttrs(*args):
    selection = pm.ls(sl=True)
    if not isSelectionOk(selection):
        return
    for sel in selection:
        if sel.nodeType() != 'transform':
            print ' // Must select a transform node to search for unique attributes.'
            return
        allAttrs = pm.listAttr(sel, r=1, s=1, k=1)
        removeAttrs = fnmatch.filter(allAttrs, "translate*")
        removeAttrs = removeAttrs + fnmatch.filter(allAttrs, "rotate*")
        removeAttrs = removeAttrs + fnmatch.filter(allAttrs, "scale*")
        removeAttrs = removeAttrs + fnmatch.filter(allAttrs, "visibility")
        for attr in removeAttrs:
            allAttrs.remove(attr)
        if not allAttrs:
            print " // No unique attributes found on \"%s\"" % sel
            return
        # start listing the unique attrs
        print("//  ==>  Attrs found in '" + sel + "' are:    <==")
        for attr in allAttrs:
            print("*    =>    Unique attr \"" + attr + "\": ")
            if pm.attributeQuery(attr, node=sel, e=True):
                print("*     enum attribute with (current val is " + str(pm.getAttr(sel + "." + attr)) + "):")
                print("*     %s" % pm.attributeQuery(attr, node=sel, listEnum=True))
            else:
                print("*     current val : %s" % pm.getAttr(sel + "." + attr))
                try:
                    print("*     range : %s" % pm.attributeQuery(attr, node=sel, range=True))
                except:
                    continue


# analyze deformers for current selection
def analyzeDeformers(*args):
    selection = pm.ls(sl=True)
    if not isSelectionOk(selection):
        return
    allWraps = {}
    allBShapes = {}
    allSkins = {}
    allDeformers = {}
    for sel in selection:
        wraps = []
        bShapes = []
        skins = []
        deformers = []
        history = pm.listHistory(sel)
        for hist in history:
            types = pm.nodeType(hist, inherited=True)
            if 'geometryFilter' in types:
                if 'BlendShape' in pm.nodeType(hist, apiType=True):
                    bShapes.append(hist)
                if 'Wrap' in pm.nodeType(hist, apiType=True):
                    wraps.append(hist)
                if 'Skin' in pm.nodeType(hist, apiType=True):
                    skins.append(hist)
                deformers.append(hist)
        if (len(wraps) > 0):
            allWraps[sel] = wraps
        if (len(bShapes) > 0):
            allBShapes[sel] = bShapes
        if (len(skins) > 0):
            allSkins[sel] = skins
        if (len(deformers) > 0):
            allDeformers[sel] = deformers
        if not wraps and not bShapes and not skins and not deformers:
            print(" // \"%s\"has no deformers" % sel)
            return

    # print all found deformers
    if allDeformers:
        print("//  ==>  Deformers found :")
        for obj in allDeformers:
            print("*  **  " + obj + "  has  " + str(len(allDeformers[obj])) + "  deformers :")
            for d in allDeformers[obj]:
                print("*        - " + d)

    # print wrap deformers
    if allWraps:
        print("//  ==>  Wrap Deformers :")
        for obj in allWraps:
            print("*  **  " + obj + "    ==>    " + str(len(allWraps[obj])) + "    wrap deformers :")
            for d in allWraps[obj]:
                print("*        - " + d)

    # print blend shapes
    if allBShapes:
        print("//  ==>  Blend Shapes :")
        for obj in allBShapes:
            print("*  **  " + obj + "    ==>    " + str(len(allBShapes[obj])) + "    blend shapes :")
            for d in allBShapes[obj]:
                print("*        - " + d)

    # print skins
    if allSkins:
        print("//  ==>  Skins :")
        for obj in allSkins:
            print("*  **  " + obj + "    ==>    " + str(len(allSkins[obj])) + "    skins :")
            for d in allSkins[obj]:
                print("*        - " + d)


def getInfluList(toPrint=False, *args):
    sel = pm.ls(sl=True)
    if not isSelectionOk(sel):
        return
    print("getting influence list for: %s" % sel[0])
    try:
        shape1 = pm.listRelatives(sel[0], type="shape")[0]
    except:
        print(sel[0] + " - invalid object - has no shape")
        return
    skin1 = gmt.getSkin(shape1)
    if isinstance(skin1, (list, tuple)):
        skin1 = skin1[0]
    skinInflu = pm.skinCluster(skin1, query=True, inf=True)
    if toPrint:
        temp = []
        for influ in skinInflu:
            temp.append('%s' % influ.name())
        print("%s" % temp).replace(", u'", ", '").replace('[u', "[")
    else:
        return skinInflu
