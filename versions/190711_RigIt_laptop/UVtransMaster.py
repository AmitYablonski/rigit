from maya import cmds, mel
import pymel.core as pm
from functools import partial
import UI_modules as uim
import RigItMethodsUI as rim


class UVtransMaster:
    def __init__(self, par='', scriptIt=False):
        self.widgets = {}
        self.feedbackName = 'UV Transfer Master'
        topLay, mainLay = self.winBase('UVtransMaster', self.feedbackName, par)
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def MainToMany(self, w, parLay=''):
        if not parLay:
            print('no parent found for MassAttrTransfer.MainToMany')
            return
        cmds.separator(w=w, h=7, p=parLay)
        pm.text('Select Main object', p=parLay)
        self.widgets['mainObj'] = uim.selectAndAddToField(self, parLay, 'Select', 'transform')

        selectLay = cmds.rowColumnLayout(nc=2, cs=[2, 5], p=parLay)

        cmds.separator(h=7, p=selectLay)
        cmds.separator(h=7, p=selectLay)

        scrollName = 'Transfer Objects'
        cmds.separator(h=7, vis=False, p=selectLay)

        self.addScrollSetup(scrollName, selectLay, w, False)

        cmds.separator(h=7, p=parLay)
        cmds.button('Execute', p=parLay, c=self.execMainToMany)

    def execMainToMany(self, *args):
        self.defaultFeedback()
        mainObj = cmds.textField(self.widgets['mainObj'], q=True, tx=True)
        destList = cmds.textScrollList(self.widgets["Transfer_ObjectsScroll"], q=True, allItems=True)
        if not mainObj:
            self.orangeError('No main object selected')
            return
        if not destList:
            self.orangeError('No destination objects listed')
            return
        for dest in destList:
            dObj = pm.PyNode(dest[4:])
            print(dObj)
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
            self.orangeError('Nothing to remove')
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
        cmds.separator(w=w+10, h=7, p=parLay)
        pm.text('* Transfer attributes for children of selected folders\n'
                'Note: object names inside groups must match *', p=parLay)
        cmds.separator(h=7, p=parLay)

        pm.text('Select Source group', p=parLay)
        self.widgets['sourceGrp'] = uim.selectAndAddToField(self, parLay, 'Select', 'transform')

        pm.text('Select Destination group', p=parLay)
        self.widgets['destGrp'] = uim.selectAndAddToField(self, parLay, 'Select', 'transform')

        cmds.separator(h=7, vis=False, p=parLay)
        pm.button('Transfer', c=self.execTransByParentGrps, p=parLay)
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
            self.orangeError('Error occurred in process, check Script Editor for details')
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

    def transToBound(self, w, parLay=''):
        if not parLay:
            print
            'no parent found for MassAttrTransfer.transToBound'
            return
        cmds.separator(w=w, h=7, p=parLay)
        pm.text('* Transfer UV to a bound object *', p=parLay)
        cmds.separator(h=7, p=parLay)

        self.widgets['sourceObj'] = uim.selectAndAddToField(self, parLay, 'Source', 'transform')
        self.widgets['destObj'] = uim.selectAndAddToField(self, parLay, 'Destination', 'transform')

        pm.text('Verify Orig Shape node', p=parLay)

        pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=parLay)
        pm.button(l='Find Orig', c=self.updateOrigField)
        self.widgets['origObj'] = cmds.textField()

        cmds.separator(h=7, vis=False, p=parLay)
        pm.button('Transfer', w=w + 10, c=self.execTransToBound, p=parLay)
        cmds.separator(h=7, vis=False, p=parLay)

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
        shps = pm.listRelatives(destObj, s=True)
        origs = []
        for shp in shps:
            if 'Orig' in shp.name():
                origs.append(shp)
        if not origs:
            self.printFeedback("Couldn't find Orig shape under '%s'" % destObj)
            return
        if len(origs) > 1:
            print 'multiple origs: %s ' % origs
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
        #cmds.rowColumnLayout(nc=2, cs=[[2, 5]])
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

    def execTransToBound(self, *args):
        self.defaultFeedback()
        sourceObj = cmds.textField(self.widgets['sourceObj'], q=True, tx=True)
        destObj = cmds.textField(self.widgets['destObj'], q=True, tx=True)
        origObj = cmds.textField(self.widgets['origObj'], q=True, tx=True)

        for item, name in [[sourceObj, 'Destination'],
                           [destObj, 'Source'],
                           [origObj, 'Orig']]:
            if item and pm.objExists(item):
                self.greenFeedback('item %s valid' % item)
                continue
            else:
                self.printFeedback('No %s selected or object not found.' % name)
                return
        source = pm.PyNode(sourceObj)
        dest = pm.PyNode(destObj)
        orig = pm.PyNode(origObj)

        print('source="%s"\ndest="%s"\norig="%s"' % (source, dest, orig))

        orig.intermediateObject.set(0)

        # transferring uv
        mapSource = str(pm.polyUVSet(source, q=True, cuv=True))
        print('Source UV map: ' + str(mapSource))
        pm.transferAttributes(source, orig, pos=0, nml=0, uvs=2, col=2, spa=4, sus=mapSource, sm=3, fuv=0, clb=1)

        # deleting history
        pm.delete(orig, ch=True)

        # connect orig back
        orig.intermediateObject.set(1)
        pm.select(dest)

    def transferAttributes(self, source, destination):
        # todo check what are all the variables - create a ui to control some of it
        mapSource = str(pm.polyUVSet(source, q=True, cuv=True))
        mapDestination = str(pm.polyUVSet(destination, q=True, cuv=True))
        pm.transferAttributes(source, destination,
                              pos=0, nml=0, uvs=2, col=2, spa=5,
                              sus=mapSource, tus=mapDestination,
                              sm=3, fuv=0, clb=1)

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
                self.orangeError('Nothing to remove')
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
            self.orangeError('Nothing selected')
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

    def populateUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)
        pm.text(l='UV Transfer Toolbox', font='boldLabelFont', p=mainLay)
        pm.separator(h=7, p=mainLay)

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
        self.transToBound(mainWidth, self.frameAndLayout('transfer to bound', uiLay, collapse))
        '''
        self.MainToMany(mainWidth, cmds.rowColumnLayout('Main to Many', nc=1, p=uiLay))
        self.transByAssos(mainWidth, cmds.rowColumnLayout('by Association', nc=1, p=uiLay))
        self.transByParentGrps(mainWidth, cmds.rowColumnLayout('by Parent Grps', nc=1, p=uiLay))
        self.transToBound(mainWidth, cmds.rowColumnLayout('transfer to bound', nc=1, p=uiLay))

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
