from maya import cmds, mel
import pymel.core as pm
from functools import partial
import generalMayaTools as gmt


class MassAttrTransfer:

    def __init__(self):

        self.feedbackName = 'Mass Attr Transfer'

        self.widgets = {}
        self.massAttrWin()

    def massAttrWin(self):
        if cmds.window("mass_attrWindow", exists=True):
            cmds.deleteUI("mass_attrWindow")
        self.widgets["mass_attrWindow"] = cmds.window("mass_attrWindow", title="Mass Attr Transfer", sizeable=1,
                                                      rtf=True)
        mainLay = cmds.rowColumnLayout(nc=1)
        pm.separator(h=5)
        pm.text('Mass Attributes Destruction ( transfer )')
        pm.separator(h=5)
        self.widgets["tabLayout"] = cmds.tabLayout(childResizable=True)
        # by parent groups tab

        self.fromMainToMany(cmds.rowColumnLayout('from Main object to many', nc=1, p=self.widgets["tabLayout"]))
        self.transferByAssos(cmds.rowColumnLayout('by Association', nc=1, p=self.widgets["tabLayout"]))
        self.transferByParent(cmds.rowColumnLayout('by Parent Grps', nc=1, p=self.widgets["tabLayout"]))

        cmds.separator(h=7, p=mainLay)
        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False, p=mainLay)
        cmds.separator(h=7, p=mainLay)

        self.defaultFeedback()
        cmds.showWindow()

    def addScrollSetup(self, scrollName, parentLay, w=170, upDown=True):
        mainLay = cmds.rowColumnLayout(nc=1, p=parentLay)
        pm.text('Select ' + scrollName, p=mainLay)
        cmds.rowColumnLayout(nc=2, cs=[2, 4], p=mainLay)
        cmds.button('add from\nselection', w=w / 2 - 2, c=partial(self.updateScrolls, scrollName))
        cmds.button('remove\nfrom list', w=w / 2 - 2, c=partial(self.updateScrolls, scrollName, True))
        self.widgets[scrollName + "Scroll"] = cmds.textScrollList(allowMultiSelection=True, h=100, w=w, p=mainLay)
        if upDown:
            cmds.rowColumnLayout(nc=3, cs=[[2, 5], [3, 5]], p=mainLay)
            pm.text('Move : ')
            cmds.button(l='Down', w=50, c=partial(self.moveScrollItem, scrollName))
            cmds.button(l='Up', w=50, c=partial(self.moveScrollItem, scrollName, True))

    def fromMainToMany(self, parentLay=''):
        if not parentLay:
            print 'no parent found for MassAttrTransfer.fromMainToMany'
            return
        cmds.separator(h=7, p=parentLay)
        pm.text('Select Main object', p=parentLay)
        selectLay = cmds.rowColumnLayout(nc=2, cs=[2, 5], p=parentLay)
        cmds.button(l='Select', c=partial(self.updateFromSelection, 'mainObj'))
        self.widgets['mainObj'] = cmds.textField(w=300)

        cmds.separator(h=7, p=selectLay)
        cmds.separator(h=7, p=selectLay)

        scrollName = 'Transfer_Objects'
        cmds.separator(h=7, vis=False, p=selectLay)

        self.addScrollSetup(scrollName, selectLay, 260, False)

        cmds.separator(h=7, p=parentLay)
        cmds.button('Execute', p=parentLay, c=self.execFromMainToMany)

    def execFromMainToMany(self, *args):
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
            print dObj
            self.transferAttributes(mainObj, dObj)

    def transferByAssos(self, parentLay=''):
        if not parentLay:
            print 'no parent found for MassAttrTransfer.transferByAssos'
            return
        '''
        cmds.separator(h=7, p=parentLay)
        pm.text('* Create associations for attribute transfer\n'
                'NOTE 1: lists must match (1st to 1st, 2nd to 2nd etc.)\n'
                'NOTE 2: Possible to add multiple abjects to list and \n'
                're-arrange the order if needed *', p=parentLay)
        '''
        cmds.separator(h=7, p=parentLay)
        mainLay = cmds.rowColumnLayout(nc=2, cs=[2, 5], p=parentLay)
        scrollName = 'source'
        for scrollName in ['source', 'dest']:
            self.addScrollSetup(scrollName, mainLay, 168)

        cmds.separator(h=7, p=parentLay)
        cmds.button('Execute', p=parentLay, c=self.execTransferByAssos)

    def execTransferByAssos(self, *args):
        sourceList = cmds.textScrollList(self.widgets["sourceScroll"], q=True, allItems=True)
        destList = cmds.textScrollList(self.widgets["destScroll"], q=True, allItems=True)
        if len(sourceList) != len(destList):
            self.orangeError('Nothing to remove')
            return
        for source, dest in zip(sourceList, destList):
            sObj = source[4:]
            dObj = dest[4:]
            self.transferAttributes(sObj, dObj)

    def updateScrolls(self, scrollName, remove=False, *args):
        scroll = self.widgets[scrollName + "Scroll"]
        if remove:
            # todo removeItem
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
                print sel
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

    def transferByParent(self, parentLay=''):
        if not parentLay:
            print 'no parent found for MassAttrTransfer.transferByParent'
            return
        cmds.separator(h=7, p=parentLay)
        pm.text('* Transfer attributes for children of selected folders\n'
                'Note: object names inside groups must match *', p=parentLay)
        cmds.separator(h=7, p=parentLay)
        pm.text('Select Source group', p=parentLay)
        selectLay1 = cmds.rowColumnLayout(nc=2, cs=[2, 5], p=parentLay)
        cmds.button(l='Select', c=partial(self.updateFromSelection, 'sourceGrp'))
        self.widgets['sourceGrp'] = cmds.textField(w=300)

        pm.text('Select Destination group', p=parentLay)
        selectLay2 = cmds.rowColumnLayout(nc=2, cs=[2, 5], p=parentLay)
        cmds.button(l='Select', c=partial(self.updateFromSelection, 'destGrp'))
        self.widgets['destGrp'] = cmds.textField(w=300)

        cmds.separator(h=7, vis=False, p=parentLay)
        pm.button('Transfer', c=self.doTransferAttr, p=parentLay)
        cmds.separator(h=7, vis=False, p=parentLay)

    def doTransferAttr(self, *args):
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
                # todo check what are all the variables, mainly if the map1 can be a problem or not
                self.transferAttributes(sObj, dObj)
            else:
                error = ' // %s : source "%s" and destination "%s" names do not match - skipping ' \
                        'transfer.' % (self.feedbackName, sObj, dObj)
                print error
        if error:
            self.orangeError('Error occurred in process, check Script Editor for details')
        else:
            self.changeFeedback('done', 'green')

    def transferAttributes(self, source, destination):
        # todo check what are all the variables, mainly if the map1 can be a problem or not
        pm.transferAttributes(source, destination, pos=0, nml=0, uvs=2, col=2, spa=5, sus='map1', tus='map1',
                              sm=3, fuv=0, clb=1)

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

    def updateTextField(self, txField):
        self.defaultFeedback()
        if not self.selection:
            self.redError('no selection found')
            return
        tx = '%s' % self.selection[0].name()
        for i in range(1, len(self.selection)):
            tx += ', %s' % self.selection[i].name()
        cmds.textField(self.widgets['selection'], e=True, tx=tx)

    def updateFromSelection(self, txField, *args):
        self.defaultFeedback()
        sele = pm.selected()
        if len(sele) < 1:
            self.redError('select a single object and try again')
            return
        cmds.textField(self.widgets[txField], e=True, tx=sele[0].name())

    def orangeError(self, text):
        self.redError(text, True)

    def redError(self, text, orange=False):
        error = ' // %s : %s' % (self.feedbackName, text)
        print error
        color = 'red'
        if orange:
            color = 'orange'
        self.changeFeedback(error, color)

    def defaultFeedback(self):
        self.changeFeedback(self.feedbackName)

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)
