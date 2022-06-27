################# paper shading ##################
import pymel.core as pm
import mgear.maya.shifter as ms
import mgear.maya.skin as mSkin
import maya.cmds as cmds
import os
import PIL


class Draw:
    def __init__(self, draw_name='', textures=[], ratio=0, highDir='', lowDir='', layered_texture=0, rig_group=0):
        self.draw_name = draw_name
        self.textures = textures
        self.ratio = ratio
        self.highDir = highDir
        self.lowDir = lowDir


def createFileTexture(fileTextureName, p2dName=''):
    tex = pm.shadingNode('file', name=fileTextureName, asTexture=True, isColorManaged=True)
    if not pm.objExists(p2dName):
        pm.shadingNode('place2dTexture', name=p2dName, asUtility=True)
    p2d = pm.PyNode(p2dName)
    tex.filterType.set(0)
    pm.connectAttr(p2d.outUV, tex.uvCoord)
    pm.connectAttr(p2d.outUvFilterSize, tex.uvFilterSize)
    pm.connectAttr(p2d.vertexCameraOne, tex.vertexCameraOne)
    pm.connectAttr(p2d.vertexUvOne, tex.vertexUvOne)
    pm.connectAttr(p2d.vertexUvThree, tex.vertexUvThree)
    pm.connectAttr(p2d.vertexUvTwo, tex.vertexUvTwo)
    pm.connectAttr(p2d.coverage, tex.coverage)
    pm.connectAttr(p2d.mirrorU, tex.mirrorU)
    pm.connectAttr(p2d.mirrorV, tex.mirrorV)
    pm.connectAttr(p2d.noiseUV, tex.noiseUV)
    pm.connectAttr(p2d.offset, tex.offset)
    pm.connectAttr(p2d.repeatUV, tex.repeatUV)
    pm.connectAttr(p2d.rotateFrame, tex.rotateFrame)
    pm.connectAttr(p2d.rotateUV, tex.rotateUV)
    pm.connectAttr(p2d.stagger, tex.stagger)
    pm.connectAttr(p2d.translateFrame, tex.translateFrame)
    pm.connectAttr(p2d.wrapU, tex.wrapU)
    pm.connectAttr(p2d.wrapV, tex.wrapV)
    return tex


### find folders with drawings

props_dir = 'P:/MBA_SE02/assets/props/'
maps_conventions = "/maps/drawings/"
high = "/"
low = "/low/"
props_folders = os.listdir(props_dir)
drawing_props = []

for prop_folder in props_folders:
    if os.path.exists(props_dir + prop_folder + maps_conventions):
        drawing_props.append(prop_folder)

### check a specific draw

# prop selection
drawing_prop = drawing_props[0]
draws_folders = os.listdir(props_dir + drawing_prop + maps_conventions)
# draw selection
drawings = []
for draw_folder in draws_folders:
    highDir = props_dir + drawing_prop + maps_conventions + draw_folder + high
    lowDir = props_dir + drawing_prop + maps_conventions + draw_folder + low
    try:
        os.makedirs(lowDir)
    except:
        pass
    draw_high_content = os.listdir(highDir)
    draw_low_content = os.listdir(lowDir)

    draw_high_jpgs = []
    ratio = 0
    for obj in draw_high_content:
        if obj.endswith(".jpg"):
            draw_high_jpgs.append(obj)
            image_inst = PIL.Image.open(highDir + obj)
            width, height = image_inst.size
            ratio = float('%.3f' % (float(width) / float(height)))
            if obj not in draw_low_content:
                lowResSize = width / 2, height / 2
                im_resized = image_inst.resize(lowResSize, PIL.Image.ANTIALIAS)
                im_resized.save(lowDir + obj)
            image_inst.close()
    drawings.append(Draw(draw_name=draw_folder, textures=draw_high_jpgs, ratio=ratio, highDir=highDir, lowDir=lowDir))

# todo: if 2 draws in the same folder but not the same ratio, raise warning

### create shading

pm.group(em=True, n='high_grp')
pm.group('high_grp', n='main')


texture_index=0
for draw in drawings:
    cmds.file("P:/MBA_SE02/scripts/rigging/amit/paper/tmp/paper_shading.ma", i=True, typ="mayaAscii", ignoreVersion=True)
    pm.parent('paper_high', 'high_grp')
    paper = pm.PyNode('paper_high')
    vray_multi = pm.PyNode('paper_VRayMultiSubTex')
    paper.sx.set(draw.ratio)
    pm.makeIdentity(paper, a=True)
    pm.delete(paper, ch=True)

    for i, texture in enumerate(draw.textures):
        fileName = draw.draw_name + "_texture" + str(i + 1).zfill(2)
        fileInst = createFileTexture(fileTextureName=fileName + "_file", p2dName=fileName + "_p2d")
        pm.setAttr(fileInst.fileTextureName, draw.highDir + texture)
        fileInst.outColor >> vray_multi.subTexList[texture_index].subTexListTex
        vray_multi.subTexList[texture_index].subTexListID.set(texture_index)
        texture_index+=1

    # remane
    paper.rename(draw.draw_name + '_high')
    vray_multi.rename('paper_VRayMultiSubTex_' + draw.draw_name)
    draw.layered_texture = vray_multi



# add switcher

enumVars = []
for draw in drawings:
    for texture in draw.textures:
        enumVars.append(texture.split(".")[0])
enumString = enumVars[0]
for i in range(1, len(enumVars)):
    enumString += ":%s" % enumVars[i]
attrName = "c_draw"
obj = "high_grp"
pm.addAttr(obj, ln=attrName, at="enum", enumName=enumString)
pm.setAttr(obj + "." + attrName, keyable=True)

high_grp = pm.PyNode('high_grp')
for draw in drawings:
    high_grp.c_draw >> draw.layered_texture.idGenTex