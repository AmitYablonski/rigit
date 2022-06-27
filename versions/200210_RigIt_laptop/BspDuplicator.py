from maya import cmds, mel
import pymel.core as pm
from functools import partial
import generalMayaTools as gmt


class BspDuplicator:

    def __init__(self):

        self.winWidth = 350
        self.obj = ''
        self.newObj = ''
        self.bsp = ''
        self.rename = ''
        self.lastMirrorOp = 1
        self.widgets = {}
        self.bspDupWin()

    def bspDupWin(self):
        if cmds.window("bspDup_window", exists=True):
            cmds.deleteUI("bspDup_window")
        self.widgets["bspDup_window"] = cmds.window("bspDup_window", title="Bsp Duplicator", sizeable=1, rtf=True)
        self.widgets["bspDup_main_Layout"] = cmds.rowColumnLayout(numberOfColumns=1)#, w=self.winWidth)

        cmds.text('  Currently only works with all blend shape targets in scene.',
                  al='left')
        cmds.text('Please rebuild targets if necessary.',
                  al='center')
        cmds.separator(h=7)#, w=self.winWidth)

        self.widgets["bspDup_geo_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=2, cw2=[100, 100], select=1,
                                                               labelArray2=['New Geo', 'Same Geo'],
                                                               cc=partial(self.geoRadioUpdate, False))
        self.widgets["bspDup_mirror_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=3, cw3=[100, 100, 100],
                                                                  labelArray3=['Duplicate', 'Mirror', 'both'],
                                                                  select=self.lastMirrorOp,
                                                                  cc=partial(self.geoRadioUpdate, True))

        # objects selection
        self.widgets["object_Layout"] = cmds.rowColumnLayout(nc=2, cs=[2, 5],  # rs=[2, 2], # bgc=self.darkGreen,
                                                             p=self.widgets["bspDup_main_Layout"])
        cmds.button(l='Select object with bsp', c=partial(self.updateTextField, 'obj'))
        self.widgets['obj'] = cmds.textField(w=300, tcc=partial(self.updateObject, 'obj'))
        cmds.button(l='Select blend shape', c=partial(self.updateTextField, 'bsp'))
        self.widgets['bsp'] = cmds.textField(w=300, tcc=partial(self.updateObject, 'bsp'))
        self.widgets['newObjButton'] = cmds.button(l='Select new object', c=partial(self.updateTextField, 'newObj'))
        self.widgets['newObj'] = cmds.textField(w=300, tcc=partial(self.updateObject, 'newObj'))

        # rename
        self.widgets["rename_topLayout"] = cmds.rowColumnLayout(numberOfColumns=1,
                                                             p=self.widgets["bspDup_main_Layout"])
        cmds.separator(h=7, p=self.widgets["bspDup_main_Layout"])
        self.widgets["rename"] = cmds.checkBox(l="Rename duplicated Mirror", v=True,
                                               cc=self.renameCheck)
        self.widgets["rename_Layout"] = cmds.rowColumnLayout(nc=2, cs=[2, 5])
        cmds.text(l=' Name to replace :')
        self.widgets['renameSearch'] = cmds.textField(text='_L_', w=250)
        cmds.text(l=' Replace with :')
        self.widgets['renameReplace'] = cmds.textField(text='_R_')

        # execute
        cmds.separator(h=7, p=self.widgets["bspDup_main_Layout"])
        cmds.button(l="execute", c=self.executeBspDup, p=self.widgets["bspDup_main_Layout"])

        cmds.separator(h=7, p=self.widgets["bspDup_main_Layout"])
        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False,
                                                           p=self.widgets["bspDup_main_Layout"])
        self.geoRadioUpdate(False)
        self.geoRadioUpdate(True)
        self.renameCheck()
        self.defaultFeedback()

        cmds.showWindow()

    def renameCheck(self, *args):
        status = cmds.checkBox(self.widgets["rename"], q=True, v=True)
        cmds.rowColumnLayout(self.widgets["rename_Layout"], e=True, en=status)
        self.rename = status

    def geoRadioUpdate(self, mirrorChange, *args):
        self.defaultFeedback()
        sameGeo = 1 - (cmds.radioButtonGrp(self.widgets["bspDup_geo_radio"], q=True, select=True) - 1)
        mirror = cmds.radioButtonGrp(self.widgets["bspDup_mirror_radio"], q=True, select=True)
        if mirrorChange:
            self.lastMirrorOp = mirror
        # show/hide newObj
        cmds.button(self.widgets['newObjButton'], e=True, en=sameGeo)
        cmds.textField(self.widgets['newObj'], e=True, en=sameGeo)
        if 1-sameGeo:
            #cmds.radioButtonGrp(self.widgets["bspDup_mirror_radio"], e=True, select=1)
            cmds.radioButtonGrp(self.widgets["bspDup_mirror_radio"], e=True, select=2, en=False)
        else:
            cmds.radioButtonGrp(self.widgets["bspDup_mirror_radio"], e=True, select=self.lastMirrorOp, en=True)
        # dis/enable mirroring rename options
        if mirror > 1:
            cmds.rowColumnLayout(self.widgets["rename_topLayout"], e=True, en=True)
        else:
            cmds.rowColumnLayout(self.widgets["rename_topLayout"], e=True, en=False)

    def executeBspDup(self, *args):
        self.defaultFeedback()
        sameGeo = cmds.radioButtonGrp(self.widgets["bspDup_geo_radio"], q=True, select=True)-1
        mirror = cmds.radioButtonGrp(self.widgets["bspDup_mirror_radio"], q=True, select=True)
        # check if object is selected
        if not self.obj:
            self.changeFeedback('Please select geometry with blend shape', 'red')
            return
        # check if new object is selected/needed
        if not sameGeo and not self.newObj:
            self.changeFeedback('Please select the new geometry', 'red')
            return
        # check if blend shape node is found
        if not self.bsp:
            self.changeFeedback('Please add the blend shape node', 'red')
            return
        targets = self.getBspShapes(self.obj, self.bsp)
        if not targets:
            self.changeFeedback('No Targets were found for %s' % self.bsp, 'red')
            return

        # execute
        if sameGeo:
            self.bspDupIt(self.obj, targets, self.newObj, True)
        else:
            if mirror == 3:
                self.bspDupIt(self.obj, targets, self.newObj, False)
            elif mirror == 1:
                self.bspDupIt(self.obj, targets, self.newObj, False)
            if mirror > 1:
                self.bspDupIt(self.obj, targets, self.newObj, True)

    def bspDupIt(self, obj, targets, newObj, mirror):
        self.defaultFeedback()
        dupTargets = []
        newTargets = []
        objsToDelete = []
        rename = False
        if self.rename and mirror:
            rename = True
        if rename:
            nameS = cmds.textField(self.widgets['renameSearch'], q=True, text=True)
            nameR = cmds.textField(self.widgets['renameReplace'], q=True, text=True)
        # basic bspDup setup
        dupSuffix = '_duplicate'
        for tar in targets:
            if rename:
                dup = pm.duplicate(tar, n=tar.replace(nameS, nameR) + 'temp')[0]
            else:
                dup = pm.duplicate(tar, n=tar + dupSuffix)[0]
            dupTargets.append(dup)
            objsToDelete.append(dup)
        dupObj = pm.duplicate(obj, n=obj + dupSuffix)[0]
        dupBsp = pm.blendShape(dupTargets, dupObj)[0]
        objsToDelete.append(dupObj)
        # mirror setup
        targetName = '_newTarget'
        if mirror:
            targetName = '_newMirrorTarget'
            dupGrp = pm.group(n='dupGrp', em=True)
            pm.select(dupObj)
            gmt.lockAttributes(False)
            pm.parent(dupObj, dupGrp)
            dupGrp.sx.set(-1)
            objsToDelete.append(dupGrp)
        # setup bspMaker - wrap and the actual blend shapes will be made with it.
        if newObj:
            bspMaker = pm.duplicate(newObj, n=newObj + '_bspMaker')[0]
        else:
            bspMaker = pm.duplicate(obj, n=obj + '_bspMaker')[0]
        if not bspMaker:
            self.changeFeedback('Object duplication failed', 'red')
            return
        objsToDelete.append(bspMaker)
        pm.select(bspMaker, dupObj)
        cmds.CreateWrap()
        self.renameWrap(bspMaker.listRelatives(s=True)[0])

        # The duplication process - final output creation
        for tar in dupTargets:
            dupBsp.attr(tar).set(1)
            if rename:
                dup = pm.duplicate(bspMaker, n=tar.replace(nameS, nameR).rpartition('temp')[0])[0]
            else:
                dup = pm.duplicate(bspMaker, n=tar.replace(dupSuffix, targetName))[0]
            dupBsp.attr(tar).set(0)
            newTargets.append(dup)

        # cleanup
        pm.delete(objsToDelete)
        if newTargets:
            print "Bsp Duplicator -> created following targets %s" % newTargets
        self.changeFeedback('Blend Shape Duplication Completed', 'green')

    def renameWrap(self, shp):
        newWrap = pm.listConnections(shp, c=True, type='wrap')[0][1]
        newWrap.rename('wrap_' + shp)

    def findBlendShapes(self, obj):
        self.changeFeedback("looking for blendShapes on %s" % obj.name())
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
        else:
            cmds.textField(self.widgets["bsp"], e=True, text="")
            self.changeFeedback('No blend shapes found on "%s"' % obj.name(), "red")

    def getBspShapes(self, obj, bsp):
        '''
        works only if all targets exist in the scene,
        if not, user must rebuild targets manually.
        :param bsp: blend shape node associated with the obj
        :param obj: mesh object node associated with the obj
        :return: The Blend Shape's Targets
        '''
        bspTargets = []
        targets = pm.listConnections(bsp, source=True)
        for tar in targets:
            if tar.type() == 'transform' and tar.name() != obj.name():
                bspTargets.append(tar)
        return bspTargets

    def updateObject(self, field='', *args):
        self.defaultFeedback()
        if field == '':
            return
        tx = cmds.textField(self.widgets[field], q=True, tx=True)
        if field == 'obj':
            self.obj = tx
        if field == 'newObj':
            self.newObj = tx
        if field == 'bsp':
            self.bsp = tx
        try:
            pm.select(tx)
        except:
            self.changeFeedback("Can't find given name '%s' in scene" % tx, 'red')
        obj = pm.PyNode(tx)
        if self.objNotValid(obj, field):
            return

    def objNotValid(self, obj, field):
        self.defaultFeedback()
        if field == 'bsp':
            if obj.type() != 'blendShape':
                return True
        else:
            if obj.type() != 'transform' or not obj.listRelatives(s=True):
                self.changeFeedback("Seems like the selected object doesn't have a shape", 'red')
                return True
            if obj.listRelatives(s=True)[0].type() != 'mesh':
                self.changeFeedback("Seems like the selected object isn't a poly mesh", 'red')
                return True
        return False

    def updateTextField(self, field, *args):
        self.defaultFeedback()
        print "call was made to updateTextField with " + field
        selection = pm.ls(sl=True)
        print "selection is %s" % selection
        if len(selection) == 1:
            sel = selection[0]
            if field == 'bsp':
                if self.objNotValid(sel, field):
                    self.bsp = self.findBlendShapes(sel)
                    if isinstance(self.bsp, list):
                        return
                    sel = self.bsp
                else:
                    self.bsp = sel
            if self.objNotValid(sel, field):
                return
            cmds.textField(self.widgets[field], e=True, tx=sel.name())
            if field == 'obj':
                self.obj = sel
                self.updateTextField('bsp')
            elif field == 'newObj':
                self.newObj = sel
            pm.select(selection)
            return
        self.changeFeedback('Please select a single mesh and try again', 'red')
        return

    def defaultFeedback(self):
        self.changeFeedback("Blend Shape Duplicator Tool")

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)

    def bShapeSelectionWin(self, bShapes):
        if pm.window("bspSel_win", exists=True):
            pm.deleteUI("bspSel_win")
        self.widgets["bspSel_win"] = pm.window("bspSel_win", title="Select Blend Shape", sizeable=1, rtf=True)
        self.widgets[("bspSel_main_Layout")] = cmds.rowColumnLayout(numberOfColumns=1, adj=True)
        bShapeNames = []
        for bsp in bShapes:
            bShapeNames.append(bsp.name())
        hight = 20 * len(bShapes)
        if hight < 100:
            hight = 100
        self.widgets["bspScroll"] = pm.textScrollList(append=bShapeNames, allowMultiSelection=False,
                                                      sii=1, w=250, h=hight)
        pm.button(l="Select Blend Shape", h=40, c=partial(self.bspWinSelection, bShapes))
        pm.showWindow()
        pm.window(self.widgets["bspSel_win"], e=True, h=100)

    def bspWinSelection(self, bShapes, *args):
        idx = pm.textScrollList(self.widgets["bspScroll"], query=True, selectIndexedItem=True)[0]
        idx -= 1
        pm.textField(self.widgets["bsp"], e=True, text=bShapes[idx].name())
        self.bsp = bShapes[idx].name()
        sel = pm.ls(sl=True)
        pm.select(bShapes[idx])
        self.updateTextField('bsp')
        pm.select(sel)
        pm.deleteUI("bspSel_win")