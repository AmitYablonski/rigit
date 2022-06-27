import pymel.core as pm
# import mgear.maya.shifter as ms
# import mgear.maya.skin as mSkin
import maya.cmds as cmds
import os
# import PIL


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

#############################################################################

### find folders with drawings
class Paper:
    def __init__(self):
        self.props_dir = 'P:/MBA_SE02/assets/props/'
        self.maps_conventions = "/maps/drawings/"
        self.high = "/"
        self.low = "/low/"
        self.drawings = []
        self.highDir = ''
        self.lowDir = ''
        self.low_res_factor =2
        self.draw_high_content = []
        self.drawing_prop = ''

    def getDrawingsProps(self):
        props_folders = os.listdir(self.props_dir)
        drawing_props = []
        for prop_folder in props_folders:
            if os.path.exists(self.props_dir + prop_folder + self.maps_conventions):
                drawing_props.append(prop_folder)
        return drawing_props

    def make_low(self, obj):
        image_inst = PIL.Image.open(self.highDir + obj)
        width, height = image_inst.size
        ratio = float('%.3f' % (float(width) / float(height)))
        # if obj not in draw_low_content:
        lowResSize = width / self.low_res_factor, height / self.low_res_factor
        im_resized = image_inst.resize(lowResSize, PIL.Image.ANTIALIAS)
        im_resized.save(self.lowDir + obj)
        image_inst.close()
        return ratio

    def get_drawings(self):
        self.drawings = []
        draws_folders = os.listdir(self.props_dir + self.drawing_prop + self.maps_conventions)
        for draw_folder in draws_folders:
            self.highDir = self.props_dir + self.drawing_prop + self.maps_conventions + draw_folder + self.high
            self.lowDir = self.props_dir + self.drawing_prop + self.maps_conventions + draw_folder + self.low
            try:
                os.makedirs(self.lowDir)
            except:
                pass
            self.draw_high_content = os.listdir(self.highDir)
            # draw_low_content = os.listdir(self.lowDir)

            draw_high_jpgs = []
            ratio = 0
            for obj in self.draw_high_content:
                # print obj
                if obj.endswith(".jpg") or obj.endswith(".png"):
                    ratio = self.make_low(obj)
                    draw_high_jpgs.append(obj)
            self.drawings.append(
                Draw(draw_name=draw_folder, textures=draw_high_jpgs, ratio=ratio, highDir=self.highDir, lowDir=self.lowDir))

        # todo: if 2 draws in the same folder but not the same ratio, raise warning

    def create_rig(self, drawing_prop):
        self.drawing_prop = drawing_prop
        self.get_drawings()

        paper_rig = 0
        index = 1

        for draw in self.drawings:

            cmds.file("P:/MBA_SE02/scripts/rigging/amit/paper/tmp/paper_model.ma", i=True, typ="mayaAscii", ignoreVersion=True)
            cmds.file("P:/MBA_SE02/scripts/rigging/amit/paper/tmp/paper_guide.ma", i=True, typ="mayaAscii", ignoreVersion=True)

            paper = pm.PyNode('paper_high')
            guide = pm.PyNode('guide')

            paper.sx.set(draw.ratio)
            guide.sx.set(draw.ratio)

            pm.makeIdentity(paper, a=True)
            pm.delete(paper, ch=True)

            guide.select()
            ms.Rig().buildFromSelection()
            pm.delete('guide')

            mSkin.importSkin("P://MBA_SE02//assets//props//paper_301A//rigging//paper_301A//gSkin//paper.gSkin")
            pm.setAttr("rig.jnt_vis", 0)

            for i, texture in enumerate(draw.textures):
                fileName = draw.draw_name + "_texture" + str(i + 1).zfill(2)
                fileInst = createFileTexture(fileTextureName=fileName + "_file", p2dName=fileName + "_p2d")
                pm.setAttr(fileInst.fileTextureName, draw.lowDir + texture)
                pm.connectAttr(fileInst.outColor, "paper_layeredTexture.inputs[" + str(i) + "].color")

            # remane
            paper.rename(draw.draw_name + '_high')
            draw.layered_texture = pm.rename('paper_layeredTexture', 'paper_layeredTexture_' + draw.draw_name)

            if not paper_rig:
                rig = pm.PyNode('rig')
                rig.rename('paper_rig')
                paper_rig = rig
                rig_set = pm.PyNode('rig_sets_grp')
                rig_set.rename('paper_rig_sets_grp')
                pm.group(paper, n="high_grp")
                pm.group("high_grp", rig, n="main")
                local = pm.PyNode('local_C0_ctl')
                jnt_org = pm.PyNode('jnt_org')
                jnt_org.rename('paper_jnt_org')
            else:
                pm.parent(paper, "high_grp")
                pm.parent('chainSpring_C0_root', local)
                pm.parent('chainSpringUI_C0_root', local)
                pm.parent('chainSpring_C0_jnt_org', jnt_org)
                # todo do something with rig set
                # connect spring
                pm.delete('rig')
            draw.rig_group = pm.group('chainSpring_C0_root', 'chainSpringUI_C0_root', n="draw_" + str(index) + "_grp")
            chainSpring = pm.ls('chainSpring*_C0*')
            if chainSpring:
                for item in chainSpring:
                    item.rename(item.name().replace('C0', 'C' + str(index)))
                index += 1

        # add switcher
        enumVars = []
        for draw in self.drawings:
            for texture in draw.textures:
                enumVars.append(texture.split(".")[0])
        enumString = enumVars[0]

        for i in range(1, len(enumVars)):
            enumString += ":%s" % enumVars[i]

        attrName = "draw"
        obj = "global_C0_ctl"
        pm.addAttr(obj, ln=attrName, at="enum", enumName=enumString)
        pm.setAttr(obj + "." + attrName, keyable=True)

        attrName = "c_draw"
        obj = "high_grp"
        pm.addAttr(obj, ln=attrName, at="enum", enumName=enumString)
        pm.setAttr(obj + "." + attrName, keyable=True)

        pm.connectAttr('global_C0_ctl.draw', 'high_grp.c_draw')

        global_texture_index = 0
        i = 0
        high_grp = pm.PyNode('high_grp')
        for draw in self.drawings:
            if len(self.drawings) > 1:
                min_index = i
                max_index = i + len(draw.textures) - 1
                min_cond = pm.shadingNode('floatLogic', asUtility=True, name=draw.draw_name + "_min_floatLogic")
                max_cond = pm.shadingNode('floatLogic', asUtility=True, name=draw.draw_name + "_max_floatLogic")
                float_math = pm.shadingNode('floatMath', asUtility=True, name=draw.draw_name + "_floatMath")
                min_cond.floatB.set(min_index)
                min_cond.operation.set(5)
                max_cond.floatB.set(max_index)
                max_cond.operation.set(4)
                high_grp.c_draw >> min_cond.floatA
                high_grp.c_draw >> max_cond.floatA
                min_cond.outBool >> float_math.floatA
                max_cond.outBool >> float_math.floatB
                float_math.operation.set(2)
                float_math.outFloat >> draw.rig_group.v
                float_math.outFloat >> draw.draw_name + "_high.v"
                i = max_index + 1
            local_texture_index = 0
            for texture in draw.textures:
                tex_cond = pm.shadingNode('floatLogic', asUtility=True, name=texture.split('.')[0] + "_floatLogic")
                high_grp.c_draw >> tex_cond.floatA
                tex_cond.floatB.set(global_texture_index)
                pm.connectAttr(tex_cond.outBool,
                               draw.layered_texture.name() + '.inputs[' + str(local_texture_index) + '].alpha')
                local_texture_index += 1
                global_texture_index += 1

    def create_shading(self, drawing_prop):
        self.drawing_prop = drawing_prop
        self.get_drawings()

        pm.group(em=True, n='high_grp')
        pm.group('high_grp', n='main')

        texture_index = 0
        for draw in self.drawings:
            cmds.file("P:/MBA_SE02/scripts/rigging/amit/paper/tmp/paper_shading.ma", i=True, typ="mayaAscii",
                      ignoreVersion=True)
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
                texture_index += 1

            # remane
            paper.rename(draw.draw_name + '_high')
            vray_multi.rename('paper_VRayMultiSubTex_' + draw.draw_name)
            draw.layered_texture = vray_multi

        # add switcher

        enumVars = []
        for draw in self.drawings:
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
        for draw in self.drawings:
            high_grp.c_draw >> draw.layered_texture.idGenTex