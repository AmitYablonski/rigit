from maya import cmds, mel
import pymel.core as pm
from functools import partial
import CrvFromSelection

reload(CrvFromSelection)


class CurveRigTool:

    def __init__(self):

        self.widgets = {}
        self.crv = ''
        self.topCrv = ''
        self.lowCrv = ''
        self.curveRigWin()

    def curveRigWin(self):
        if cmds.window("curveRig_window", exists=True):
            cmds.deleteUI("curveRig_window")
        self.widgets["curveRig_window"] = cmds.window("curveRig_window", title="Curve Rigging Toolbox", sizeable=1,
                                                      rtf=True)
        self.widgets["mainLayout"] = cmds.rowColumnLayout(nc=1)
        parent1 = self.widgets["mainLayout"]
        bgc = [.1, .2, .1]
        bgc2 = [.2, .1, .2]
        h = 5
        variousLayout = self.addSeparatorAndFrame(parent1, h, bgc2, bgc, label="Various curve tools")
        vtxLayout = self.addSeparatorAndFrame(parent1, h, bgc2, bgc, label="Create a curve from vertex selection")
        lipsLayout = self.addSeparatorAndFrame(parent1, h, bgc2, bgc, label="Lips Rig builder")
        self.addSeparatorAndFrame(parent1, h, bgc2)

        # populate layouts
        CrvFromSelection.CrvFromSelection(False, vtxLayout)
        self.crvToolsPop(variousLayout)
        # todo select/create upper and lower curves
        self.lipsSetupLayout(lipsLayout)

        cmds.separator(h=7, p=self.widgets["mainLayout"])
        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False,
                                                           p=self.widgets["mainLayout"])
        self.defaultFeedback()
        cmds.showWindow()

    def addSeparatorAndFrame(self, parent1, h, bgc2, bgc=[], label=''):
        cmds.separator(h=h + 10, p=parent1)
        cmds.separator(h=h, p=parent1, bgc=bgc2)
        if label:
            return cmds.frameLayout(label=label, collapsable=True, p=parent1, bgc=bgc)

    def crvToolsPop(self, parent1=''):
        if not parent1:
            return "can't load crvToolsPop"
        # todo populate this area of the tool with common curve tools
        cmds.separator(h=12, p=parent1)
        topLay = cmds.rowColumnLayout(nc=4, p=parent1)
        cmds.separator(w=30)  # , vis=False)
        cmds.rowColumnLayout(nc=1)
        self.widgets["polyToCrv_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=2, select=2,  # cw2=[100, 100],
                                                              labelArray2=['Linear', 'Cubic'])
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1)
        cmds.button(l='polyToCurve', c=self.runPolyToCurve)
        cmds.button(l='Opt.', c='mel.eval("CreateCurveFromPolyOptions;")')
        cmds.separator(w=30, p=topLay)  # , vis=False)
        crvToolsLay = cmds.rowColumnLayout(nc=4, p=topLay, cs=[[1, 3], [2, 3], [3, 3], [4, 3]])
        cmds.iconTextButton(style='iconAndTextVertical', l='Detach', c='mel.eval("DetachCurve")', #Options
                            ann="Detach Curve: Select curve parameter point(s)", image1='detachCurve.png')
        cmds.iconTextButton(style='iconAndTextVertical', l='Offset', c='mel.eval("OffsetCurveOptions")',
                            image1='offsetCurve.png',
                            ann="Offset Curve Options: Select curve, curve on surface, isoparm or trim edge")
        cmds.iconTextButton(style='iconAndTextVertical', l='Rebuild', c='mel.eval("RebuildCurveOptions;")',
                            image1='rebuildCurve.png')
        cmds.iconTextButton(style='iconAndTextVertical', l='Edit', c='mel.eval("CurveEditTool")',
                            image1='curveEditor.png', ann="Curve Edit Tool: Select curve/crv point or curve on surface")

        # cmds.button()
        # cmds.button()
        # cmds.button()

    def lipsSetupLayout(self, parent1='None'):
        if parent1 == 'None':
            return "Can't load lipsSetupLayout for CurveRigTool"
        lipsLayout = cmds.rowColumnLayout('Lips setup', nc=1, p=parent1)
        cmds.separator(h=3)
        cmds.text(l='Note - must name curves with "_crv" suffix')
        cmds.separator(h=3)
        # objects selection
        cmds.rowColumnLayout(nc=2, cs=[2, 5])
        cmds.button(l='Select upper lip curve', c=partial(self.updateTextField, 'topCrv'))
        self.widgets['topCrv'] = cmds.textField(w=300, tcc=partial(self.updateObject, 'topCrv'))
        cmds.button(l='Select lower lip curve', c=partial(self.updateTextField, 'lowCrv'))
        self.widgets['lowCrv'] = cmds.textField(w=300, tcc=partial(self.updateObject, 'lowCrv'))
        cmds.separator(h=3, p=lipsLayout)
        self.widgets["jntAmt"] = cmds.intSliderGrp(l="Number of Joints:", field=True, min=0, max=20, v=11,
                                                   fieldMinValue=0, fieldMaxValue=100, cw=[2, 40], p=lipsLayout)
        autoBgc = [.215, .215, .215]
        axisLayout = cmds.rowColumnLayout(nc=3, p=lipsLayout)
        cmds.separator(w=20, bgc=autoBgc)
        cmds.text('*Auto up is recommended*', al='left', bgc=autoBgc)
        self.widgets['leftAxis'] = cmds.optionMenu(label='  Left side axis:')  # , cc=self.leftAxisChanged)
        for ax in 'XYZ':
            cmds.menuItem(label='   %s ' % ax)
            cmds.menuItem(label=' - %s ' % ax)
        cmds.optionMenu(self.widgets['leftAxis'], edit=True, sl=1)
        # up vector
        # cmds.separator(w=110, vis=False, p=axisLayout)
        cmds.separator(bgc=autoBgc)
        self.widgets['autoUpVector'] = cmds.checkBox(l='Auto select up vector', w=150, p=axisLayout, v=1,
                                                     cc=self.autoSelectUpVector, bgc=autoBgc)
        self.widgets['upAxis'] = cmds.optionMenu(label='      Up Vector:', p=axisLayout)  # , cc=self.upVectorChanged
        for ax in 'XYZ':
            cmds.menuItem(label='   %s ' % ax)
            cmds.menuItem(label=' - %s ' % ax)
        cmds.optionMenu(self.widgets['upAxis'], edit=True, sl=3)

        cmds.separator(h=7, p=lipsLayout)
        cmds.button(l='Execute', p=lipsLayout, c=self.executeLips)
        cmds.separator(h=3, p=lipsLayout)
        self.autoSelectUpVector()

    def autoSelectUpVector(self, *args):
        if cmds.checkBox(self.widgets['autoUpVector'], q=True, v=True):
            cmds.optionMenu(self.widgets['upAxis'], e=True, enable=False)
        else:
            cmds.optionMenu(self.widgets['upAxis'], e=True, enable=True)

    def runPolyToCurve(self, *args):
        degRadio = cmds.radioButtonGrp(self.widgets["polyToCrv_radio"], q=True, select=True)
        degree = 1
        if degRadio == 2:
            degree = 3
        pm.polyToCurve(form=2, degree=degree, conformToSmoothMeshPreview=1)

    def updateTextField(self, field='', *args):
        self.defaultFeedback()
        if not field:
            return
        selection = pm.ls(sl=True)
        if len(selection) == 1:
            sel = selection[0]
            if not self.isObjCurve(sel):
                return
            if field == 'topCrv':
                self.topCrv = sel
            if field == 'lowCrv':
                self.lowCrv = sel
            cmds.textField(self.widgets[field], e=True, tx=sel.name())
            pm.select(selection)
            return
        self.changeFeedback('Please select a single curve and try again', 'red')
        return

    def updateObject(self, field='', *args):
        self.defaultFeedback()
        if not field:
            return
        tx = cmds.textField(self.widgets[field], q=True, tx=True)
        if field == 'topCrv':
            self.topCrv = tx
        if field == 'lowCrv':
            self.lowCrv = tx
        if not pm.objExists(tx):
            self.changeFeedback("Can't find given name '%s' in scene" % tx, 'red')
        if not self.isObjCurve(pm.PyNode(tx)):
            self.changeFeedback("Selected name '%s' isn't a curve" % tx, 'red')

    def isObjCurve(self, obj):
        self.defaultFeedback()
        if obj.type() != 'nurbsCurve':
            return True
        else:
            if obj.type() != 'transform':
                print 'testing %s' % obj
                shps = obj.listRelatives(s=True)
                if not shps:
                    self.changeFeedback("Seems like the selected object isn't a curve", 'red')
                    return False
                if shps[0].type() == 'nurbsCurve':
                    return True
        return False

    def delParCns(self, obj1, obj2):
        pm.delete(pm.pointConstraint(obj1, obj2))

    def getCurveSettings(self):
        upr_pref = cmds.textField(self.widgets['topCrv'], q=True, tx=True)
        lwr_pref = cmds.textField(self.widgets['lowCrv'], q=True, tx=True)
        jntsAmount = cmds.intSliderGrp(self.widgets["jntAmt"], q=True, v=True)
        leftAxisOp = cmds.optionMenu(self.widgets['leftAxis'], q=True, sl=True)
        leftAxis = 0  # X
        if leftAxisOp > 4:  # Z
            leftAxis = 2
        elif leftAxisOp > 2:  # Y
            leftAxis = 1

        if leftAxisOp % 2:
            leftPositive = 1
        else:
            leftPositive = -1
        return upr_pref, lwr_pref, leftAxis, leftPositive, jntsAmount

    def executeLips(self, *args):
        # todo make sure this line works:
        upr_pref, lwr_pref, leftAxis, leftPositive, jntsAmount = self.getCurveSettings()
        self.lipsRigOnCrvs(upr_pref, lwr_pref, leftAxis, leftPositive, jntsAmount)

    def attach_joints_to_crv(self, jntsAmount, crv, pref, needFlip):
        jnts_grp = pm.group(n=pref + "_jnts_grp", em=True)
        acc = 0  # todo <- check what to do with this
        # todo test if jnts will get build in the correct order
        rangeList = []
        for i in range(1, jntsAmount + 1):
            rangeList.append(i)
        if needFlip:
            temp = []
            for i in reversed(rangeList):
                temp.append(i)
            rangeList = temp
        for i in rangeList:
            '''
            if needFlip:
                for i in range(0, jntAmt + 1):
                    i = float(i)
                    if not i:
                        print jntAmt
                    elif i == jntAmt:
                        print 0
                    else:
                        val = (1-(i/jntAmt))*jntAmt
                        print val
                    print ''
            '''
            jnt = pm.joint(n=pref + '_%s_jnt' % i)
            pm.parent(jnt, jnts_grp)
            mPath = pm.createNode("motionPath", n=pref + "_%s_jnt_mPath" % i)
            pm.connectAttr(crv + ".worldSpace[0]", mPath.geometryPath)
            for axis in "xyz":
                attr = "r" + axis
                pm.connectAttr(mPath.attr(attr), jnt.attr(attr))
                pm.connectAttr(mPath + "." + axis + "Coordinate", jnt + ".t" + axis)
                pm.setAttr(mPath.uValue, acc)
                pm.setAttr(mPath.fractionMode, 1)
                pm.setAttr(mPath.follow, 0)
            acc += 1 / float(jntsAmount - 1)
        return jnts_grp

    def curveFlipTester(self, jntsAmount, crv, leftAxis, leftPositive, upVector=False):
        retrunVar = False
        jnts_grp = pm.group(n="temp_curveTester_grp", em=True)
        acc = 0
        jntsList = []
        for i in range(1, jntsAmount + 1):
            jnt = pm.joint(n='temp_curveTester_%s_jnt' % i)
            jntsList.append(jnt)
            pm.parent(jnt, jnts_grp)
            mPath = pm.createNode("motionPath", n="temp_curveTester_%s_jnt_mPath" % i)
            pm.connectAttr(crv + ".worldSpace[0]", mPath.geometryPath)
            for axis in "xyz":
                attr = "r" + axis
                pm.connectAttr(mPath.attr(attr), jnt.attr(attr))
                pm.connectAttr(mPath + "." + axis + "Coordinate", jnt + ".t" + axis)
                pm.setAttr(mPath.uValue, acc)
                pm.setAttr(mPath.fractionMode, 1)
                pm.setAttr(mPath.follow, 0)
            acc += 1 / float(jntsAmount - 1)
        pos1 = pm.xform(jntsList[0], query=True, t=True, ws=True)
        pos2 = pm.xform(jntsList[len(jntsList) - 1], query=True, t=True, ws=True)
        if upVector:
            midPos = int(len(jntsList) * .5)
            posMid = pm.xform(jntsList[midPos], query=True, t=True, ws=True)
            # setup
            testGrp = pm.group(n='upV_testGrp', em=True, p=jnts_grp)  # , w=True)
            aim = pm.group(n='aim_testGrp', em=True, p=testGrp)
            target = pm.group(n='target_testGrp', em=True, p=testGrp)
            posMidGrp = pm.group(n='posMid_testGrp', em=True, p=testGrp)
            pm.xform(aim, t=pos1, ws=True)
            pm.xform(target, t=pos2, ws=True)
            pm.xform(posMidGrp, t=posMid, ws=True)
            # up setup
            upVecPar = pm.group(n='upV_parent_testGrp', em=True, w=True)
            upVecPos = pm.group(n='upV_position_testGrp', em=True, p=upVecPar)
            upVecPos.ty.set(25)
            pm.parent(upVecPar, aim)
            # position and calculate
            aimCns = pm.aimConstraint(target, aim, worldUpObject=posMidGrp, worldUpType="object",
                                      aimVector=[1, 0, 0], upVector=[0, 0, 1])
            pm.delete(pm.pointConstraint(aim, target, upVecPar))
            upPar = pm.xform(upVecPar, query=True, t=True, ws=True)
            upPos = pm.xform(upVecPos, query=True, t=True, ws=True)
            upV = []
            for i in range(0, 3):
                upV.append(upPos[i] - upPar[i])
            retrunVar = upPos
        else:
            if leftPositive == 1:
                if pos1[leftAxis] < pos2[leftAxis]:  # Needs Flipping
                    retrunVar = True
            else:
                if pos1[leftAxis] > pos2[leftAxis]:  # Needs Flipping
                    retrunVar = True
        pm.delete(jnts_grp)
        return retrunVar

    # lips setup maker
    def lipsRigOnCrvs(self, upr_crv, lwr_crv, leftAxis, leftPositive, jntsAmount=11, *args):
        # todo keep testing this. not working yet
        # todo test with different names
        upr_pref = upr_crv.rpartition('_crv')[0]
        lwr_pref = lwr_crv.rpartition('_crv')[0]
        print 'leftPositive: %s' % leftPositive
        print 'leftAxis: %s' % leftAxis
        setupGrp = pm.group(n="lips_setup", em=True)
        grpCtls = pm.group(n="lips_setup_ctl_grp", em=True)
        grpCrvs = pm.group(n="lips_setup_crv_grp", em=True)
        grpJnts = pm.group(n="lips_setup_jnt_grp", em=True)
        pm.parent(grpCtls, grpCrvs, grpJnts, setupGrp)

        for pref in [upr_pref, lwr_pref]:
            crv = pref + "_crv"

            upN = pm.duplicate(crv, n=pref + "_upN")[0]
            # if leftPositive == 1:
            autoUp = cmds.checkBox(self.widgets['autoUpVector'], q=True, v=True)
            if autoUp:
                upVector = self.curveFlipTester(jntsAmount, crv, leftAxis, leftPositive, True)
            else:
                upOp = cmds.optionMenu(self.widgets['upAxis'], q=True, sl=True)
                upVector = [0, 0, 0]
                idx = 0  # X
                if upOp > 4:  # Z
                    idx = 2
                elif upOp > 2:  # Y
                    idx = 1
                positive = 1
                if not upOp % 2:
                    positive = -1
                upVector[idx] = 25 * positive
            if autoUp:
                pm.xform(upN, t=upVector, ws=True)
            else:
                upN.t.set(upVector)
            # was previously: upN.ty.set(25)
            pm.parent(crv, upN, grpCrvs)

            # check if curve will get built in the correct order
            needFlip = self.curveFlipTester(jntsAmount, crv, leftAxis, leftPositive)

            grp = self.attach_joints_to_crv(jntsAmount, crv, pref, needFlip)
            pm.parent(grp, grpJnts)
            grp = self.attach_joints_to_crv(jntsAmount, upN, upN, needFlip)
            pm.parent(grp, grpJnts)

            grp = self.attach_joints_to_crv(5, crv, "temp_" + pref, needFlip)
            pm.parent(grp, grpJnts)

            for i in range(1, jntsAmount + 1):
                pm.connectAttr(pref + "_upN_%s_jnt.worldMatrix[0]" % i, pref + "_%s_jnt_mPath.worldUpMatrix" % i)

        pm.select(cl=1)
        print 'after jnts part'

        names = ["echo_MouthCorner_L0", "echo_MouthSneer_L0", "echo_MouthSneer_L1", "echo_MouthUpperMid_C0",
                 "echo_MouthLowerMid_C0", "echo_MouthCorner_R0", "echo_MouthSneer_R0", "echo_MouthSneer_R1"]

        for name in names:
            npo = pm.group(n=name + "_ctl_npo", em=True)
            ctl = pm.circle(n=name + "_ctl")[0]
            jnt = pm.joint(n=name + "_jnt")
            pm.parent(jnt, ctl)
            pm.parent(ctl, npo)
            pm.parent(npo, grpCtls)
            if "_R" in name:
                pm.setAttr(npo.ry, 180)
                pm.setAttr(npo.sz, -1)
        print 'after circle part'

        # todo make this work with any jnt amt and not be name specific like now
        # L
        self.delParCns(["temp_upperLip_1_jnt", "temp_lowerLip_1_jnt"], "echo_MouthCorner_L0_ctl_npo")

        self.delParCns("temp_upperLip_2_jnt", "echo_MouthSneer_L0_ctl_npo")
        self.delParCns("temp_lowerLip_2_jnt", "echo_MouthSneer_L1_ctl_npo")

        # R
        self.delParCns(["temp_upperLip_5_jnt", "temp_lowerLip_5_jnt"], "echo_MouthCorner_R0_ctl_npo")

        self.delParCns("temp_upperLip_4_jnt", "echo_MouthSneer_R0_ctl_npo")
        self.delParCns("temp_lowerLip_4_jnt", "echo_MouthSneer_R1_ctl_npo")

        # C
        self.delParCns("temp_upperLip_3_jnt", "echo_MouthUpperMid_C0_ctl_npo")
        self.delParCns("temp_lowerLip_3_jnt", "echo_MouthLowerMid_C0_ctl_npo")

        # delete motion path
        pm.delete("temp_" + upr_pref + "_jnts_grp")
        pm.delete("temp_" + lwr_pref + "_jnts_grp")

        pm.skinCluster("echo_MouthCorner_L0_jnt", "echo_MouthCorner_R0_jnt", "echo_MouthSneer_L1_jnt",
                       "echo_MouthSneer_R1_jnt", "echo_MouthLowerMid_C0_jnt", lwr_crv, n=lwr_crv + "_skinCluster")
        pm.skinCluster("echo_MouthCorner_L0_jnt", "echo_MouthCorner_R0_jnt", "echo_MouthSneer_L0_jnt",
                       "echo_MouthSneer_R0_jnt", "echo_MouthUpperMid_C0_jnt", upr_crv, n=upr_crv + "_skinCluster")

        pm.parent(pm.joint(p=(0, 0, 0), n="lips_setup_static_jnt"), grpJnts)
        self.changeFeedback(' // Lips Rig Built', 'green')

    def curveRig(self, *args):
        return

    def defaultFeedback(self):
        self.changeFeedback("Curves rigging toolbox")

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.7, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)
