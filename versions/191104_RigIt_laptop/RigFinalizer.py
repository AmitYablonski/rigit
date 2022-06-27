from maya import cmds, mel
import pymel.core as pm
from functools import partial
import fnmatch
import UI_modules as uim
import RigItMethodsUI as rim
import traceback


class RigFinalizer:
    def __init__(self, par='', scriptIt=False):
        self.widgets = {}
        self.feedbackName = 'Rig Finalizer'
        topLay, mainLay = self.winBase('RigFinalizer', self.feedbackName, par)
        self.assetTypes = ["characters", "variants", "set", "props"]
        self.defaultFieldText = {}
        self.logHeaders = {}
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def execute(self, *args):
        self.defaultFeedback()
        radio_input = pm.radioButtonGrp(self.widgets['cnsRadio'], q=1, select=1)
        radio_input -= 1
        # todo ? assetType = pm.optionMenu(self.widgets['assetType'], q=True, sl=True)

        self.create_cns(radio_input)
        self.finalize_rig()

    def scriptIt(self, *args):
        self.defaultFeedback()
        script = 'This needs to be done'
        rim.showScript(script)
        return

    '''
    def addCnsAttr(self, gloabl):
        try:
            pm.addAttr(gloabl, ln="ShowCnsCtrls", at="double", dv=0, min=0, max=1)
            pm.setAttr((gloabl + ".ShowCnsCtrls"), e=1, keyable=False, cb=1)
            pm.setAttr((gloabl + ".ShowCnsCtrls"), 0)
        except:
            error = '%s\n%s' % (traceback.print_exc(), '{} has cns show attribute'.format(gloabl.name()))
            self.printFeedback(error, 'none')

    def addCns(self, gloabl, ctl):  # todo is it used? if so, import ic
        oParent = ctl.getParent()
        if not pm.objExists(ctl.name() + "_cns"):
            icon = ic.create(oParent, ctl.name() + "_cns", ctl.getMatrix(), [1, 0, 0], 'cross')
            icon.setTransformation(ctl.getMatrix())
            pm.parent(ctl, icon)
            iconShape = icon.getShape()
            pm.connectAttr(gloabl.ShowCnsCtrls, iconShape.visibility)
            self.printFeedback('[add cns controller] proccessed: {}'.format(ctl.name()))
        else:
            self.printFeedback('[add cns controller] already exists: {}'.format(ctl.name()))

    def create_cns(self, selected=False):
        ctls = pm.ls('*_ctl')
        if selected:
            excList = pm.ls(sl=True)
            temp = []
            for ctl in excList:
                if ctl in ctls:
                    temp.append(ctl)
            ctls = temp

        gloabl = pm.PyNode('global_C0_ctl')

        self.addCnsAttr(gloabl)

        for ctl in ctls:
            self.addCns(gloabl, ctl)

    def override_ref_on(self, item):
        pm.setAttr(item + ".overrideEnabled", 1)
        pm.setAttr(item + ".overrideDisplayType", 2)

    def finalize_rig(self):
        try:
            pm.setAttr("rig.jnt_vis", 0)
        except:
            self.printFeedback("rig.jnt_vis failed", 'none')

        pm.parent("rig", "main")
        hg = "high_grp"
        hg_items = pm.listRelatives(hg, c=1)
        for item in hg_items:
            self.override_ref_on(item)
            pm.select(item)
            mel.eval(
                'displaySmoothness -divisionsU 0 -divisionsV 0 -pointsWire 4 -pointsShaded 1 -polygonObject 1;')
            pm.select(cl=1)
    '''

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
        else:  # todo test in pipeline:
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

    def refHighGrpOverride(self, *args):
        field = 'hGrpOverride'
        self.updateTextFramesStat(field, default=True)
        idx = pm.optionMenu(self.widgets['assetType'], q=True, sl=True) - 1
        # check if high_grp locked and geo
        self.widgets[field + '_items'] = []
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
        if error:
            self.addLogHeader(field)
            if obj_highGrp:
                self.addLog('Override NOT Enabled for high_grp')
            if obj_override:
                self.addLog('Override Enabled for high_grp children/shapes')
            if obj_dispType:
                self.addLog('overrideDisplayType not Reference for high_grp objects')
            self.updateTextFramesStat(field, red=True, fieldNote='found high_grp errors - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='high_grp checked')

    def refHighGrpValues(self, *args):
        field = 'hGrpVals'
        self.updateTextFramesStat(field, default=True)
        self.widgets[field + '_items'] = []
        hGrp_ad = pm.listRelatives('high_grp', ad=True, s=False, typ='transform')
        hGrp_ad.append('high_grp')
        objs_to_fix = []
        for obj in hGrp_ad:
            for atr in 'trs':
                for axi in 'xyz':
                    value = pm.getAttr(obj + '.' + atr + axi)
                    if atr != 's':
                        if round(abs(value)) > 0.0:
                            if str(obj) not in objs_to_fix:
                                objs_to_fix.append(obj)

                    else:
                        if round(abs(value)) > 1.0:
                            if str(obj) not in objs_to_fix:
                                objs_to_fix.append(obj)
        if objs_to_fix:
            self.addLogHeader(field)
            for obj in objs_to_fix:
                self.widgets[field + '_items'].append(obj)
                self.addLog('Found vals on "%s"' % obj)
            self.updateTextFramesStat(field, red=True, fieldNote='found high_grp Values - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='clean high_grp values')

    def refAnimKeys(self):
        field = 'animKeys'
        self.updateTextFramesStat(field, default=True)
        try:
            main = pm.PyNode('main')
        except:
            self.addLog('\n\n- - - - Cancelled anim keys search! - - - -\n'
                        '- -  Can\'t find "main" -- skipped step  - -')
            self.updateTextFramesStat(field, red=True, fieldNote='Can\'t find "main" - skipped step')
            return
        main_ad = pm.listRelatives(main, ad=True, s=False, typ='transform')
        obj_keys_list = []
        for obj in main_ad:
            animCrvs = pm.listConnections(obj, type='animCurve', d=False, s=True)
            for con in animCrvs:
                conType = con.type()
                if 'animCurveU' not in conType:
                    obj_keys_list.append(obj)
        if obj_keys_list:
            self.addLogHeader(field)
            for obj in obj_keys_list:
                self.addLog('Found animation on "%s"' % obj)
            self.widgets[field + '_items'] = obj_keys_list
            self.updateTextFramesStat(field, red=True, fieldNote='found animation keys - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No animation found under "main"')

    def refCtlCns(self):
        field = 'mainCns'
        cnsFixList = []
        missins_cns = []
        disconnected_cns = []
        # todo currently checks only ctls in list.
        main_ctls = ['global_C0_ctl', 'local_C0_ctl', 'control_C0_ctl', 'asmLocal_C0_ctl']
        for ctl in main_ctls:
            if pm.objExists(ctl):
                if not pm.objExists(ctl + '_cns') and not pm.objExists(ctl + '_cns_ctl'):
                    missins_cns.append(ctl)
                    cnsFixList.append(ctl)
        # finds existing ctls with shapes and check if they're connected
        cnsLs = pm.ls(['*_cns', '*_cns_ctl'])
        for cns in cnsLs:
            conn = pm.listConnections(cns.v, p=True)
            if 'ShowCnsControls' not in conn:
                shp = cns.getShape()
                if shp:
                    conn = pm.listConnections(shp.v, p=True)
                    if 'ShowCnsControls' not in conn:
                        disconnected_cns.append(shp)
                        cnsFixList.append(cns)
        # feedback
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

    def refLambert1(self):
        field = 'lambert1'
        error = False
        objs_lamb1 = []
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
        highG_shps = pm.listRelatives('high_grp', ad=True, type='mesh')
        lamb1_cons = pm.listConnections('initialShadingGroup', p=True)
        for con in lamb1_cons:
            if 'instObjGroups' in con.name():
                shp = pm.PyNode(con.name().partition('.instObjGroups')[0])
                if shp in highG_shps:
                    # obj = shp.getParent()
                    addCtl = shp  # todo used to print the shp and select object
                    if addCtl not in objs_lamb1:
                        objs_lamb1.append(addCtl)
                        error = True

        if objs_lamb1:
            self.widgets[field + '_items'] = objs_lamb1
        else:
            self.widgets[field + '_items'] = []
        if error:
            self.addLogHeader(field)
            for lam1_attr, sourceAttr in cons_lamb1:
                self.addLog('connection found: "%s" from "%s"' % (lam1_attr, sourceAttr))
            if not colorOK:
                self.addLog('lamber1 color isn\'t set to default (default is [0.5, 0.5, 0.5])')
            for obj in objs_lamb1:
                self.addLog('"%s" is associated to lambert1' % obj)
            self.updateTextFramesStat(field, red=True, fieldNote='found lambert1 issues - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No lambert1 issues found')

    def refVRay(self):
        field = 'vray'
        vray_nodes = pm.ls('*vray*')  # todo another search?
        self.widgets[field + '_items'] = vray_nodes
        if vray_nodes:
            self.addLogHeader(field)
            self.addLog('Found vray nodes is scene')
            self.updateTextFramesStat(field, red=True, fieldNote='found vRay nodes - see log')
        else:
            self.widgets[field + '_items'] = []
            self.updateTextFramesStat(field, green=True, fieldNote='No vRay nodes found')

    def refVRay(self):
        field = 'vray'
        # custom attrs on high_grp [not perfect, still needs to check attrs without c_ ]
        # todo check if other costum attributes on high_grp (with wrong naming)
        hGrp_attrs = pm.listAttr('high_grp')
        # todo filter all basic attrs and
        custom_attrs = []
        vray_nodes = ''
        for attr in hGrp_attrs:
            if 'c_' in attr:
                cons = pm.listConnections('high_grp' + '.' + attr, p=True)
                if len(cons):
                    for con in cons:
                        gCtl = con.rpartition('.')[0]
                        if gCtl == 'global_C0_ctl':
                            print
                            'global'
                            s_attr = con.rpartition('.')[2]
                            if 'c_' + s_attr == attr:
                                print
                                'custom attributes match'
                            else:
                                print
                                'custom attributes dont match'
                                custom_attrs.append(attr + " [connected but name doesn't match]")
                else:
                    'not connected'
                    custom_attrs.append(attr + " [not connected to ctl]")

        self.widgets[field + '_items'] = custom_attrs
        if vray_nodes:
            self.addLogHeader(field)
            self.addLog('Found vray nodes is scene')
            self.updateTextFramesStat(field, red=True, fieldNote='Found vRay nodes - see log')
        else:
            self.widgets[field + '_items'] = []
            self.updateTextFramesStat(field, green=True, fieldNote='No vRay nodes found')

    def refUnloadedRef(self):  # todo test this, see if something to add
        field = 'unloadedRef'
        self.updateTextFramesStat(field, default=True)
        ref_errors = []
        ref_list = cmds.file(q=True, r=True)
        for ref in ref_list:
            name = pm.referenceQuery(ref, rfn=True)
            loaded = pm.referenceQuery(ref, il=True)
            if not loaded:
                ref_errors.append(name)  # + ' [unloaded]')
        if ref_errors:
            self.addLogHeader(field)
            for error in ref_errors:
                self.addLog(error)
            self.updateTextFramesStat(field, red=True, fieldNote='Unloaded references found - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No Unloaded references found')

    def refAssembly(self):
        field = 'assembly'
        self.updateTextFramesStat(field, default=True)
        asm_errors = []
        ref_list = pm.ls('*:*')
        if len(ref_list):
            if pm.objExists('assembly') != True:  # todo check if assembly is of the correct type?
                asm_errors.append('"assembly" node is missing - References found in scene')
        if asm_errors:
            self.addLogHeader(field)
            for error in asm_errors:
                self.addLog(error)
            self.updateTextFramesStat(field, red=True, fieldNote='Assembly issues found - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No Assembly issues found')

    def isTooFarFromParent(self, obj, steps, amt=0, par='', printLog=False):
        #print('0 isTooFarFromParent(%s, %s, %s, %s, %s)' % (obj, steps, amt, par, printLog))
        if not amt:
            amt = steps
            par = obj
        ch = pm.listRelatives(obj, c=True, s=False)
        if ch:
            if not steps:
                print 'too far!', obj
                if printLog:
                    self.addLog('children under "%s" are more than %s steps away from %s' % (obj, amt, par))
                else:
                    return True
            for c in ch:
                tooFar = self.isTooFarFromParent(c, steps - 1, amt, par, printLog)
                if tooFar and printLog: # todo !! you were here !! fix adding to log etc
                    return True
                else:
                    self.isTooFarFromParent(c, steps - 1, amt, par, printLog)
        '''
        print('0 isTooFarFromParent(%s, %s, %s, %s, %s)' % (obj, steps, amt, par, printLog))
        if not amt:
            amt = steps
            par = obj
        ch = pm.listRelatives(obj, c=True, s=False)
        if not ch:
            print('1 isTooFarFromParent(%s, %s, %s, %s, %s)' % (obj, steps, amt, par, printLog))
            return False
        if ch and not steps:
            if printLog:
                self.addLog('children under "%s" are more than %s steps away from %s' % (obj, amt, par))
            print('2 isTooFarFromParent(%s, %s, %s, %s, %s)' % (obj, steps, amt, par, printLog))
            return True
        for c in ch:
            self.isTooFarFromParent(c, steps - 1, amt, par, printLog)
        '''

    def refHierarchy(self):  # todo hierarchy checkups - other than sets
        # todo test if nothing is outside of main (apart from sets?)
        field = 'hierarchy'
        self.updateTextFramesStat(field, default=True)
        idx = pm.optionMenu(self.widgets['assetType'], q=True, sl=True) - 1
        assetType = self.assetTypes[idx]
        tooFar = False
        steps = cmds.intSliderGrp(self.widgets['hierIntField'], q=True, v=True)
        if self.isTooFarFromParent('high_grp', steps):
            tooFar = True
        hierarchy_errors = []
        # "characters", "variants", "set", "props"
        self.widgets[field + '_items'] = []
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
        # todo if set, check if transform/deform correct (skinned etc)
        if assetType == 'set':
            for obj in ['deform', 'transform']:
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
                            hierarchy_errors.append('"%s" should be child of "high_grp"' % obj)
                            self.widgets[field + '_items'].append(obj)
                else:
                    hierarchy_errors.append('"%s" group not found' % obj)
        # todo test hierarchy also for none sets
        if hierarchy_errors:
            self.addLogHeader(field)
            for error in hierarchy_errors:
                self.addLog(error)
            if tooFar:
                self.isTooFarFromParent('high_grp', steps, printLog=True)
            self.updateTextFramesStat(field, red=True, fieldNote='Hierarchy issues found - see log')
        else:
            self.updateTextFramesStat(field, green=True, fieldNote='No Hierarchy issues found')

    def refGuide(self):
        field = 'guide'
        self.updateTextFramesStat(field, default=True)
        guides = pm.ls('*guide*', type='transform')
        if guides:
            self.addLogHeader(field)
            for guide in guides:
                self.addLog('guide found: "%s"' % guide)
            self.widgets[field + '_items'] = guides
            self.updateTextFramesStat(field, red=True, fieldNote='Guides found - see log')
        else:
            self.widgets[field + '_items'] = []
            self.updateTextFramesStat(field, green=True, fieldNote='No guides found')

    def refCAttrs(self):
        field = 'cAttrs'
        self.updateTextFramesStat(field, default=True)
        errors = []
        obj = pm.PyNode('high_grp')
        allAttrs = pm.listAttr(obj, r=1, s=1, k=1)
        removeAttrs = fnmatch.filter(allAttrs, "visibility")
        for channel in ['translate', 'rotate', 'scale']:
            removeAttrs = removeAttrs + fnmatch.filter(allAttrs, "%s*" % channel)
        for attr in removeAttrs:
            allAttrs.remove(attr)
        if not allAttrs:
            # self.addLog('No unique attributes found on "%s"' % obj)
            self.updateTextFramesStat(field, green=True, fieldNote='No unique attrs found')
            return

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
        if errors:
            self.addLogHeader(field)
            for error in errors:
                self.addLog(error)
            self.updateTextFramesStat(field, red=True, fieldNote='found c_attr errors - see log')

    def fixUnloadedRefs(self, *args):
        ref_list = cmds.file(q=True, r=True)
        for ref in ref_list:
            loaded = pm.referenceQuery(ref, il=True)
            if not loaded:
                name = pm.referenceQuery(ref, rfn=True)
                cmds.file(loadReference=name)
                self.addLog('Refernce "%s" loaded successfully' % name)
        self.refUnloadedRef()

    def removeUnloadedRefs(self, *args):
        ref_list = cmds.file(q=True, r=True)
        for ref in ref_list:
            loaded = pm.referenceQuery(ref, il=True)
            if not loaded:
                name = pm.referenceQuery(ref, rfn=True)
                cmds.file(ref, removeReference=True)
                self.addLog('Refernce "%s" removed successfully' % name)
        self.refUnloadedRef()

    def fixLambert1(self, *args):
        lam1 = pm.PyNode('lambert1')

        conn = pm.listConnections(lam1, s=True, d=False, p=True, c=True)
        if conn:
            for lam1_attr, sourceAttr in conn:
                pm.disconnectAttr(sourceAttr, lam1_attr)
                self.addLog('disconnected: "%s" from "%s"' % (lam1_attr, sourceAttr))

        lam1.color.set([.5, .5, .5])

        self.refLambert1()

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
        self.refHighGrpOverride()

    def refreshUIasset(self, *args):
        assetName, assetType = self.refAssetDetails()

    def refreshUI(self, *args):
        self.defaultFeedback()
        # todo progress bar ?
        if pm.checkBox(self.widgets['clearLog'], q=True, v=True):
            self.clearLog()
        # base hierarchy
        self.refHierarchy()
        # todo fix: props: place grp under main and so, set: fix names and under main
        # high_grp stuff (override)
        self.refHighGrpOverride()
        # step 03 - values on ctls
        self.refHighGrpValues()
        # step 04 - animation keyframes
        self.refAnimKeys()
        # todo fix: zero out ctls and delete keyframes?
        # step 05 - CNS for main ctrls
        self.refCtlCns()
        # todo fix: create cns for main ctls
        # step 06 - Lambert 1 clean
        self.refLambert1()
        # todo fix: create default mtl and replace connections
        # step 07 - Vray nodes
        self.refVRay()
        # step 08 - custom attrs on high_grp [not done, still needs to check attrs without c_ ]
        self.refCAttrs()
        # todo fix: edit high_grp attrs to match the ones on global_Ctl and/or reconnect
        # step 09 - guide
        self.refGuide()
        # todo fix: hide guide / if the name is worng there is no auto fix
        # step 11 - Assembly
        self.refAssembly()
        # todo take "add assembly" code from Lior
        # step 12 - Unloaded references
        self.refUnloadedRef()
        self.addLog('')
        self.addLog('- - - - - - - - - - - - - - - - - - - - - - - - - -')
        self.addLog('- - - - - - - - - - - - - - - - - - - - - - - - - -')
        self.addLog('')
        self.addLog('')

    def clearLog(self):
        cmds.scrollField(self.widgets["log"], e=True, text='')

    def addLog(self, logTx, headline=False, fix=False):
        if headline:
            logTx = ('\n-------------------------------------------------------'
                     '\n  ---  %s  ---'
                     '\n-------------------------------------------------------' % logTx)
            # logTx = '\n--------    %s    --------' % logTx
        elif fix:
            logTx = '  *  %s  *' % logTx
        else:
            if logTx:
                logTx = ' - %s' % logTx
        cmds.scrollField(self.widgets["log"], e=True, it=logTx + "\n")

    def addLogHeader(self, field):
        logTx = self.logHeaders[field]
        self.addLog(logTx, headline=True)

    def updateTextFramesStat(self, field, fieldNote='', red=False, green=False, default=False):
        bgc = [.25, .25, .25]
        if default:
            fieldNote = self.defaultFieldText[field]
        else:
            if green:
                bgc = [.3, .6, .3]
            if red:
                bgc = [.7, .3, .3]
        cmds.textField(self.widgets[field], e=True, tx=fieldNote, bgc=bgc)

    def selectItems(self, field, *args):
        self.printFeedback('selecting %s' % self.widgets[field + '_items'], 'none')
        if not self.widgets[field + '_items']:
            self.orangeFeedback('No items found to select')
            return
        pm.select(self.widgets[field + '_items'])

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
            self.refVRay()
        elif field == 'guide':
            self.refGuide()

    def stepsLayBase(self, parLay, header, field, fieldTx, fix, select, delete=False):
        lay = pm.rowLayout(nc=3, columnOffset2=[0, 5], adjustableColumn=3, p=parLay)
        h = 25
        pm.text(header, bgc=[.15, .15, .15], w=80, h=h)
        butLay = cmds.rowColumnLayout(nc=2, adj=True, cs=[2, 3], p=lay)
        # refBut = pm.button(l='Refresh')
        # selBut = pm.button(l='Show Items')
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
            selBut = pm.button(l='Select', w=butW, h=h, c=partial(self.selectItems, field))
            self.widgets[field + '_items'] = []
        else:
            pm.separator(style='none', w=butW)
        # mainLay = cmds.rowColumnLayout(nc=1, adj=True, p=lay)
        # cmds.rowColumnLayout(nc=1, adj=True, p=mainLay)
        self.widgets[field] = cmds.textField(tx=self.fieldsDefault[field], editable=False, h=h, p=lay)
        return fixBut, selBut

    def addHierarchyIntSlider(self, parLay):
        lay = pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=parLay)
        h = 25
        pm.text('Child steps from high_grp:', bgc=[.15, .15, .15], w=170, h=h)
        self.widgets['hierIntField'] = pm.intSliderGrp(field=True, v=4, minValue=1, maxValue=10,
                                                       fieldMinValue=1, fieldMaxValue=99)

    def populateSteps(self, parLay):
        self.addHierarchyIntSlider(parLay)
        buttonsDict = {}
        buttonsDict2 = {}
        allFieldsDict = [
            ['hierarchy', 'hierarchy', 'Hierarchy issues', False, True],
            ['hGrpOverride', 'high_grp', 'high_grp Override issues', True, True],
            ['hGrpVals', 'Transform Vals', 'Found values under "high_grp"', False, True],
            ['animKeys', 'Anim Keys', 'Found animation Keys under "main"', False, True],
            ['mainCns', 'Cns ctls', 'cns ctls issues', False, True],
            ['lambert1', 'lambert1', 'lambert1 issues', True, True],
            ['vray', 'vRay', 'vRay nodes found', True, True],
            ['cAttrs', 'c_ attrs', '"c_" attributes issues', False, False],
            ['guide', 'guide', 'guides found in scene', True, True],
            ['assembly', 'assembly', 'Assembly issues', False, False],
            ['unloadedRef', 'unloaded ref', 'Unloaded references found', True, True]
        ]
        self.fieldsDefault = {
            'hierarchy': 'Check hierarchy',
            'hGrpOverride': 'Check high_grp Override',
            'hGrpVals': 'Find values under "high_grp"',
            'animKeys': 'Find animation Keys under "main"',
            'mainCns': 'Check cns ctls',
            'lambert1': 'Check lambert1',
            'vray': 'Check for vRay nodes',
            'cAttrs': 'Check for c_ attributes',
            'guide': 'Check for guides in scene',
            'assembly': 'Check assembly',
            'unloadedRef': 'Check unloaded references'
        }
        delButton = ['vray', 'guide']
        for field, header, tx, fix, select in allFieldsDict:
            self.defaultFieldText[field] = tx
            self.logHeaders[field] = tx
            if field in delButton:
                but1, but2 = self.stepsLayBase(parLay, header, field, tx, fix, select, True)
            else:
                but1, but2 = self.stepsLayBase(parLay, header, field, tx, fix, select)
            buttonsDict[field] = but1
            buttonsDict2[field] = but2
            if field == 'lambert1':
                print(' // TODO: add lambert1 options')
                # todo add lambert1 replacement mtl
                # todo self.addLambert1Options() ?
        pm.button(buttonsDict['hGrpOverride'], e=True, c=self.fixHighGrpOverride)
        pm.button(buttonsDict['lambert1'], e=True, c=self.fixLambert1)
        # pm.button(buttonsDict['vray'], e=True, l='delete', c=partial(self.fixVRay, 'vray'))
        # pm.button(buttonsDict['guide'], e=True, l='delete', c=partial(self.fixVRay, 'vray'))
        pm.button(buttonsDict['unloadedRef'], e=True, l='Reload', c=self.fixUnloadedRefs)
        pm.button(buttonsDict2['unloadedRef'], e=True, l='Remove', c=self.removeUnloadedRefs)

    def layoutAssetDetails(self, mainLay):
        pm.rowLayout(nc=3, columnOffset2=[0, 5], adjustableColumn=2, p=mainLay)
        sidesW = 60
        pm.separator(style='none', w=sidesW)
        pm.button('1 - Refresh Asset', c=self.refreshUIasset)
        pm.separator(style='none', w=sidesW)
        pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=mainLay)
        pm.text('  Asset Name   ')
        self.widgets['assetName'] = cmds.textField()

        pm.separator(h=3, style='none', p=mainLay)

        self.widgets['assetType'] = pm.optionMenu(label='  Asset Type    ', w=300, h=20,
                                                  p=mainLay)  # , cc=self.updateCharVar)

        for aType in self.assetTypes:
            pm.menuItem(label=aType)
        # refresh button
        pm.separator(h=5, p=mainLay)
        pm.rowLayout(nc=4, columnOffset2=[0, 5], adjustableColumn=2, p=mainLay)
        pm.separator(style='none', w=sidesW)
        pm.button('2 - Check / Refresh Checklist', c=self.refreshUI)
        pm.separator(style='none', w=5)
        self.widgets['clearLog'] = pm.checkBox(l='Clear Log', v=1)

    def populateUI(self, parLay, scriptIt):
        topLay = cmds.paneLayout(configuration='vertical2', p=parLay)
        mainLay = cmds.rowColumnLayout(nc=1, adj=True)
        form = pm.formLayout(p=topLay)
        self.widgets['log'] = cmds.scrollField()
        log = self.widgets['log']
        pm.formLayout(form, e=True, af=((log, 'top', 0), (log, 'left', 0),
                                        (log, 'right', 0), (log, 'bottom', 0)))

        pm.separator(h=7, p=mainLay)
        pm.text(l='Rig Finalizer', font='boldLabelFont', p=mainLay, w=220)
        pm.separator(h=7, p=mainLay)

        self.layoutAssetDetails(mainLay)

        pm.separator(h=7, p=mainLay)

        stepsLay = cmds.scrollLayout(childResizable=True, p=mainLay)
        # stepsLay = cmds.rowColumnLayout(nc=1, adj=True)

        self.populateSteps(stepsLay)
        '''
        # todo cns part below ?
        self.widgets['cnsRadio'] = pm.radioButtonGrp(label='Create Cns: ', labelArray2=['All', 'Selected'],
                                                     numberOfRadioButtons=2, sl=1,
                                                     cal=[(1, "left"), (2, "left"), (3, "left")], cw3=(70, 50, 50),
                                                     p=mainLay)
        # todo execute buttons ?
        # buttons
        if scriptIt:
            # buttons
            cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
            cmds.button(l='Execute', h=28, c=self.execute)
            cmds.button(l='Script it', w=100, c=self.scriptIt)
        else:
            cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
            cmds.button(l='Step 3: Execute', h=28, p=mainLay, c=self.execute)
        '''

    def winBase(self, name, title, par):
        winName = name + "_window"
        mainLay = "mainLay"
        topLay = "topLay"
        asWindow = True
        if par:
            print(' // %s - creating Layout under parent' % self.feedbackName)
            asWindow = False
        if asWindow:
            if cmds.window(winName, exists=True):
                cmds.deleteUI(winName)
            self.widgets[winName] = cmds.window(winName, title=title, sizeable=1, rtf=True)
            self.widgets[topLay] = cmds.columnLayout(adj=True)
        else:
            self.widgets[topLay] = cmds.columnLayout(title, adj=True, p=par)
        self.widgets[mainLay] = cmds.columnLayout(adj=True)
        pm.separator(h=7, p=self.widgets[topLay])
        self.widgets["feedback"] = cmds.textField(tx="", editable=False, p=self.widgets[topLay])
        if asWindow:
            cmds.showWindow()
        self.defaultFeedback()
        return self.widgets[topLay], self.widgets[mainLay]

    def greenFeedback(self, text):
        self.printFeedback(text, 'green')

    def orangeFeedback(self, text):
        self.printFeedback(text, 'orange')

    def printFeedback(self, text, color=''):
        error = ' // %s : %s' % (self.feedbackName, text)
        print(error)
        fColor = 'red'
        if color:
            fColor = color
        self.changeFeedback(error, fColor)

    def defaultFeedback(self):
        self.changeFeedback('// %s' % self.feedbackName)

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.7, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedback"], e=True, bgc=bg, tx=messege)
