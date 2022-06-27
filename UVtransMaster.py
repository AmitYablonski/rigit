from maya import cmds, mel
import pymel.core as pm
from functools import partial
import UI_modules as uim
import generalMayaTools as gmt
import RigItMethodsUI as rim

reload(uim)
reload(gmt)
reload(rim)


class UVtransMaster:
    def __init__(self, par='', scriptIt=False):
        self.widgets = {}
        self.mapsDict = {}
        self.feedbackName = 'UV Transfer Master'
        # todo add progress bar
        topLay, mainLay = self.winBase('UVtransMaster', self.feedbackName, par)
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def mapFinderSwitcher(self, chBox, mapLay, chVal='', *args):
        val = pm.checkBox(chBox, q=True, v=True)
        pm.rowLayout(mapLay, e=True, enable=val)
        if chVal:
            cmds.radioButtonGrp(self.widgets["UVsets"], e=True, select=2)

    def addMapFinder(self, parLay, field, *args):
        pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=parLay)
        pm.separator(w=80, style='none')
        chBox = pm.checkBox(l='Select map')
        mapLay = pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=parLay, enable=False)
        pm.checkBox(chBox, e=True, cc=partial(self.mapFinderSwitcher, chBox, mapLay))
        but = pm.button(l='List Maps')
        optLay = pm.rowLayout(nc=1, adj=True)
        optMenu = pm.optionMenu()
        pm.button(but, e=True, c=partial(self.populateMapFinder, optLay, field))
        self.mapsDict[field] = [optLay, chBox, optMenu, mapLay]
        pm.textField(field, e=True, cc=partial(self.fieldChangedZeroMaps, optLay, field))

    def resetOptionMenu(self, parLay, field):
        cmds.deleteUI(self.mapsDict[field][2])
        self.mapsDict[field][2] = pm.optionMenu(p=parLay)

    def populateMapFinder(self, parLay, field, *args):
        self.resetOptionMenu(parLay, field)
        cmds.radioButtonGrp(self.widgets["UVsets"], e=True, select=2)
        obj = cmds.textField(field, q=True, tx=True)
        if not obj or not pm.objExists(obj):
            self.printFeedback('Select a valid object and try again')
            return
        maps = pm.polyUVSet(obj, q=True, auv=True)
        for ma in maps:
            pm.menuItem(label=ma)

    def fieldChangedZeroMaps(self, parLay, field, *args):
        optLay, chBox, optMenu, mapLay = self.mapsDict[field]
        pm.checkBox(chBox, e=True, v=0)
        self.mapFinderSwitcher(chBox, mapLay)
        self.resetOptionMenu(parLay, field)

    def MainToMany(self, w, parLay=''):
        if not parLay:
            print('no parent found for MassAttrTransfer.MainToMany')
            return
        cmds.separator(w=w, h=7, p=parLay, style='none')
        pm.text('Select Main object', p=parLay)
        cmds.separator(h=7, p=parLay)
        self.widgets['mainObj'] = uim.selectAndAddToField(self, parLay, 'Select', 'transform')
        self.addMapFinder(parLay, self.widgets['mainObj'])

        selectLay = cmds.rowColumnLayout(nc=2, cs=[2, 5], p=parLay)

        cmds.separator(h=7, p=selectLay)
        cmds.separator(h=7, p=selectLay)

        scrollName = 'Transfer_Objects'
        cmds.separator(h=7, vis=False, p=selectLay)

        self.addScrollSetup(scrollName, selectLay, w, False)

        cmds.separator(h=7, p=parLay)
        cmds.button('Execute', p=parLay, c=self.execMainToMany)

    def execMainToMany(self, *args):
        self.defaultFeedback()
        mainObj = cmds.textField(self.widgets['mainObj'], q=True, tx=True)
        destList = cmds.textScrollList(self.widgets["Transfer_ObjectsScroll"], q=True, allItems=True)
        optLay, chBox, optMenu, mapLay = self.mapsDict[self.widgets['mainObj']]
        sMap = False
        if pm.checkBox(chBox, q=True, v=True):
            sMap = True
        if not mainObj:
            self.orangeFeedback('No main object selected')
            return
        if not destList:
            self.orangeFeedback('No destination objects listed')
            return
        for dest in destList:
            dObj = pm.PyNode(dest.partition(' - ')[2])
            if sMap:
                mapSource = pm.optionMenu(optMenu, q=True, sl=True) - 1
                self.transferAttributes(mainObj, dObj, mapSource)
            else:
                self.transferAttributes(mainObj, dObj)

    def transByAssos(self, w, parLay=''):
        if not parLay:
            print('no parent found for MassAttrTransfer.transByAssos')
            return
        '''
        cmds.separator(h=7, p=parLay)
        pm.text('* Create associations for attribute transfer\n'
                'NOTE 1: lists must match (1st to 1st, 2nd to 2nd etc.)\n'
                'NOTE 2: Possible to add multiple abjects to list and \n'
                're-arrange the order if needed *', p=parLay)
        '''
        cmds.separator(w=w, h=7, p=parLay)
        mainLay = cmds.rowColumnLayout(nc=2, cs=[2, 5], p=parLay)
        scrollName = 'source'
        for scrollName in ['source', 'dest']:
            self.addScrollSetup(scrollName, mainLay, w / 2)

        cmds.separator(h=7, p=parLay)
        cmds.button('Execute', p=parLay, c=self.execTransByAssos)

    def execTransByAssos(self, *args):
        self.defaultFeedback()
        sourceList = cmds.textScrollList(self.widgets["sourceScroll"], q=True, allItems=True)
        destList = cmds.textScrollList(self.widgets["destScroll"], q=True, allItems=True)
        if len(sourceList) != len(destList):
            self.orangeFeedback('Nothing to remove')
            return
        for source, dest in zip(sourceList, destList):
            sObj = source[4:]
            dObj = dest[4:]
            self.transferAttributes(sObj, dObj)

    def transByParentGrps(self, w, parLay=''):
        if not parLay:
            print
            'no parent found for MassAttrTransfer.transByParentGrps'
            return
        cmds.separator(w=w + 10, h=7, p=parLay)
        pm.text('Transfer by hierarchy\n'
                'Note: names must match', p=parLay)
        cmds.separator(h=7, p=parLay)

        pm.text('Select Source group', p=parLay)
        self.widgets['sourceGrp'] = uim.selectAndAddToField(self, parLay, 'Select', 'transform')

        pm.text('Select Destination group', p=parLay)
        self.widgets['destGrp'] = uim.selectAndAddToField(self, parLay, 'Select', 'transform')

        cmds.separator(h=7, vis=False, p=parLay)
        pm.button('Execute', c=self.execTransByParentGrps, p=parLay)
        cmds.separator(h=7, vis=False, p=parLay)

    def execTransByParentGrps(self, *args):
        self.defaultFeedback()
        source = cmds.textField(self.widgets['sourceGrp'], q=True, tx=True)
        dest = cmds.textField(self.widgets['destGrp'], q=True, tx=True)
        error = ''
        if not source or not dest:
            error = 'missing selection'
        if not pm.objExists(source):
            error = "source '%s' can't be found in the scene"
        if not pm.objExists(dest):
            error = "destination '%s' can't be found in the scene"
        if error:
            self.redError(error)
            return
        # ready to start transfer
        sourceObjs = pm.listRelatives(source, c=True, type='transform')
        destObjs = pm.listRelatives(dest, c=True, type='transform')
        if not len(sourceObjs) == len(destObjs):
            self.redError('folders children do not match')
            return
        for sObj, dObj in zip(sourceObjs, destObjs):
            match = self.nameMatchCheck(sObj, dObj)
            if not match:
                for temp in destObjs:
                    if self.nameMatchCheck(sObj, temp):
                        dObj = temp
                        match = True
                        break
            if match:
                self.transferAttributes(sObj, dObj)
            else:
                error = ' // %s : source "%s" and destination "%s" names do not match - skipping ' \
                        'transfer.' % (self.feedbackName, sObj, dObj)
                print(error)
        if error:
            self.orangeFeedback('Error occurred in process, check Script Editor for details')
        else:
            self.changeFeedback('done', 'green')

    def nameMatchCheck(self, name1, name2):
        if '|' in name1.name():
            name1 = name1.name().rpartition('|')[2]
        elif ':' in name1.name():
            name1 = name1.name().rpartition(':')[2]
        else:
            name1 = name1.name()
        if '|' in name2.name():
            name2 = name2.name().rpartition('|')[2]
        elif ':' in name2.name():
            name2 = name2.name().rpartition(':')[2]
        else:
            name2 = name2.name()
        # return
        if name1 == name2:
            return True
        else:
            return False

    def transObjToObj(self, w, parLay=''):
        if not parLay:
            print
            'no parent found for MassAttrTransfer.transObjToObj'
            return
        cmds.separator(w=w, h=7, p=parLay)
        pm.text('Transfer a specific UV set\nor\nselect the Orig shape (skinned objs)', p=parLay)
        cmds.separator(h=7, p=parLay)

        pm.text('Source', p=parLay, font='boldLabelFont')
        self.widgets['sourceObj'] = uim.selectAndAddToField(self, parLay, 'Source', 'transform')
        self.addMapFinder(parLay, self.widgets['sourceObj'])
        cmds.separator(h=7, p=parLay)

        pm.text('Destination', p=parLay, font='boldLabelFont')
        self.widgets['destObj'] = uim.selectAndAddToField(self, parLay, 'Destination', 'transform')
        self.addMapFinder(parLay, self.widgets['destObj'])
        cmds.separator(h=7, p=parLay)

        pm.text('Select Orig Shape node', p=parLay, font='boldLabelFont')

        pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=parLay)
        pm.button(l='Find Orig', c=self.updateOrigField)
        self.widgets['origObj'] = cmds.textField()

        pm.separator(h=7, p=parLay)

        cmds.separator(h=7, vis=False, p=parLay)
        pm.button('Execute', w=w + 10, c=self.execTransObjToObj, p=parLay)
        cmds.separator(h=7, vis=False, p=parLay)

    def execTransObjToObj(self, *args):
        self.defaultFeedback()
        sourceObj = cmds.textField(self.widgets['sourceObj'], q=True, tx=True)
        destObj = cmds.textField(self.widgets['destObj'], q=True, tx=True)

        objectChecks = [[sourceObj, 'Source'],
                        [destObj, 'Destination']]
        hasSkin = False
        if gmt.hasSkin(destObj) or gmt.hasBlendShape(destObj):  # todo check for deformers in general
            hasSkin = True
            origObj = cmds.textField(self.widgets['origObj'], q=True, tx=True)
            objectChecks.append([origObj, 'Orig Shape'])

        for item, name in objectChecks:
            if item and pm.objExists(item):
                self.greenFeedback('item %s valid' % item)
                continue
            else:
                self.printFeedback('No %s selected or object not found.' % name)
                return
        source = pm.PyNode(sourceObj)
        dest = pm.PyNode(destObj)
        if hasSkin:
            # print('source="%s"\ndest="%s"\norig="%s"' % (source, dest, origObj))
            dest = pm.PyNode(origObj)
            dest.intermediateObject.set(0)
            print 'set intermediate 0'

        # transferring uv
        optLayS, chBoxS, optMenuS, mapLay = self.mapsDict[self.widgets['sourceObj']]
        if pm.checkBox(chBoxS, q=True, v=True):
            mapNum = int(pm.optionMenu(optMenuS, q=True, sl=True))
            maps = gmt.getAllUVmaps(source)
            if mapNum > len(maps) or not gmt.isValidMap(maps[mapNum - 1], source):
                self.printFeedback('Refresh Source map selection and try again')
                return
            mapSource = maps[mapNum - 1]
        else:
            mapSource = str(pm.polyUVSet(source, q=True, cuv=True))

        optLayD, chBoxD, optMenuD, mapLay = self.mapsDict[self.widgets['destObj']]
        if pm.checkBox(chBoxD, q=True, v=True):
            mapNum = int(pm.optionMenu(optMenuD, q=True, sl=True))
            maps = gmt.getAllUVmaps(source)
            if mapNum > len(maps) or not gmt.isValidMap(maps[mapNum - 1], dest):
                self.printFeedback('Refresh Destination map selection and try again')
                return
            mapDest = gmt.getAllUVmaps(dest)[mapNum - 1]
        else:
            mapDest = str(pm.polyUVSet(dest, q=True, cuv=True))

        print('Source UV map: %s' % mapSource)
        print('Destination UV map: %s' % mapDest)

        if hasSkin:
            print ('transferAttributes(source="%s",\n'
                   '                   dest="%s",\n'
                   '                   mapSource="%s",\n'
                   '                   mapDest="%s"' % (source, dest, mapSource, mapDest))
            self.transferAttributes(source, dest, mapSource, mapDest, origObj=True)
            print 'with orig'
        else:
            self.transferAttributes(source, dest, mapSource, mapDest)
            print 'without orig'
        # pm.transferAttributes(source, orig, pos=0, nml=0, uvs=2, col=2, spa=4, sus=mapSource, sm=3, fuv=0, clb=1)
        # deleting history and connect back Orig
        # pm.delete(dest, ch=True)
        if hasSkin:
            pm.select(dest)
            mel.eval('DeleteHistory;')
            pm.select(d=True)
            dest.intermediateObject.set(1)
        pm.select(destObj)

    def getOrigShapes(self, obj):
        shps = pm.listRelatives(obj, s=True)
        origs = []
        for shp in shps:
            if 'Orig' in shp.name():
                origs.append(shp)
        return origs

    def updateOrigField(self, *args):
        self.defaultFeedback()
        destObj = cmds.textField(self.widgets['destObj'], q=True, tx=True)
        if not destObj:
            self.printFeedback('No destination selected.')
            return
        if not pm.objExists(destObj):
            self.printFeedback('No Destination selected or object not found.')
            return
        destObj = pm.PyNode(destObj)
        origs = self.getOrigShapes(destObj)
        if not origs:
            self.printFeedback("Couldn't find Orig shape under '%s'" % destObj)
            return
        if len(origs) > 1:
            print('multiple origs: %s ' % origs)
            self.origSelector(origs)
            return
        else:
            orig = origs[0]
        cmds.textField(self.widgets['origObj'], e=True, tx=orig.name())

    def origSelector(self, origs):
        if cmds.window('origSelector', exists=True):
            cmds.deleteUI('origSelector')
        cmds.window('origSelector', title='Orig Selector', sizeable=1, rtf=True)
        cmds.columnLayout(adj=True)
        pm.separator(w=200, style='none')
        scroll = cmds.textScrollList(allowMultiSelection=True, h=70)
        for orig in origs:
            cmds.textScrollList(scroll, edit=True, append=orig.name())
        pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=1)
        # cmds.rowColumnLayout(nc=2, cs=[[2, 5]])
        cmds.button('Select', c=partial(self.selectMultOrig, scroll))
        cmds.button('  Close  ', c=self.cancelMultOrig)
        cmds.showWindow()

    def selectMultOrig(self, scroll, *args):
        orig = cmds.textScrollList(scroll, query=True, selectItem=True)
        cmds.textField(self.widgets['origObj'], e=True, tx=orig[0])
        if cmds.window('origSelector', exists=True):
            cmds.deleteUI('origSelector')

    def cancelMultOrig(self, *args):
        if cmds.window('origSelector', exists=True):
            cmds.deleteUI('origSelector')

    def transferAttributes(self, source, destination, sourceMap='', mapDest='', origObj=False):
        # todo compare/delete the uv sets before transferring (it keeps the old and adds the new ones)
        print('//  //   transferAttributes:   //  //\n'
              'source = %s\n'
              'destination = %s' % (source, destination))
        vtxPos = cmds.radioButtonGrp(self.widgets["vtxPos"], q=True, select=True) - 1
        normalPos = cmds.radioButtonGrp(self.widgets["normalPos"], q=True, select=True) - 1
        uvSets = cmds.radioButtonGrp(self.widgets["UVsets"], q=True, select=True) - 1
        colorSets = cmds.radioButtonGrp(self.widgets["colorSets"], q=True, select=True) - 1
        sampleSpace = int(cmds.radioCollection(self.widgets["sampleSpace"], q=True, select=True).replace('rad', ''))
        mirroring = cmds.radioButtonGrp(self.widgets["mirroring"], q=True, select=True)
        flipUVs = cmds.radioButtonGrp(self.widgets["flipUVs"], q=True, select=True) - 1
        colorBorders = cmds.radioButtonGrp(self.widgets["colorBorders"], q=True, select=True) - 1
        searchMethod = cmds.radioButtonGrp(self.widgets["searchMethod"], q=True, select=True)

        mirrorChBox = cmds.checkBox(self.widgets["mirrorChBox"], q=True, v=True)
        boundChBox = cmds.checkBox(self.widgets["boundChBox"], q=True, v=True)

        # this is for current map
        if sourceMap is not '':
            pm.polyUVSet(source, e=True, cuv=True, uvs=sourceMap)
        else:
            sourceSets = gmt.getAllUVmaps(source)
            if sourceSets:
                sourceMap = str(sourceSets[0])
        if mapDest is not '':
            pm.polyUVSet(destination, e=True, cuv=True, uvs=mapDest)
            destMap = mapDest
        else:
            destSets = pm.polyUVSet(destination, q=True, cuv=True)
            destMap = ''
            if destSets:
                destMap = str(destSets[0])
                # destMap += destSets[0]
            else:
                print(' // no sets found on target: "%s"\n'
                      '// using map1 instead' % destination)
                destMap = 'map1'

        # print('sourceMap = %s' % sourceMap)
        # print('destMap = %s' % destMap)
        hasSkin = False
        checkOrig = False
        if not origObj:
            if gmt.hasSkin(destination):
                hasSkin = True
                checkOrig = True
        if hasSkin:
            if boundChBox:
                if checkOrig:
                    origs = self.getOrigShapes(destination)
                    if origs:
                        orig = origs[len(origs) - 1]
                        print('using orig shape "%s" for "%s"' % (orig, destination))
                        orig.intermediateObject.set(0)
                        destination = orig
                        print 'updated destination = %s' % destination
            else:
                self.printFeedback('Object "%s" has skin - SKIPPED - '
                                   'to transfer, check the skin to bound checkbox' % destination)
                return

        if searchMethod == 1:
            searchMethod = 0
        else:
            searchMethod = 3
        '''
        print ('pm.transferAttributes("%s", "%s", '
               'pos=%s, nml=%s, uvs=%s, col=%s, spa=%s, '
               'suv="%s", tuv="%s", '
               'sm=%s, fuv=%s, clb=%s)' % (source, destination,
                                           vtxPos, normalPos, uvSets, colorSets, sampleSpace, sourceMap,
                                           destMap, searchMethod, flipUVs, colorBorders))
        '''
        if uvSets == 1:  # Current
            # add arguments: "sourceUvSet=sourceMap, targetUvSet=destMap"
            if mirroring == 2:
                # print('checkpoint 1')
                pm.transferAttributes(source, destination,
                                      pos=vtxPos, nml=normalPos, uvs=uvSets, col=colorSets, spa=sampleSpace,
                                      suv=sourceMap, tuv=destMap,
                                      sus=sourceMap, tus=destMap, searchScaleX=-1.0,
                                      sm=searchMethod, fuv=flipUVs, clb=colorBorders)
            elif mirroring == 3:
                # print('checkpoint 2')

                pm.transferAttributes(source, destination,
                                      pos=vtxPos, nml=normalPos, uvs=uvSets, col=colorSets, spa=sampleSpace,
                                      suv=sourceMap, tuv=destMap,
                                      sus=sourceMap, tus=destMap, searchScaleY=-1.0,
                                      sm=searchMethod, fuv=flipUVs, clb=colorBorders)
            elif mirroring == 4:
                # print('checkpoint 3')

                pm.transferAttributes(source, destination,
                                      pos=vtxPos, nml=normalPos, uvs=uvSets, col=colorSets, spa=sampleSpace,
                                      suv=sourceMap, tuv=destMap,
                                      sus=sourceMap, tus=destMap, searchScaleZ=-1.0,
                                      sm=searchMethod, fuv=flipUVs, clb=colorBorders)
            else:
                # print('checkpoint 4')
                '''
                print ('pm.transferAttributes(%s, %s, '
                       'pos=%s, nml=%s, uvs=%s, col=%s, spa=%s,'
                       'suv=%s, tuv=%s,'
                       'sm=%s, fuv=%s, clb=%s)' % (source, destination,
                                                   vtxPos, normalPos, uvSets, colorSets, sampleSpace, sourceMap,
                                                   destMap, searchMethod, flipUVs, colorBorders))
                '''
                pm.transferAttributes(source, destination,
                                      pos=vtxPos, nml=normalPos, uvs=uvSets, col=colorSets, spa=sampleSpace,
                                      suv=sourceMap, tuv=destMap,
                                      sm=searchMethod, fuv=flipUVs, clb=colorBorders)
        else:
            if mirroring == 2:
                # print('checkpoint 5')
                pm.transferAttributes(source, destination,
                                      pos=vtxPos, nml=normalPos, uvs=uvSets, col=colorSets, spa=sampleSpace,
                                      suv=sourceMap, tuv=destMap, searchScaleX=-1.0,
                                      sm=searchMethod, fuv=flipUVs, clb=colorBorders)
            elif mirroring == 3:
                # print('checkpoint 6')
                pm.transferAttributes(source, destination,
                                      pos=vtxPos, nml=normalPos, uvs=uvSets, col=colorSets, spa=sampleSpace,
                                      suv=sourceMap, tuv=destMap, searchScaleY=-1.0,
                                      sm=searchMethod, fuv=flipUVs, clb=colorBorders)
            elif mirroring == 4:
                # print('checkpoint 7')
                pm.transferAttributes(source, destination,
                                      pos=vtxPos, nml=normalPos, uvs=uvSets, col=colorSets, spa=sampleSpace,
                                      suv=sourceMap, tuv=destMap, searchScaleZ=-1.0,
                                      sm=searchMethod, fuv=flipUVs, clb=colorBorders)
            else:
                # print('checkpoint 8')
                print ('pm.transferAttributes("%s", "%s", '
                       'pos=%s, nml=%s, uvs=%s, col=%s, spa=%s,'
                       'suv=%s, tuv=%s,'
                       'sm=%s, fuv=%s, clb=%s)' % (source, destination,
                                                   vtxPos, normalPos, uvSets, colorSets, sampleSpace, sourceMap,
                                                   destMap, searchMethod, flipUVs, colorBorders))
                pm.transferAttributes(source, destination,
                                      pos=vtxPos, nml=normalPos, uvs=uvSets, col=colorSets, spa=sampleSpace,
                                      suv=sourceMap, tuv=destMap,
                                      sm=searchMethod, fuv=flipUVs, clb=colorBorders)
        if mirrorChBox:  # todo test in more situations
            print ' // Trying to mirror %s' % destination
            gmt.mirrorUV(destination)

        if checkOrig:
            # pm.delete(orig, ch=True)
            pm.select(orig)
            mel.eval('DeleteHistory;')
            pm.select(d=True)
            orig.intermediateObject.set(1)
        # pm.transferAttributes(source, destination,
        #                      pos=0, nml=0, uvs=2, col=2, spa=5,
        #                      sus=sourceMap, tuv=destMap,
        #                      sm=3, fuv=0, clb=1)

    def addScrollSetup(self, scrollName, parLay, w=170, upDown=True):
        mainLay = cmds.rowColumnLayout(nc=1, p=parLay)

        pm.text(scrollName + ' List', p=mainLay)

        cmds.rowColumnLayout(nc=2, cs=[2, 4], p=mainLay)
        cmds.button('add from\nselection', w=w / 2 - 2, c=partial(self.updateScrolls, scrollName))
        cmds.button('remove\nfrom list', w=w / 2 - 2, c=partial(self.updateScrolls, scrollName, True))
        self.widgets[scrollName + "Scroll"] = cmds.textScrollList(allowMultiSelection=True, h=100, w=w, p=mainLay)
        if upDown:
            cmds.rowColumnLayout(nc=3, cs=[[2, 5], [3, 5]], p=mainLay)
            pm.text('Move : ')
            cmds.button(l='Down', w=50, c=partial(self.moveScrollItem, scrollName))
            cmds.button(l='Up', w=50, c=partial(self.moveScrollItem, scrollName, True))

    def updateScrolls(self, scrollName, remove=False, *args):
        scroll = self.widgets[scrollName + "Scroll"]
        if remove:
            selItem = cmds.textScrollList(scroll, query=True, selectItem=True)
            if not selItem:
                self.orangeFeedback('Nothing to remove')
                return
            for item in selItem:
                cmds.textScrollList(scroll, e=True, removeItem=item)
        else:
            sele = pm.selected()
            i = 1
            for sel in sele:
                cmds.textScrollList(scroll, edit=True, append='%s - %s' % (i, sel.name()))
                i += 1
            # resize scroll
            allItems = cmds.textScrollList(scroll, q=True, allItems=True)
            if len(allItems) > 16:
                cmds.textScrollList(scroll, e=True, h=300)
            elif len(allItems) > 13:
                cmds.textScrollList(scroll, e=True, h=250)
            elif len(allItems) > 6:
                cmds.textScrollList(scroll, e=True, h=200)
        self.renumberScroll(scroll)

    def renumberScroll(self, scroll):
        allItems = cmds.textScrollList(scroll, q=True, allItems=True)
        tempList = []
        i = 1
        if not allItems:
            cmds.textScrollList(scroll, e=True, removeAll=True)
            return
        for item in allItems:
            tempList.append('%s - %s' % (i, item.partition(' - ')[2]))
            i += 1
        cmds.textScrollList(scroll, e=True, removeAll=True)
        for item in tempList:
            cmds.textScrollList(scroll, edit=True, append=item)

    def moveScrollItem(self, scrollName, up=False, *args):
        scroll = self.widgets[scrollName + "Scroll"]
        selItem = cmds.textScrollList(scroll, query=True, selectItem=True)
        selIdx = cmds.textScrollList(scroll, query=True, selectIndexedItem=True)
        if not selIdx or not selItem:
            self.orangeFeedback('Nothing selected')
            return
        selIdx = selIdx[0]
        appendPos = selIdx + 1
        if up:
            appendPos = selIdx - 1
        cmds.textScrollList(scroll, edit=True, removeIndexedItem=selIdx)
        cmds.textScrollList(scroll, edit=True, appendPosition=[appendPos, selItem[0]])
        self.renumberScroll(scroll)
        cmds.textScrollList(scroll, edit=True, selectIndexedItem=appendPos)

    def frameAndLayout(self, title, parLay, collapse=False):
        cmds.frameLayout(label=title, collapsable=True, cl=collapse, p=parLay)
        newLay = cmds.rowColumnLayout(nc=1)
        return newLay

    def addLayAndText(self, parLay, label):
        pm.rowLayout(nc=2, adjustableColumn=2, p=parLay)
        cmds.text(label + '  ', w=100, al='right')

    def affectSecondaryRadio(self, mainRadio, secRadio, *args):
        val = cmds.radioButtonGrp(self.widgets[mainRadio], q=True, select=True) - 1
        if val:
            cmds.radioButtonGrp(self.widgets[secRadio], e=True, enable=True)
        else:
            cmds.radioButtonGrp(self.widgets[secRadio], e=True, enable=False)
        print val
        if val != 1 and mainRadio == 'UVsets':
            self.clearUvMapCheckboxes()

    def clearUvMapCheckboxes(self):
        for field in self.mapsDict:
            optLay, chBox, optMenu, mapLay = self.mapsDict[field]
            pm.checkBox(chBox, e=True, v=0)
            self.fieldChangedZeroMaps(optLay, field)

    def populateUVoptions(self, mainLay):
        rw = 67
        radioH = 16
        lay = cmds.frameLayout(label="Attributes to transfer", collapsable=True, cl=False, p=mainLay)
        self.addLayAndText(lay, 'Vertex Position:')
        self.widgets["vtxPos"] = cmds.radioButtonGrp(nrb=2, cw2=[rw * 2, rw], select=1, h=radioH,
                                                     labelArray2=['Off', 'On'])
        self.addLayAndText(lay, 'Normal Position:')
        self.widgets["normalPos"] = cmds.radioButtonGrp(nrb=2, cw2=[rw * 2, rw], select=1, h=radioH,
                                                        labelArray2=['Off', 'On'])
        self.addLayAndText(lay, 'UV Sets:')
        self.widgets["UVsets"] = cmds.radioButtonGrp(nrb=3, cw3=[rw, rw, rw], select=3, h=radioH,
                                                     labelArray3=['Off', 'Current', 'On'],
                                                     cc=partial(self.affectSecondaryRadio,
                                                                'UVsets', 'flipUVs'))
        self.addLayAndText(lay, 'Color Sets:')
        self.widgets["colorSets"] = cmds.radioButtonGrp(nrb=3, cw3=[rw, rw, rw], select=3, h=radioH,
                                                        labelArray3=['Off', 'Current', 'On'],
                                                        cc=partial(self.affectSecondaryRadio,
                                                                   'colorSets', 'colorBorders'))
        pm.separator(h=7, p=mainLay, style='none')
        lay = cmds.frameLayout(label="Attributes Settings", collapsable=True, cl=False, p=mainLay)

        self.addLayAndText(lay, 'Sample Space:')

        cmds.rowColumnLayout(nc=4, columnWidth=[[1, rw], [2, rw], [3, rw], [4, rw + 13]])
        self.widgets["sampleSpace"] = cmds.radioCollection()
        self.widgets["sampleB1"] = cmds.radioButton('rad0', label='World')
        self.widgets["sampleB2"] = cmds.radioButton('rad1', label='Local')
        self.widgets["sampleB3"] = cmds.radioButton('rad3', label='UV')
        self.widgets["sampleB4"] = cmds.radioButton('rad4', label='Component')
        self.widgets["sampleB5"] = cmds.radioButton('rad5', label='Topology')
        cmds.radioCollection(self.widgets["sampleSpace"], edit=True, select=self.widgets["sampleB5"])

        self.addLayAndText(lay, 'Mirroring:')
        self.widgets["mirroring"] = cmds.radioButtonGrp(nrb=4, select=1, cw4=[rw, rw, rw, rw], h=radioH,
                                                        labelArray4=['Off', 'X', 'Y', 'Z'])
        self.addLayAndText(lay, 'Flip UVs:')
        self.widgets["flipUVs"] = cmds.radioButtonGrp(nrb=3, cw3=[rw, rw, rw], select=1, h=radioH,
                                                      labelArray3=['Off', 'U', 'V'])
        self.addLayAndText(lay, 'Color Borders:')
        self.widgets["colorBorders"] = cmds.radioButtonGrp(nrb=2, cw2=[rw * 2, rw], select=2, h=radioH,
                                                           labelArray2=['Ignore', 'Preserve'])
        self.addLayAndText(lay, 'Search Method:')
        self.widgets["searchMethod"] = cmds.radioButtonGrp(nrb=2, cw2=[rw * 2, rw], select=2, h=radioH,
                                                           labelArray2=['Closest along normal', 'Closest to point'])
        pm.separator(h=7, p=mainLay, style='none')
        lay = cmds.frameLayout(label="       Extras", collapsable=False, cl=False, p=mainLay)
        pm.separator(h=1, style='none', p=lay)
        pm.rowLayout(nc=2, adjustableColumn=2, p=lay)
        pm.separator(w=100, style='none')
        pm.columnLayout()
        self.widgets["mirrorChBox"] = cmds.checkBox(l='Mirror UV', v=0)
        self.widgets["boundChBox"] = cmds.checkBox(l='Transfer to bound objects', v=0)
        pm.separator(h=7, p=mainLay)

    def populateUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)
        pm.text(l='UV Transfer Toolbox', font='boldLabelFont', p=mainLay)
        pm.separator(h=7, p=mainLay)

        self.populateUVoptions(mainLay)

        self.widgets["tabLayout"] = cmds.tabLayout(childResizable=True, p=mainLay)
        # uiLay = mainLay
        uiLay = self.widgets["tabLayout"]
        mainWidth = 385
        '''
        collapse = True
        self.MainToMany(mainWidth, self.frameAndLayout('Main to Many', uiLay))
        #pm.separator(h=5, style='none', p=uiLay)
        self.transByAssos(mainWidth, self.frameAndLayout('by Association', uiLay, collapse))
        #pm.separator(h=5, style='none', p=uiLay)
        self.transByParentGrps(mainWidth, self.frameAndLayout('by Parent Grps', uiLay, collapse))
        #pm.separator(h=5, style='none', p=uiLay)
        self.transObjToObj(mainWidth, self.frameAndLayout('transfer to bound', uiLay, collapse))
        '''
        self.MainToMany(mainWidth, cmds.rowColumnLayout('Main to Many', nc=1, p=uiLay))
        self.transByAssos(mainWidth, cmds.rowColumnLayout('by Association', nc=1, p=uiLay))
        self.transByParentGrps(mainWidth, cmds.rowColumnLayout('by Parent Grps', nc=1, p=uiLay))
        self.transObjToObj(mainWidth, cmds.rowColumnLayout('Obj to Obj', nc=1, p=uiLay))

        '''
        # add Execute/scriptIt buttons
        cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
        cmds.button(l='Execute', h=28, c=self.execute)
        if scriptIt:
            cmds.button(l='Script it', w=100, c=self.scriptIt)
        else:
            pm.separator(w=100, style='none')
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

    '''
    def execute(self, *args):
        return

    def scriptIt(self, *args):
        return
    '''
