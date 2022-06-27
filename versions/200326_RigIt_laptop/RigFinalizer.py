from maya import cmds, mel
import pymel.core as pm
from functools import partial
import fnmatch
import UI_modules as uim
import RigItMethodsUI as rim
import traceback
import FinalizerFixer
import generalMayaPrints as gmp
import generalMayaTools as gmt

reload(FinalizerFixer)
reload(gmp)
reload(gmt)


class RigFinalizer:
    def __init__(self, par=''):
        self.widgets = {}
        self.feedbackName = 'Rig Finalizer'
        self.barLength = 13
        self.barLength2 = 2
        self.listHight = 400

        self.assetTypes = ["characters", "variants", "set", "props"]
        self.tooFarSteps = 3
        self.logHeaders = {}
        self.fieldsDefault = {}
        self.doubles_hGrp, self.doubles_guides, self.doubles_general = [], [], []

        # Build UI
        topLay = self.winBase('RigFinalizer', self.feedbackName, par)

        mainLay = self.populateUI(topLay)

        pm.separator(h=7, p=mainLay)

        self.layoutAssetDetails(mainLay)

        pm.separator(h=3, p=mainLay)

        self.populate_steps(mainLay)

        self.finalizer = FinalizerFixer.FinalizerFixer(par=self.widgets["top_tabLayout"],
                                                       scriptIt=True, finalizer=self)
        self.updateAssetType()
        self.endProgBar()
        self.defaultFeedback()
        # todo add layers check ?

    def runFinalizer(self, *args):
        self.defaultFeedback()

        # Reset UI
        self.resetUI()
        self.resetProgBar()

        # Start
        self.addTimeStamp()

        # all steps
        for field in self.fieldsOrder:
            self.do_checks(field)
            self.stepProgBar()

        # End
        self.addLog('')
        self.addTimeStamp(False)
        self.addLog('')

        self.endProgBar()

    def do_checks(self, field, ignoreChBox=False, *args):
        chBox = pm.checkBox(self.widgets[field + 'chBox'], q=True, v=True)
        if not chBox and not ignoreChBox:
            return

        method_name = 'ref_' + field
        method = getattr(self, method_name, lambda: 'no field found')
        return method()

    '''
        #another option:
        methodsDict = {
            'hierarchy': self.ref_hierarchy,
            'hGrpOverride': self.ref_hGrpOverride,
            'hGrpVals': self.ref_hGrpVals,
            'animKeys': self.ref_animKeys,
            'ctlVals': self.ref_ctlVals,
            'mainCns': self.ref_mainCns,
            'lambert1': self.ref_lambert1,
            'vray': self.ref_vray,
            'cAttrs': self.ref_cAttrs,
            'guide': self.ref_guide,
            'naming': self.ref_naming,
            'nameSpaces': self.ref_nameSpaces,
            'assembly': self.ref_assembly,
            'references': self.ref_references,
            'ngSkinTools': self.ref_ngSkinTools
        }
        func = methodsDict.get(field, lambda: 'no field found')
        func()
    '''

    def ref_hierarchy(self):
        field = 'hierarchy'
        assetType = self.getAssetType()
        self.widgets[field + '_items'] = []
        tooFar, deformTrans_errors = False, []

        # general hierarchy checks
        hierarchy_errors = self.generalHierarchyChecks(field)

        # set checks
        if assetType == 'set':
            tooFar, hierarchy_errors, deformTrans_errors = self.setHierarchyCheck(field, hierarchy_errors)
        else:
            hierarchy_errors = self.hierarchyCheck(field)

        # check for items outside of "main"
        worldChilds = self.getWorldChilds(assetType)
        # self.endProgBar(True)

        # UI update
        if hierarchy_errors or deformTrans_errors or tooFar or worldChilds:
            space = False
            self.addLogHeader(field)
            for error in hierarchy_errors:
                self.addLog(error)
                space = True
            if hierarchy_errors and deformTrans_errors and space:
                self.addLog('')
            for error in deformTrans_errors:
                self.addLog(error)
                space = True
            if worldChilds:
                if space:
                    self.addLog('')
                self.addLog('Objects found outside of "main":')
                for obj in worldChilds:
                    self.addLog("%s" % obj.name(), space=1)
                    self.widgets[field + '_items'].append(obj)
                space = True
            if tooFar:
                if space:
                    self.addLog('')
                self.addLog('Transforms too far from high_grp:', fix=True)
                self.isTooFarFromParent('deform', printLog=field)
            self.updateTextFramesStat(field, red=True, fieldNote='Hierarchy issues found - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No Hierarchy issues found')

    def generalHierarchyChecks(self, field):
        hierarchy_errors = []
        allhGrp = pm.ls('high_grp')
        amt = len(allhGrp)
        if amt > 0:
            if amt > 1:
                hierarchy_errors.append('multiple "high_grp" objects in scene')
                self.widgets[field + '_items'].append(allhGrp)
            else:
                hGrp = allhGrp[0]
                main = hGrp.getParent()
                if main != 'main':
                    hierarchy_errors.append('"high_grp" should be child of "main"')
                    self.widgets[field + '_items'].append(hGrp)
                if main:
                    par = main.getParent()
                    if par:
                        hierarchy_errors.append('"main" should be child of world')
                        self.widgets[field + '_items'].append(main)
                else:
                    hierarchy_errors.append('"main" not found')
        else:
            hierarchy_errors.append('"high_grp" not found')
        return hierarchy_errors

    def hierarchyCheck(self, field):
        if not pm.objExists('high_grp'):
            return []
        hGrpObjs = pm.listRelatives('high_grp', ad=True, type='transform')
        constraints = pm.listRelatives('high_grp', ad=True, type='constraint')

        errors = []
        self.resetProgBar2(len(hGrpObjs))
        for obj in hGrpObjs:
            grp = False
            okObj = False
            added = False
            suffix = 'Hierarchy issues: "%s" - ' % obj.name()
            if obj not in constraints:
                shps = pm.listRelatives(obj, s=True)
                if not shps:
                    if not pm.listRelatives(obj, ad=True):
                        errors.append(suffix + 'Empty group')
                        self.widgets[field + '_items'].append(obj)
                        added = True
                    okObj = True
                else:
                    for shp in shps:
                        shpType = shp.type()
                        if 'mesh' not in shpType:
                            errors.append(suffix + 'Shape isn\'t "mesh"')
                            added = True
                        else:
                            connections = pm.listConnections(shp, d=False, s=True)
                            if connections:
                                for con in connections:
                                    if 'geometryFilter' in pm.nodeType(con, i=True):
                                        okObj = True
                    objChildren = pm.listRelatives(obj, ad=True, type='transform')
                    if objChildren:
                        errors.append(suffix + 'Children found.. (bad boy)')
                        for objCh in objChildren:
                            if objCh not in self.widgets[field + '_items']:
                                self.widgets[field + '_items'].append(objCh)
            if not okObj and obj not in constraints:
                if obj not in self.widgets[field + '_items']:
                    self.widgets[field + '_items'].append(obj)
                if not added:
                    errors.append(suffix + 'No deformer found')
            self.stepProgBar(True)
        self.endProgBar(True)
        for obj in constraints:
            errors.append('Constraint in high_grp: %s' % obj.name())
            self.widgets[field + '_items'].append(obj)
        return errors

    def setHierarchyCheck(self, field, hierarchy_errors):
        deformTrans_errors = []

        setGrps = ['deform', 'transform']
        tooFar = False
        if self.isTooFarFromParent('deform'):
            tooFar = True

        if not pm.objExists('high_grp'):
            return tooFar, hierarchy_errors, deformTrans_errors
        self.resetProgBar2(3)
        self.stepProgBar(True)
        # check what's outside of deform/transform
        for obj in pm.listRelatives('high_grp', c=True, type='transform'):
            name = obj.name()
            if name not in setGrps:
                hierarchy_errors.append('"%s" is outside of deform/transform' % obj)
                self.widgets[field + '_items'].append(obj)
        self.stepProgBar(True)
        # check under transform/deform
        for obj in setGrps:
            objList = pm.ls(obj)
            amt = len(objList)
            if amt > 0:
                if amt > 1:
                    hierarchy_errors.append('multiple "%s" objects found in scene' % obj)
                    self.widgets[field + '_items'].append(objList)
                else:
                    grp = objList[0]
                    hGrp = grp.getParent()
                    if hGrp != 'high_grp':
                        hierarchy_errors.append('"%s" should be child of "high_grp"' % grp)
                        self.widgets[field + '_items'].append(grp)
            else:
                hierarchy_errors.append('"%s" group not found' % obj)
        self.endProgBar(True)

        # deform / transform checks
        errorsDef, badObjsDef = self.deformCheck()
        errorsTrans, badObjsTrans = self.transformCheck()

        badObjs = badObjsDef + badObjsTrans
        for obj in badObjs:
            self.widgets[field + '_items'].append(obj)
        errors = errorsDef + errorsTrans
        for error in errors:
            deformTrans_errors.append(error)
        return tooFar, hierarchy_errors, deformTrans_errors

    def deformCheck(self):
        deform = 'high_grp|deform'
        if pm.objExists(deform):
            deform = pm.PyNode(deform)
        else:
            return [], []

        deformObjs = pm.listRelatives(deform, ad=True, type='transform')
        constraints = pm.listRelatives(deform, ad=True, type='constraint')
        errors = []
        notGood = []
        self.resetProgBar2(len(deformObjs))
        for obj in deformObjs:
            okObj = False
            added = False
            suffix = '"deform" issues: "%s" - ' % obj.name()
            if obj not in constraints:
                shps = pm.listRelatives(obj, s=True)
                if not shps:
                    if pm.listRelatives(obj, ad=True):
                        okObj = True
                    else:  # empty group
                        errors.append(suffix + 'Empty group')
                        added = True
                for shp in shps:
                    shpType = shp.type()
                    if 'mesh' not in shpType:
                        errors.append(suffix + 'Shape isn\'t "mesh"')
                        added = True
                    else:
                        connections = pm.listConnections(shp, d=False, s=True)
                        if connections:
                            for con in connections:
                                if 'geometryFilter' in pm.nodeType(con, i=True):
                                    okObj = True
            else:
                errors.append(suffix + '%s should be under "transform"' % obj.type())
                added = True
            if not okObj:
                obj = obj.name()
                if obj not in notGood:
                    notGood.append(obj)
                if not added:
                    errors.append(suffix + 'No deformer found')
            self.stepProgBar(True)
        self.endProgBar(True)
        if errors:
            errors.append('')
        return errors, notGood

    def hasCns(self, obj, needCns_attrs, objCount=0):
        if not needCns_attrs:
            return True
        if not obj:
            return False
        par = pm.listRelatives(obj, p=True)
        if par:
            par = par[0]
        else:  # world is parent
            return False
        objName = str("%s" % obj)
        if 'main' == objName:
            return False
        cnsAttrs = cmds.listConnections(objName, s=True, d=False, type='constraint', p=True)
        if not cnsAttrs:
            if 'transform' == objName:
                return False
            return self.hasCns(par, needCns_attrs)

        # check cns on current
        goodSum = []
        for transAt in needCns_attrs:
            i = 0  # bad count
            ii = 0  # good count
            notFound = []
            for axis in "XYZ":
                attr = transAt + axis
                found = False
                for cnsAttr in cnsAttrs:
                    if attr in cnsAttr:
                        found = True
                        ii += 1
                if not found:
                    notFound.append(attr)
                    i += 1
            if ii == 3:
                goodSum.append(transAt)
        for good in goodSum:
            if good in needCns_attrs:
                needCns_attrs.remove(good)
        if not needCns_attrs:
            return True
        return self.hasCns(par, needCns_attrs)

    def transformMeshesCheck(self, meshes, needCns, needCns_attrs):
        hasDeformers = []
        missingCns = []
        self.resetProgBar2(len(meshes))
        for obj in meshes:
            shps = pm.listRelatives(obj, s=True)
            for shp in shps:
                connections = pm.listConnections(shp, d=False, s=True)
                if connections:
                    for con in connections:
                        if 'geometryFilter' in pm.nodeType(con, i=True):
                            if obj not in hasDeformers:
                                hasDeformers.append(obj)
            if needCns:
                temp = []
                for item in needCns_attrs:
                    temp.append(item)
                if not self.hasCns(obj, temp):
                    if obj not in missingCns:
                        missingCns.append(obj)
            self.stepProgBar(True)
        self.endProgBar(True)
        return hasDeformers, missingCns

    def isPivotCentered(self, obj):
        centered = True
        grp = pm.group(em=True, w=True)
        pm.delete(pm.parentConstraint(obj, grp))
        pm.delete(pm.scaleConstraint(obj, grp))
        for atr in 'trs':
            for axi in 'xyz':
                value = grp.attr(atr + axi).get()
                if atr != 's':
                    if round(value, 3) != 0.0:
                        centered = False
                else:
                    if round(value, 3) != 1.0:
                        centered = False
        pm.delete(grp)
        return centered

    def transformObjsFilter(self, transformObjs, constraints):
        emptyGrps, meshes, notMeshesShapes, hasChildren, badPivot = [], [], [], [], []
        self.resetProgBar2(len(transformObjs))
        for obj in transformObjs:
            grp = False
            if not obj in constraints:
                # check if pivot is centered
                if not self.isPivotCentered(obj):
                    if obj not in badPivot:
                        badPivot.append(obj)
                # check if mesh or grp
                shps = pm.listRelatives(obj, s=True)
                if shps:
                    addMesh = True
                    for shp in shps:
                        shpType = shp.type()
                        if 'mesh' not in shpType:
                            addMesh = False
                            if obj not in notMeshesShapes:
                                notMeshesShapes.append(obj)
                    if addMesh:
                        meshes.append(obj)
                else:
                    grp = True
                    if not pm.listRelatives(obj, ad=True):  # an empty group
                        if obj not in emptyGrps:
                            emptyGrps.append(obj)
                if not grp:
                    objChildren = pm.listRelatives(obj, ad=True, type='transform')
                    if objChildren:
                        hasChildren.append(obj)
            self.stepProgBar(True)
        self.endProgBar(True)
        return emptyGrps, meshes, notMeshesShapes, hasChildren, badPivot

    def checkConstrainted(self, obj, needCns_attrs, transformGrp=False):
        errorsSum = []
        goodSum = []
        objName = obj.name()
        print('checkConstrainted("%s", %s, transformGrp=%s)' % (objName, needCns_attrs, transformGrp))
        cnsAttrs = cmds.listConnections(objName, s=True, d=False, type='constraint', p=True)
        self.resetProgBar2(len(cnsAttrs))
        if cnsAttrs:
            for transAt in needCns_attrs:
                i = 0  # bad count
                ii = 0  # good count
                notFound = []
                for axis in "XYZ":
                    attr = transAt + axis
                    found = False
                    for cnsAttr in cnsAttrs:
                        if attr in cnsAttr:
                            found = True
                            ii += 1
                    if not found:
                        notFound.append(attr)
                        i += 1
                if ii == 3:
                    goodSum.append(transAt)
                else:
                    if i == 3:
                        if transformGrp:
                            errorsSum.append('"%s" isn\'t connected: "%s"' % (objName, transAt))
                        else:
                            errorsSum.append('"%s" Not connected' % (transAt))
                    else:
                        for attr in notFound:
                            if transformGrp:
                                errorsSum.append('"%s" isn\'t connected: "%s"' % (objName, attr))
                            else:
                                errorsSum.append('"%s" Not connected' % (attr))
                self.stepProgBar(True)
        else:
            errorsSum = needCns_attrs
        self.endProgBar(True)
        return errorsSum, goodSum

    def transformCnsCheck(self, transform, needCns, needCns_attrs):
        errors = []
        # check transform constraint
        errorsSum, goodSum = self.checkConstrainted(transform, needCns_attrs, True)
        if errorsSum:
            if goodSum:
                for transAt in goodSum:
                    needCns_attrs.remove(transAt)
                types = goodSum[0]
                for i in range(1, len(goodSum)):
                    types += ' and %s' % goodSum[i]
                needTypes = needCns_attrs[0]
                for i in range(1, len(needCns_attrs)):
                    needTypes += ' and %s' % needCns_attrs[i]
                errors.append('"transform" grp is connected to %s but not to %s:' % (types, needTypes))
            for error in errorsSum:
                errors.append(error)
        else:
            needCns = False
            needCns_attrs = []
        return errors, needCns, needCns_attrs

    def transformCheck(self):
        transform = 'high_grp|transform'
        if pm.objExists(transform):
            transform = pm.PyNode(transform)
        else:
            return [], []
        errors = []
        notGood = []

        # check if no constraints at all
        transformObjs = pm.listRelatives(transform, ad=True, type='transform')
        constraints = pm.listRelatives(transform, ad=True, type='constraint')
        if transformObjs and not constraints:
            errors.append('No constraints found under transform')

        # check if transform is constrained to avoid more cns seaarches
        needCns = True
        needCns_attrs = ['Translate', 'Rotate', 'Scale']
        errorsT, needCns, needCns_attrs = self.transformCnsCheck(transform, needCns, needCns_attrs)
        if errorsT:
            errors += errorsT
            notGood.append(transform)

        # check for empty groups, bad shape types, children under meshes, bad pivots (not centered)
        returnList = self.transformObjsFilter(transformObjs, constraints)
        emptyGrps, meshes, notMeshesShapes, hasChildren, badPivot = returnList

        hasDeformers, missingCns = self.transformMeshesCheck(meshes, needCns, needCns_attrs)
        notGood += hasDeformers + emptyGrps + hasChildren + badPivot

        for obj in hasDeformers:
            errors.append(self.transformSuffix(obj) + 'Has a deformer')
        for obj in missingCns:
            errors.append(self.transformSuffix(obj) + "isn't fully constrained (trans/rot/scale)")
        for obj in hasChildren:
            errors.append(self.transformSuffix(obj) + "Shouldn't have Constraints/children")
        for obj in emptyGrps:
            errors.append(self.transformSuffix(obj) + 'Empty group')
        for obj in badPivot:
            errors.append(self.transformSuffix(obj) + 'Pivot Not centered')
        for obj in notMeshesShapes:
            errors.append(self.transformSuffix(obj) + 'Shape isn\'t "mesh"')
        return errors, notGood

    def transformSuffix(self, obj):
        return '"transform" issues: "%s" - ' % obj.name()

    def getWorldChilds(self, assetType):
        allowedObjs = ['persp', 'top', 'front', 'side', 'main']  # todo test more cases
        if assetType == 'set':
            worldObjs = pm.ls('|*')
        else:
            worldObjs = pm.ls('|*', '|*:*')
        worldChilds = []
        for obj in worldObjs:
            name = obj.name()
            if name not in allowedObjs and not 'guide' in name:
                worldChilds.append(obj)
        return worldChilds

    def ref_hGrpOverride(self, *args):
        field = 'hGrpOverride'
        self.widgets[field + '_items'] = []

        # check override issues
        error = False
        hGrp = 'high_grp'
        objList = pm.ls(hGrp)
        amt = len(objList)
        if amt > 0:
            if amt > 1:
                error = 'multiple "%s" objects found in scene' % hGrp
                self.widgets[field + '_items'] = objList
            else:
                self.widgets[field + '_items'] = objList[0]
        else:
            error = '"%s" group not found' % hGrp
        if error:
            self.addLogHeader(field)
            self.addLog(error)
            self.updateTextFramesStat(field, red=True, fieldNote=error)
            return
        hGrp_ad = pm.listRelatives(hGrp, ad=True, noIntermediate=True)

        hGrp_ad.append(hGrp)
        obj_override = []
        obj_dispType = []
        obj_highGrp = False
        self.resetProgBar2(len(hGrp_ad))
        for obj in hGrp_ad:
            ovEnabled = pm.getAttr(obj + '.overrideEnabled')
            if ovEnabled:
                if obj != hGrp:
                    error = True
                    if obj not in obj_override:
                        obj_override.append(obj)
                if pm.getAttr(obj + '.overrideDisplayType') != 2:
                    error = True
                    if obj not in obj_dispType:
                        obj_dispType.append(obj)
            else:
                if obj == hGrp:
                    obj_highGrp = True
                    error = True
            self.stepProgBar(True)
        self.endProgBar(True)

        # UI update
        if error:
            self.addLogHeader(field)
            notOverride = 0
            if obj_highGrp:
                notOverride += 1
                self.addLog('Override NOT Enabled for high_grp')
            if obj_override:
                self.addLog('Override Enabled for high_grp children/shapes')
            if obj_dispType:
                notOverride += 1
                self.addLog('overrideDisplayType not Reference for high_grp objects')
            if notOverride:
                self.updateTextFramesStat(field, red=True, fieldNote='found high_grp errors - see log')
            else:  # if only override children errors - yellow error
                self.updateTextFramesStat(field, yellow=True, fieldNote='found high_grp errors - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='Override checked')

    def ref_hGrpVals(self, *args):
        field = 'hGrpVals'
        self.widgets[field + '_items'] = []
        if not pm.objExists('high_grp'):
            self.addLogHeader(field)
            self.addLog('"high_grp" group not found')
            self.widgets[field + '_items'] = []
            self.updateTextFramesStat(field, red=True, fieldNote='No "high_grp" found!')
            return

        # highGrp vals check
        hGrp_ad = pm.listRelatives('high_grp', ad=True, s=False, typ='transform')
        hGrp_ad.append('high_grp')
        hGrp_ad.append('main')
        objs_to_fix = []
        self.resetProgBar2(len(hGrp_ad))
        for obj in hGrp_ad:
            for atr in 'trs':
                for axi in 'xyz':
                    value = pm.getAttr(obj + '.' + atr + axi)
                    if atr != 's':
                        if round(abs(value), 3) > 0.0:
                            if str(obj) not in objs_to_fix:
                                objs_to_fix.append(obj)

                    else:
                        if round(abs(value), 3) > 1.0:
                            if str(obj) not in objs_to_fix:
                                objs_to_fix.append(obj)
            self.stepProgBar(True)
        self.endProgBar(True)

        # UI check
        if objs_to_fix:
            self.addLogHeader(field)
            for obj in objs_to_fix:
                self.widgets[field + '_items'].append(obj)
                self.addLog('Found vals on "%s"' % obj)
            self.updateTextFramesStat(field, red=True, fieldNote='found high_grp Values - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='clean high_grp values')

    def ref_animKeys(self):
        field = 'animKeys'

        # check main
        try:
            main = pm.PyNode('main')
        except:
            self.addLog('- Cancelled: Can\'t find "main" -- step skipped - -')
            self.updateTextFramesStat(field, red=True, fieldNote='Can\'t find "main" - skipped step')
            return

        # animKeys check
        main_ad = pm.listRelatives(main, ad=True, s=False, typ='transform')
        self.resetProgBar2(len(main_ad))
        obj_keys_list = []
        for obj in main_ad:
            animCrvs = pm.listConnections(obj, type='animCurve', d=False, s=True)
            for con in animCrvs:
                conType = con.type()
                if 'animCurveU' not in conType:
                    if obj not in obj_keys_list:
                        obj_keys_list.append(obj)
            self.stepProgBar(True)
        self.endProgBar(True)

        # UI update
        if obj_keys_list:
            self.addLogHeader(field)
            for obj in obj_keys_list:
                self.addLog('Found animation on "%s"' % obj)
            self.widgets[field + '_items'] = obj_keys_list
            self.updateTextFramesStat(field, red=True, fieldNote='found animation keys - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No animation found under "main"')

    def ref_ctlVals(self):
        field = 'ctlVals'

        ctls = pm.ls('*_ctl')
        withVals = []
        self.resetProgBar2(len(ctls))
        for ctl in ctls:
            shp = pm.listRelatives(ctl, s=True)
            if not shp:
                self.stepProgBar(True)
                continue
            for attr in 'trs':
                vals = ctl.attr(attr).get()
                for axis, val in zip('xyz', vals):
                    if attr == 's':
                        val -= 1
                    if round(val, 3):
                        if pm.getAttr(ctl.attr(attr + axis), lock=True):
                            continue
                        name = ctl.name()
                        if name not in withVals:
                            withVals.append(name)
            self.stepProgBar(True)
        self.endProgBar(True)

        # UI update
        if withVals:
            self.addLogHeader(field)
            for ctl in withVals:
                self.addLog('ctl with values: "%s"' % ctl)
            self.widgets[field + '_items'] = withVals
            self.updateTextFramesStat(field, red=True, fieldNote='found ctl transform vals - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No ctl transform values found')

    def ref_mainCns(self):
        field = 'mainCns'
        assetType = self.getAssetType()

        # create ctl list
        cnsFixList = []
        missins_cns = []
        main_ctls = ['global_C0_ctl', 'control_C0_ctl', 'asmLocal_C0_ctl']
        if 'props' in assetType or 'set' in assetType:
            main_ctls.append('local_C0_ctl')
        # todo change? currently checks only ctls in list.
        for ctl in main_ctls:
            if pm.objExists(ctl):
                if not pm.objExists(ctl + '_cns') and not pm.objExists(ctl + '_cns_ctl'):
                    missins_cns.append(ctl)
                    cnsFixList.append(ctl)

        # finds existing ctls with shapes and check if they're connected
        disconnected_cns = []
        cnsLs = pm.ls(['*_cns', '*_cns_ctl'])
        self.resetProgBar2(len(cnsLs))
        for cns in cnsLs:
            shp = cns.getShape()
            if shp:
                conn = pm.listConnections(cns.v, p=True)
                if conn:
                    if 'ShowCnsC' in conn[0].name():
                        continue
                conn = pm.listConnections(shp.v, p=True)
                if conn:
                    if 'ShowCnsC' in conn[0].name():
                        continue
                disconnected_cns.append(shp)
                cnsFixList.append(cns)
            self.stepProgBar(True)
        self.endProgBar(True)

        # UI update
        if cnsFixList:
            self.addLogHeader(field)
            for obj in missins_cns:
                self.addLog('ctl missing cns: "%s"' % obj)
            for obj in disconnected_cns:
                self.addLog('cns shape not connected: "%s"' % obj)
            self.widgets[field + '_items'] = cnsFixList
            self.updateTextFramesStat(field, red=True, fieldNote='found cns issues - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No cns issues found')

    def ref_lambert1(self):
        field = 'lambert1'
        error = False
        cons_lamb1 = []
        lam1 = pm.PyNode('lambert1')

        # check incoming connections
        conn = pm.listConnections(lam1, s=True, d=False, p=True, c=True)
        if conn:
            for lam1_attr, sourceAttr in conn:
                cons_lamb1.append([lam1_attr, sourceAttr])
                error = True

        # check default color
        color = lam1.color.get()
        colorOK = True
        for c in color:
            if c != 0.5:
                colorOK = False
                error = True

        # find objects with lambert1 under highGrp
        if not pm.objExists('high_grp'):
            self.widgets[field + '_items'] = []
            self.updateTextFramesStat(field, red=True, fieldNote='No "high_grp" found')
            return

        objs_lamb1, shps_lamb1 = self.get_lambert1_objs()

        # selection update
        if objs_lamb1 or shps_lamb1:
            self.widgets[field + '_items'] = objs_lamb1
            error = True
        else:
            self.widgets[field + '_items'] = []
        # UI update
        if error:
            self.addLogHeader(field)
            for lam1_attr, sourceAttr in cons_lamb1:
                self.addLog('connection found: "%s" from "%s"' % (lam1_attr, sourceAttr))
            if not colorOK:
                self.addLog('lambert1 color isn\'t set to default (default is [0.5, 0.5, 0.5])')
            for obj in shps_lamb1:
                self.addLog('connected to lambert1: "%s"' % obj)
            self.updateTextFramesStat(field, red=True, fieldNote='found lambert1 issues - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No lambert1 issues found')

    def ref_vray(self):
        field = 'vray'
        vray_nodes = pm.ls('*vray*') + pm.ls('*vRay*') + pm.ls('*VRay*') + pm.ls('*VRAY*')
        self.widgets[field + '_items'] = vray_nodes
        if vray_nodes:
            self.addLogHeader(field)
            self.addLog('Found vray nodes in scene')
            self.updateTextFramesStat(field, red=True, fieldNote='found vRay nodes - see log')
        else:
            self.widgets[field + '_items'] = []
            self.updateTextFramesStat(field, green=True, fieldNote='No vRay nodes found')

    def ref_cAttrs(self):
        field = 'cAttrs'

        # c_attrs check
        errors = []
        if not pm.objExists('high_grp'):
            self.updateTextFramesStat(field, red=True, fieldNote='No "high_grp" found')
            return
        obj = pm.PyNode('high_grp')
        allAttrs = pm.listAttr(obj, r=1, s=1, k=1)
        removeAttrs = fnmatch.filter(allAttrs, "visibility")
        for channel in ['translate', 'rotate', 'scale']:
            removeAttrs = removeAttrs + fnmatch.filter(allAttrs, "%s*" % channel)
        for attr in removeAttrs:
            allAttrs.remove(attr)

        self.resetProgBar2(len(allAttrs))
        for attr in allAttrs:
            attrName = obj.attr(attr).name()
            if 'c_' not in attr:
                errors.append('no "c_" prefix on "%s"' % attrName)
            else:
                cons = pm.listConnections(obj.attr(attr), p=True)
                if len(cons):
                    for con in cons:
                        gCtl = con.rpartition('.')[0]
                        if gCtl == 'global_C0_ctl':
                            s_attr = con.rpartition('.')[2]
                            if not 'c_' + s_attr == attr:  #
                                errors.append('global ctl attr name doesn\'t match "%s" to "%s"' % (s_attr, attr))
                else:
                    errors.append('no connection found on "%s"' % attrName)
            self.stepProgBar(True)
        self.endProgBar(True)

        # UI update
        if errors:
            self.addLogHeader(field)
            for error in errors:
                self.addLog(error)
            self.updateTextFramesStat(field, red=True, fieldNote='found c_attr errors - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No "c_attrs" issues found')
            return

    def ref_guide(self):
        field = 'guide'
        assetType = self.getAssetType()

        # guides check
        guides = pm.ls('*guide*', type='transform')

        # UI update
        if guides:
            self.addLogHeader(field)
            for guide in guides:
                self.addLog('guide found: "%s"' % guide)
            self.widgets[field + '_items'] = guides
            text = 'Guides found - see log'
            if 'props' in assetType or 'set' in assetType:
                self.updateTextFramesStat(field, yellow=True, fieldNote=text)
            else:
                self.updateTextFramesStat(field, red=True, fieldNote=text)
        else:
            self.widgets[field + '_items'] = []
            self.updateTextFramesStat(field, green=True, fieldNote='No guides found')

    def ref_naming(self):
        field = 'naming'

        self.doubles_hGrp, self.doubles_guides, self.doubles_general = {}, {}, {}
        doubles_hGrp, doubles_guides, doubles_general = {}, {}, {}
        if not pm.objExists('main'):
            self.updateTextFramesStat(field, red=True, fieldNote='No "main" found')
            return

        # name check
        ad = pm.listRelatives('main', ad=True)
        cards = pm.ls('*_card')
        self.resetProgBar2(len(ad))
        for obj in ad:
            obj = obj.name()
            guideItem = False
            hGrpItem = False
            if '|' in obj:
                # if obj not in selection:
                #    selection.append(obj)
                tempLs = pm.ls(obj.rpartition('|')[2])
                if len(tempLs) < 2:
                    continue
                tempColWith = []
                for temp in tempLs:
                    temp = temp.name()
                    if gmt.isUnderPar(temp, 'high_grp'):
                        hGrpItem = temp
                    elif gmt.isUnderPar(temp, 'guide'):
                        guideItem = temp
                    else:
                        tempColWith.append(temp)
                if hGrpItem:
                    if hGrpItem not in doubles_hGrp.keys():
                        doubles_hGrp[hGrpItem] = []
                    for item in tempColWith:
                        if item not in doubles_hGrp[hGrpItem]:
                            doubles_hGrp[hGrpItem].append(item)
                elif guideItem:
                    if guideItem not in doubles_guides.keys():
                        doubles_guides[guideItem] = []
                    for item in tempColWith:
                        if item not in doubles_guides[guideItem]:
                            doubles_guides[guideItem].append(item)
                else:
                    if obj not in doubles_general:
                        name = obj.rpartition('|')[2]
                        # varify that there are multiple of this name
                        doubles = pm.ls(name)
                        if len(doubles) < 2:
                            continue
                        if name not in doubles_general.keys():
                            doubles_general[name] = doubles
            self.stepProgBar(True)
        self.endProgBar(True)

        # print all groups cleanly
        self.doubles_hGrp, self.doubles_guides, self.doubles_general = doubles_hGrp, doubles_guides, doubles_general
        if doubles_hGrp or doubles_guides or doubles_general or cards:
            self.addLogHeader(field)
            space = False
            for obj in cards:
                self.addLog('"_card" found: "%s"' % obj)
                space = True
            if doubles_hGrp:
                self.addSpace(space)
                self.addLog('names clashing for objects under high_grp:')
                space = True
                for obj in doubles_hGrp:
                    self.addSpace(space)
                    self.addLog('"%s"' % obj, space=1)
                    self.addLog('clashes with:', fix=True, space=1)
                    for obj2 in doubles_hGrp[obj]:
                        self.addLog('"%s"' % obj2, space=2)
            if doubles_guides:
                self.addSpace(space)
                self.addLog('names clashing for objects under a guide:')
                space = True
                for obj in doubles_guides:
                    self.addSpace(space)
                    self.addLog('"%s"' % obj, space=1)
                    self.addLog('clashes with:', fix=True, space=1)
                    for obj2 in doubles_guides[obj]:
                        self.addLog('"%s"' % obj2, space=2)
            if doubles_general:
                self.addSpace(space)
                self.addLog('General name clashings found:')
                self.addSpace(True)
                for name in doubles_general:
                    for obj in doubles_general[name]:
                        self.addLog('"%s"' % obj, space=1)
                    self.addLog('')
            yellowError = False
            if doubles_guides:
                if not doubles_hGrp and not doubles_general:
                    yellowError = True
            if yellowError:  # if only guide naming clashes found
                self.updateTextFramesStat(field, yellow=True, fieldNote='Naming issues found - see log')
            else:
                self.updateTextFramesStat(field, red=True, fieldNote='Naming issues found - see log')
        else:
            # self.widgets[field + '_items'] = []
            self.updateTextFramesStat(field, green=True, fieldNote='No naming issues found')

    def ref_nameSpaces(self):
        field = 'nameSpaces'
        self.widgets[field + '_items'] = []

        # unloaded check
        ns_errors = []
        ns_objs = []
        # find refences name spaces
        ref_nSpaces = []
        ref_list = cmds.file(q=True, r=True)
        for ref in ref_list:
            name = pm.referenceQuery(ref, rfn=True)
            ref_nSpaces.append(name.rpartition('RN')[0])
        # sort all name space objects to a dictionary
        ns_dict = {}
        allNsObjs = pm.ls('*:*')
        for obj in allNsObjs:
            nSpace = obj.name().partition(':')[0]
            if nSpace not in ns_dict.keys():
                ns_dict[nSpace] = []
            ns_dict[nSpace].append(obj)
        # check what's not referenced
        # create obj return list
        for nSpace in ns_dict:
            if nSpace not in ref_nSpaces:  # else means it's referenced
                ns_errors.append('Found namespace: "%s"' % nSpace)
                ns_objs += ns_dict[nSpace]

        # UI update
        self.widgets[field + '_items'] += ns_objs
        if ns_errors:
            self.addLogHeader(field)
            for error in ns_errors:
                self.addLog(error)
            self.updateTextFramesStat(field, yellow=True, fieldNote="Namespace/s found")
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No Namespace/s found')

    def ref_assembly(self):
        field = 'assembly'
        assetType = self.getAssetType()

        # assembly check
        asm_errors = []
        # find refences name spaces
        ref_nSpaces = []
        ref_list = cmds.file(q=True, r=True)
        for ref in ref_list:
            name = pm.referenceQuery(ref, rfn=True)
            ref_nSpaces.append(name.rpartition('RN')[0])
        ref_objs = []
        if ref_nSpaces:
            for nSpace in ref_nSpaces:
                nsObjs = pm.ls(nSpace + ':*')  # todo select only the top-most objs?
                ref_objs += nsObjs
            if pm.objExists('assembly') != True:  # todo check assembly node type?
                if 'set' in assetType:
                    asm_errors.append('"assembly" node is missing - References found in scene')
            else:
                asm_errors.append('References found in scene')

        # UI update
        if 'set' in assetType:
            self.widgets[field + '_items'] = []
        else:
            self.widgets[field + '_items'] = ref_objs
        if asm_errors:
            self.addLogHeader(field)
            for error in asm_errors:
                self.addLog(error)
            if 'set' in assetType:
                self.updateTextFramesStat(field, red=True, fieldNote='Assembly issues found - see log')
            else:
                self.updateTextFramesStat(field, red=True, fieldNote="References issues found - Asset isn't set")
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No Assembly issues found')

    def ref_references(self):
        field = 'references'
        assetType = self.getAssetType()

        ref_errors = []
        ref_list = cmds.file(q=True, r=True)
        if 'set' in assetType:  # check for unloaded
            for ref in ref_list:
                name = pm.referenceQuery(ref, rfn=True)
                loaded = pm.referenceQuery(ref, il=True)
                if not loaded:
                    ref_errors.append('Unloaded ref: "%s"' % name)
        else:
            for ref in ref_list:
                name = pm.referenceQuery(ref, rfn=True)
                loaded = pm.referenceQuery(ref, il=True)
                if not loaded:
                    ref_errors.append('Reference found in scene: "%s" (unloaded)' % name)
                else:
                    ref_errors.append('Reference found in scene: "%s"' % name)

        # UI update
        if ref_errors:
            self.addLogHeader(field)
            for error in ref_errors:
                self.addLog(error)
            if 'set' in assetType:
                self.updateTextFramesStat(field, red=True, fieldNote='Unloaded references found - see log')
            else:
                self.updateTextFramesStat(field, red=True, fieldNote='References found in scene - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No references issues found')

    def ref_ngSkinTools(self):
        field = 'ngSkinTools'
        ngNodes = pm.ls('ngSkinTools*')
        if ngNodes:
            self.addLogHeader(field)
            for node in ngNodes:
                self.addLog('ngSkinTool node: "%s"' % node)
            self.widgets[field + '_items'].append(ngNodes)
            self.updateTextFramesStat(field, red=True, fieldNote='ngSkinTools nodes found')
        else:
            self.widgets[field + '_items'] = []
            self.updateTextFramesStat(field, green=True, fieldNote='No ngSkinTools nodes found')

    def isTooFarFromParent(self, obj, printLog=False):
        if not pm.objExists(obj):
            if printLog:
                self.addLog('Can\'t find "%s"' % obj)
                return True
            else:
                return True
        steps = cmds.intSliderGrp(self.widgets['hierIntField'], q=True, v=True)
        ad = pm.listRelatives(obj, ad=True, type='transform')
        self.resetProgBar2(len(ad))
        tooFar = self.do_isTooFarFromParent(obj, steps, printLog)
        self.endProgBar(True)
        return tooFar

    def do_isTooFarFromParent(self, obj, steps, printLog=False, amt=None):
        self.stepProgBar(True)
        if not amt:
            amt = steps
        ch = pm.listRelatives(obj, c=True, type='transform')
        if ch:
            if not steps:
                if printLog:
                    field = printLog
                    self.addLog('children under "%s" are more than %s steps away:' % (obj, amt))
                    ch2 = pm.listRelatives(obj, c=True, ad=True, type='transform')
                    for c in ch2:
                        shps = pm.listRelatives(c, type=['mesh'])
                        if shps:
                            if printLog:
                                self.widgets[field + '_items'].append(c)
                                self.addLog(str(c.name()), space=1)
                else:
                    self.stepProgBar(True)
                    return True
            for c in ch:
                temp = self.do_isTooFarFromParent(c, steps - 1, printLog, amt)
                if not printLog and temp:
                    self.stepProgBar(True)
                    return True


    def get_lambert1_objs(self):
        highG_shps = pm.listRelatives('high_grp', ad=True, type='mesh')
        pm.select('lambert1')
        cmds.hyperShade(objects='')  # todo make it not a hypershade command?
        sele = pm.ls(sl=True)
        objs_lamb1 = []
        shps_lamb1 = []
        for obj in sele:
            if pm.objectType(obj) == 'mesh':
                shp = pm.PyNode(obj.partition('.')[0])
                if shp in highG_shps:
                    objs_lamb1.append(obj)
                    if shp not in shps_lamb1:
                        shps_lamb1.append(shp)
        return objs_lamb1, shps_lamb1

    def fixLambert1(self, *args):
        lam1 = pm.PyNode('lambert1')

        # find objects with lambert1 under highGrp
        objs_lamb1, shps_lamb1 = self.get_lambert1_objs()
        newLambert = False

        # create new lambet if needed
        if objs_lamb1:
            newLambert = pm.shadingNode('lambert', asShader=True, n='lambert1_buffer')
            self.addLog('created a lambert1 replacement: "%s"' % newLambert)

            # get attrs and set on new lambert
            attrs = pm.listAttr(lam1, r=1, s=1, k=1)
            for attr in attrs:
                newVal = newLambert.attr(attr).get()
                val = lam1.attr(attr).get()
                newLambert.attr(attr).set(val)
                try:
                    lam1.attr(attr).set(newVal)
                except:
                    pass
            # assign the new lambert
            pm.select(objs_lamb1)
            pm.hyperShade(assign=newLambert)
            for shp in shps_lamb1:
                self.addLog('reconnected "%s" to "%s"' % (shp, newLambert))

        # disconnect lambert1 connections if found
        conn = pm.listConnections(lam1, s=True, d=False, p=True, c=True)
        if conn:
            for lam1_attr, sourceAttr in conn:
                # print('pm.disconnectAttr("%s, %s")' % (sourceAttr, lam1_attr))
                pm.disconnectAttr(sourceAttr, lam1_attr)
                if newLambert:
                    attr = lam1_attr.name().partition('.')[2]
                    pm.connectAttr(sourceAttr, newLambert.attr(attr))
                    self.addLog('reconnected: "%s" to "%s"' % (sourceAttr, newLambert))
                else:
                    self.addLog('disconnected: "%s" from "%s"' % (lam1_attr, sourceAttr))
        if newLambert and not objs_lamb1:
            pm.delete(newLambert)

        # refresh lambert check
        self.ref_lambert1()

        # if objs_lamb1:
        #    pm.select(objs_lamb1)

    def fixHighGrpOverride(self, *args):
        if not pm.objExists('high_grp'):
            self.printFeedback('Failed to find "high_grp"')
            return
        # high grp
        hGrp = pm.PyNode('high_grp')
        try:
            val = hGrp.overrideEnabled.get()
            if val != 1:
                hGrp.overrideEnabled.set(1)
        except:
            self.printFeedback('Failed to enable high_grp overrides')
        try:
            val = hGrp.overrideDisplayType.get()
            if val != 2:
                hGrp.overrideDisplayType.set(2)
        except:
            self.printFeedback('Failed to change high_grp overrideDisplayType to reference')
        # high grp children override and display type
        childs = pm.listRelatives(hGrp, ad=True, noIntermediate=True)
        for ch in childs:
            try:
                ch.overrideEnabled.set(0)
            except:
                self.printFeedback('Failed to update "%s.overrideEnabled"' % ch.name())
            try:
                ch.overrideDisplayType.set(2)
            except:
                self.printFeedback('Failed to update "%s.overrideDisplayType"' % ch.name())
        self.ref_hGrpOverride()

    def fixUnloadedRefs(self, *args):
        ref_list = cmds.file(q=True, r=True)
        for ref in ref_list:
            loaded = pm.referenceQuery(ref, il=True)
            if not loaded:
                name = pm.referenceQuery(ref, rfn=True)
                cmds.file(loadReference=name)
                self.addLog('Refernce "%s" loaded successfully' % name)
        self.ref_references()

    def removeUnloadedRefs(self, *args):
        # todo if not prop/set remove all references?
        ref_list = cmds.file(q=True, r=True)
        for ref in ref_list:
            loaded = pm.referenceQuery(ref, il=True)
            if not loaded:
                name = pm.referenceQuery(ref, rfn=True)
                cmds.file(ref, removeReference=True)
                self.addLog('Refernce "%s" removed successfully' % name)
        self.ref_references()

    def removeNgSkinTools(self, *args):
        gmt.removeNgSkinTools()
        self.ref_ngSkinTools()

    def resetUI(self, *args):
        self.endProgBar()
        for field in self.fieldsDefault:
            self.updateTextFramesStat(field, default=True)
        if pm.checkBox(self.widgets['clearLog'], q=True, v=True):
            self.clearLog()
        else:
            cmds.scrollField(self.widgets["log"], e=True, ip=0)

    def refAssetDetails(self):
        fileName = cmds.file(q=True, sn=True, shn=True)
        if '_rigging.' in fileName:
            assetName = fileName.rpartition('_rigging.')[0]
        else:
            assetName = fileName.rpartition('.')[0]
        qLoc = cmds.file(q=True, loc=True)
        assetType = ''
        if 'assets' not in qLoc:
            self.addLog('Unfamiliar path for current file')
            error = 'Asset type not found, select manually'
            self.addLog(error)
            self.orangeFeedback(error)
        else:
            temp = qLoc.partition('assets/')[2]
            parts = temp.partition('/')
            assetType = parts[0]
            assetName = parts[2].partition('/')[0]
        # update asset name
        cmds.textField(self.widgets['assetName'], e=True, tx=assetName)

        if assetType in self.assetTypes:
            sel = self.assetTypes.index(assetType) + 1
            pm.optionMenu(self.widgets['assetType'], e=True, sl=sel)  # , cc=self.updateCharVar)
        return assetName, assetType

    def refreshUIasset(self, *args):
        assetName, assetType = self.refAssetDetails()
        self.updateAssetType()

    def resetProgBar(self, two=False):
        if not self.barLength:
            self.barLength = 1
        if not self.barLength2:
            self.barLength2 = 1
        if two:
            pm.progressBar(self.widgets['progBar2'], edit=True, endProgress=True)
            pm.progressBar(self.widgets['progBar2'], edit=True, beginProgress=True, maxValue=self.barLength2)
        else:
            pm.progressBar(self.widgets['progBar'], edit=True, endProgress=True)
            pm.progressBar(self.widgets['progBar'], edit=True, beginProgress=True, maxValue=self.barLength)
            pm.progressBar(self.widgets['progBar2'], edit=True, endProgress=True)
            pm.progressBar(self.widgets['progBar2'], edit=True, beginProgress=True, maxValue=self.barLength2)
        field = 'progBar'
        if two:
            field = 'progBar2'
        pm.progressBar(self.widgets[field], edit=True, endProgress=True)
        pm.progressBar(self.widgets[field], edit=True, beginProgress=True, maxValue=self.barLength)

    def resetProgBar2(self, barLength):
        self.barLength2 = barLength
        self.resetProgBar(True)

    def stepProgBar(self, two=False):
        field = 'progBar'
        if two:
            field = 'progBar2'
        pm.progressBar(self.widgets[field], edit=True, step=1)

    def endProgBar(self, two=False):
        if two:
            pm.progressBar(self.widgets['progBar2'], edit=True, endProgress=True)
        else:
            pm.progressBar(self.widgets['progBar'], edit=True, endProgress=True)
            pm.progressBar(self.widgets['progBar2'], edit=True, endProgress=True)

    def addTimeStamp(self, start=True):
        if start:
            self.addLog('- - Start Log : ' + pm.date() + ' - - -')
        else:
            self.addLog('- - End Log : ' + pm.date() + ' - - -')

    def clearLog(self):
        cmds.scrollField(self.widgets["log"], e=True, text='')

    def addLog(self, logTx, headline=False, fix=False, space=0):
        sp = ''
        for i in range(0, space):
            sp += '    '
        if headline:
            logTx = ('\n-------------------------------------------------------'
                     '\n  ---  %s  ---'
                     '\n-------------------------------------------------------' % logTx)
            # logTx = '\n--------    %s    --------' % logTx
        elif fix:
            logTx = sp + ' **  %s  ' % logTx
        else:
            if logTx:
                logTx = sp + ' - %s' % logTx
        cmds.scrollField(self.widgets["log"], e=True, it=logTx + "\n")

    def addSpace(self, add):
        if add:
            self.addLog('')
        return

    def addLogHeader(self, field):
        logTx = self.logHeaders[field]
        self.addLog(logTx, headline=True)

    def updateTextFramesStat(self, field, fieldNote='', red=False, green=False, yellow=False, default=False):
        bgc = [.25, .25, .25]
        if default:
            fieldNote = self.fieldsDefault[field]
        else:
            if green:
                bgc = [.3, .6, .3]
            if red:
                bgc = [1, .4, .4]
            if yellow:
                bgc = [0.78, 0.7, .0]
        cmds.textField(self.widgets[field], e=True, tx=fieldNote, bgc=bgc)

    def getAssetType(self):
        idx = pm.optionMenu(self.widgets['assetType'], q=True, sl=True) - 1
        return self.assetTypes[idx]

    def selectItems(self, items, add=False, *args):
        sele = []
        bad = []
        for item in items:
            if pm.objExists(item):
                sele.append(item)
            else:
                bad.append(item)
        if bad:
            self.printFeedback('Error selecting the following: %s' % bad)
        if add:
            pm.select(sele, add=True)
        else:
            pm.select(sele)

    def addSelSet(self, mainLay, items, sidesW=60):
        pm.rowLayout(nc=3, columnOffset2=[0, 5], adjustableColumn=3, p=mainLay)
        pm.button('Select', c=partial(self.selectItems, items), w=sidesW)
        pm.button('Add', c=partial(self.selectItems, items, True), w=sidesW)
        pm.rowColumnLayout(nc=1, adj=True)
        num0 = .3
        num1 = .23
        bgc = {0: [num0, num0, num0],
               1: [num1, num1, num1]}
        i = 0
        for item in items:
            pm.text(l='     "%s"     ' % item, al='left', bgc=bgc[i])
            if i:
                i = 0
            else:
                i += 1
        pm.separator(h=7, p=mainLay)

    def selectNamingWin(self, *args):
        if not (self.doubles_hGrp or self.doubles_guides or self.doubles_general):
            self.orangeFeedback('No naming issues to select')
            return
        winName = "Sel_window"
        if cmds.window(winName, exists=True):
            cmds.deleteUI(winName)
        self.widgets[winName] = cmds.window(winName, title='Selection Window', sizeable=1, rtf=True)
        mainLay = pm.scrollLayout(childResizable=True)
        # mainLay = pm.rowColumnLayout()
        pm.separator(h=7, p=mainLay)
        pm.text(l='Select Naming doubles Window', font='boldLabelFont', p=mainLay, w=220)
        pm.separator(h=7, p=mainLay)
        # populate
        bgc = [.2, .2, .2]
        for itemsDict, header in [[self.doubles_hGrp, 'high_grp naming clashes:'],
                                  [self.doubles_guides, 'Guide naming clashes']]:
            if not itemsDict:
                continue
            pm.separator(h=3, style='none', p=mainLay, bgc=bgc)
            pm.text(l=header, p=mainLay, bgc=bgc)
            pm.separator(h=7, p=mainLay, bgc=bgc)
            for mainItem in itemsDict:
                items = [mainItem]
                for item in itemsDict[mainItem]:
                    items.append(item)
                self.addSelSet(mainLay, items)
        if self.doubles_general:
            pm.separator(h=3, style='none', p=mainLay, bgc=bgc)
            pm.text(l='General naming clashes:', p=mainLay, bgc=bgc)
            pm.separator(h=7, p=mainLay, bgc=bgc)
            for items in self.doubles_general:
                self.addSelSet(mainLay, self.doubles_general[items])
        cmds.showWindow()

    def selectFieldItems(self, field, *args):
        forPrint = self.widgets[field + '_items']
        if not forPrint:
            self.orangeFeedback('Nothing to select')
            return
        if isinstance(forPrint, list) or isinstance(forPrint, tuple):
            forPrint = gmp.cleanListForPrint(forPrint)
        else:
            forPrint = '"%s"' % forPrint
        self.printFeedback('selecting %s' % forPrint, 'none')
        if not self.widgets[field + '_items']:
            self.orangeFeedback('No items found to select')
            return
        pm.select(cl=True)
        for obj in self.widgets[field + '_items']:
            if pm.objExists(obj):
                pm.select(obj, add=True)

    def deleteItems(self, field, *args):
        delItems = self.widgets[field + '_items']
        if not delItems:
            self.orangeFeedback('No items found to delete')
            return
        note = 'deleting items: %s' % delItems
        self.printFeedback(note, 'none')
        self.addLog(note)
        pm.delete(delItems)
        if field == 'vray':
            self.ref_vray()
        elif field == 'guide':
            self.ref_guide()

    def stepsLayBase(self, parLay, header, field, fix, select, delete=False):
        lay = pm.rowLayout(nc=5, columnOffset2=[0, 5], adjustableColumn=3, p=parLay)
        h = 25
        pm.text(header, bgc=[.15, .15, .15], w=80, h=h)
        # button layout
        cmds.rowColumnLayout(nc=2, adj=True, cs=[2, 3], p=lay)
        fixBut = ''
        selBut = ''
        butW = 42
        if fix:
            fixBut = pm.button(l='Fix', w=butW, h=h)
            if delete:
                pm.button(fixBut, e=True, l='Delete', c=partial(self.deleteItems, field))
        else:
            pm.separator(style='none', w=butW)
        if select:
            selBut = pm.button(l='Select', w=butW, h=h, c=partial(self.selectFieldItems, field))
            self.widgets[field + '_items'] = []
        else:
            pm.separator(style='none', w=butW)

        # field and checkBox + check button
        self.widgets[field] = cmds.textField(tx=self.fieldsDefault[field], editable=False, h=h, p=lay)
        self.widgets[field + 'chBox'] = pm.checkBox(l='', v=1, p=lay)
        pm.button(l='check', c=partial(self.do_checks, field, True), p=lay)
        return fixBut, selBut

    def addHierarchyIntSlider(self, parLay):
        self.widgets['hierStepsLay'] = pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=parLay)
        h = 25
        pm.text(' Child steps from deform (sets): ', bgc=[.15, .15, .15], h=h)  # , w=170
        self.widgets['hierIntField'] = pm.intSliderGrp(field=True, v=self.tooFarSteps, minValue=1, maxValue=6,
                                                       fieldMinValue=1, fieldMaxValue=99)

    def checkBoxUpdate(self, val=0, *args):
        for field in self.fieldsOrder:
            pm.checkBox(self.widgets[field + 'chBox'], e=True, v=val)

    def steps_shelf(self, parLay):
        bgc = [.25, .25, .25]
        butBgc = [.4, .4, .4]
        butH = 16
        headerLay = pm.rowLayout(nc=3, adjustableColumn=1, p=parLay, bgc=bgc)  # , columnOffset2=[0, 5]
        butW = 75
        pm.separator(h=7, style='none')
        pm.button(l='check all', c=partial(self.checkBoxUpdate, 1), h=butH, w=butW, bgc=butBgc)
        pm.button(l='none', c=self.checkBoxUpdate, h=butH, w=butW, bgc=butBgc)

    def populate_steps(self, parLay):
        self.steps_shelf(parLay)

        self.addHierarchyIntSlider(parLay)

        buttons_dict = {}
        buttons_dict2 = {}
        fields_data_list = [
            ['hierarchy', 'hierarchy', 'Hierarchy issues', False, True],
            ['hGrpOverride', 'Override', 'high_grp Override issues', True, True],
            ['hGrpVals', 'Transform Vals', 'Found Obj values under "high_grp"', False, True],
            ['animKeys', 'Anim Keys', 'Found animation Keys under "main"', False, True],
            ['ctlVals', 'Ctrl Values', 'Found transform values under controllers', False, True],
            ['mainCns', 'Cns ctls', 'cns ctls issues', False, True],
            ['lambert1', 'lambert1', 'lambert1 issues', True, True],
            ['vray', 'vRay', 'vRay nodes found', True, True],
            ['cAttrs', 'c_ attrs', '"c_" attributes issues', False, False],
            ['guide', 'guide', 'guides found in scene', True, True],
            ['naming', 'naming', 'Naming issues', True, True],
            ['nameSpaces', 'Name Spaces', 'Namespace / reference issues', False, True],
            ['assembly', 'assembly', 'Assembly issues', False, False],
            ['references', 'references', 'Reference issues found', True, True],
            ['ngSkinTools', 'ngSkinTools', 'ngSkinTools nodes found', True, True],
        ]
        self.barLength = len(fields_data_list)
        self.fieldsDefault = {
            'hierarchy': 'Check hierarchy',
            'hGrpOverride': 'Check high_grp Override',
            'hGrpVals': 'Find values under "high_grp"',
            'animKeys': 'Find animation Keys under "main"',
            'ctlVals': 'Find transform values under controllers',
            'mainCns': 'Check cns ctls',
            'lambert1': 'Check lambert1',
            'vray': 'Check for vRay nodes',
            'cAttrs': 'Check for c_ attributes',
            'guide': 'Check for guides in scene',
            'naming': 'Check for naming issues',
            'nameSpaces': 'Check Namespaces, references and Assembly issues',
            'assembly': 'Check assembly',
            'references': 'Check references issues',
            'ngSkinTools': 'Check for ngSkinTool nodes'
        }
        delButton = ['vray', 'guide', 'ngSkinTools']
        self.fieldsOrder = []
        for field, header, tx, fix, select in fields_data_list:
            self.fieldsOrder.append(field)
            self.logHeaders[field] = tx
            if field in delButton:
                but1, but2 = self.stepsLayBase(parLay, header, field, fix, select, True)
            else:
                but1, but2 = self.stepsLayBase(parLay, header, field, fix, select)
            buttons_dict[field] = but1
            buttons_dict2[field] = but2
        pm.button(buttons_dict['hGrpOverride'], e=True, c=self.fixHighGrpOverride)
        pm.button(buttons_dict['lambert1'], e=True, c=self.fixLambert1)
        pm.button(buttons_dict2['naming'], w=80, e=True, l='Select Win', c=self.selectNamingWin)
        pm.button(buttons_dict['naming'], w=4, vis=False, e=True)
        pm.button(buttons_dict['references'], e=True, l='Remove', c=self.removeUnloadedRefs)
        pm.button(buttons_dict2['references'], e=True, l='Reload', c=self.fixUnloadedRefs)
        pm.button(buttons_dict['ngSkinTools'], e=True, l='Remove', c=self.removeNgSkinTools)

    def updateAssetType(self, *args):
        # updated fixer ui
        assetType = self.getAssetType()
        self.finalizer.setMainAttrCtl(assetType)
        # show steps slider
        if 'set' in assetType:
            pm.rowLayout(self.widgets['hierStepsLay'], e=True, enable=True)
        else:
            pm.rowLayout(self.widgets['hierStepsLay'], e=True, enable=False)

    def layoutAssetDetails(self, mainLay):
        pm.rowLayout(nc=3, columnOffset2=[0, 5], adjustableColumn=2, p=mainLay)
        sidesW = 75
        pm.separator(style='none', w=sidesW)
        pm.button('1 - Refresh Asset', c=self.refreshUIasset)
        pm.separator(style='none', w=sidesW)
        pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=mainLay)
        pm.text('  Asset Name   ')
        self.widgets['assetName'] = cmds.textField()

        pm.separator(h=3, style='none', p=mainLay)

        self.widgets['assetType'] = pm.optionMenu(label='  Asset Type    ', w=300, h=20,
                                                  p=mainLay, cc=self.updateAssetType)

        for aType in self.assetTypes:
            pm.menuItem(label=aType)
        # refresh button
        pm.separator(h=5, p=mainLay)
        lay = pm.rowLayout(nc=4, columnOffset2=[0, 5], adjustableColumn=2, p=mainLay)
        pm.columnLayout(rowSpacing=1)
        self.widgets['progBar'] = pm.progressBar(w=sidesW)
        self.widgets['progBar2'] = pm.progressBar(w=sidesW, h=10)
        pm.button('2 - Check / Refresh Checklist', h=30, c=self.runFinalizer, p=lay)
        pm.separator(style='none', w=5, p=lay)
        self.widgets['clearLog'] = pm.checkBox(l='Clear Log', v=1, p=lay)

    def populateUI(self, topLay):
        form = pm.formLayout(p=topLay)
        self.widgets["top_tabLayout"] = cmds.tabLayout()  # childResizable=True)#, p=topLay)
        tab = self.widgets["top_tabLayout"]
        pm.formLayout(form, e=True, af=((tab, 'top', 0), (tab, 'left', 0),
                                        (tab, 'right', 0), (tab, 'bottom', 0)))

        form = pm.formLayout('Check List', p=tab)
        scroll = pm.scrollLayout(childResizable=True)
        mainLay = pm.rowColumnLayout(nc=1, adj=True)
        pm.formLayout(form, e=True, af=((scroll, 'top', 0), (scroll, 'left', 0),
                                        (scroll, 'right', 0), (scroll, 'bottom', 0)))

        # right side
        form = pm.formLayout(p=topLay)
        self.widgets['log'] = cmds.scrollField()
        log = self.widgets['log']
        pm.formLayout(form, e=True, af=((log, 'top', 0), (log, 'left', 0),
                                        (log, 'right', 0), (log, 'bottom', 0)))

        # left side
        pm.separator(h=3, p=mainLay)
        headerLay = pm.rowLayout(nc=3, columnOffset2=[0, 5], adjustableColumn=2, p=mainLay)
        sidesW = 75
        midW = 220 - sidesW * 2
        pm.separator(h=7, w=sidesW, style='none')
        pm.text(l='Rig Finalizer', font='boldLabelFont', w=midW)
        pm.button(l='Reset UI', c=self.resetUI, h=15, w=sidesW)

        return mainLay

    def winBase(self, name, title, par):
        winName = name + "_window"
        topLay = "topPane"
        asWindow = True
        if par:
            print(' // %s - creating Layout under parent' % self.feedbackName)
            asWindow = False
        if asWindow:
            if cmds.window(winName, exists=True):
                cmds.deleteUI(winName)
            self.widgets[winName] = cmds.window(winName, title=title, sizeable=1, rtf=True)
            form = pm.formLayout()
        else:
            form = pm.formLayout(p=par)

        # form and main split layout
        self.widgets['topForm'] = form
        self.widgets[topLay] = cmds.paneLayout(configuration='vertical2', staticWidthPane=1)
        mLay = self.widgets[topLay]
        pm.formLayout(form, e=True, af=((mLay, 'top', 0), (mLay, 'left', 0),
                                        (mLay, 'right', 0), (mLay, 'bottom', 30)))

        # feedback layout
        fLay = pm.columnLayout(adj=True, p=self.widgets['topForm'])
        pm.separator(h=7)  # , p=self.widgets[topLay])
        self.widgets["feedback"] = cmds.textField(tx="", editable=False)  # , p=self.widgets['topForm'])
        # feedback = self.widgets["feedback"]
        pm.formLayout(form, e=True, af=((fLay, 'left', 0),
                                        (fLay, 'right', 0), (fLay, 'bottom', 0)))
        if asWindow:
            cmds.showWindow()
        self.defaultFeedback()
        return self.widgets[topLay]

    def defaultFeedback(self):
        self.changeFeedback('// %s' % self.feedbackName)

    def printFeedback(self, text, color=''):
        error = ' // %s : %s' % (self.feedbackName, text)
        print(error)
        fColor = 'red'
        if color:
            fColor = color
        self.changeFeedback(error, fColor)

    def greenFeedback(self, text):
        self.printFeedback(text, 'green')

    def orangeFeedback(self, text):
        self.printFeedback(text, 'orange')

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.7, .3, .3)
            bg = [1, .4, .4]
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedback"], e=True, bgc=bg, tx=messege)
