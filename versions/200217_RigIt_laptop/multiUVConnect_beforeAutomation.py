from maya import cmds, mel
import pymel.core as pm
from functools import partial
import UI_modules as uim
import RigItMethodsUI as rim
import generalMayaPrints as gmp
import generalMayaTools as gmt

reload(uim)
reload(rim)
reload(gmp)
reload(gmt)


class multiUVConnect:
    def __init__(self, par='', scriptIt=False):
        self.widgets = {}
        self.feedbackName = 'Multi UV Set Connection tool'
        # todo make it execute for every change on the files scroll (always keep previous selection)
        # todo add checkbox 
        self.lastFileSel = []
        mainLay = self.winBase('MultiUVConnect', self.feedbackName, par)
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def execute(self, *args):
        # todo test that map exists: maps = pm.polyUVSet(obj, q=True, auv=True)
        #  selectIndexedItem, selectItem
        objs = cmds.textScrollList(self.widgets['AllObjsScroll'], q=True, allItems=True)
        map = cmds.textScrollList(self.widgets['mapsScroll'], q=True, selectItem=True)
        allLen = cmds.textScrollList(self.widgets['mapsScroll'], q=True, allItems=True)
        mapLen = len(allLen)
        mtl = cmds.textField(self.widgets['mtlField'], q=True, tx=True)
        files = cmds.textScrollList(self.widgets['filesScroll'], q=True, selectItem=True)
        if not objs:
            self.printFeedback('No objs added', 'red')
            return
        if not map:
            self.printFeedback('No map Selects', 'red')
            return
        else:
            map = map[0]
        if not mtl:
            self.printFeedback('No material selected', 'red')
            return
        if not files:
            self.printFeedback('No file node is selected', 'red')
            return
        for item in objs:
            obj = pm.PyNode(item)
            i = self.findMapIdx(obj, map, mapLen)
            # check map name on obj
            for file in files:
                file = file.partition(' ')[0]
                pm.uvLink(uvSet=obj.uvSet[i].uvSetName, texture=file)

    def findMapIdx(self, obj, map, mapLen):
        i = 0
        while pm.getAttr(obj.uvSet[i].uvSetName) != map:
            i += 1
            if i > mapLen:
                break
        return i

    def scriptIt(self, *args):
        script = ''
        rim.showScript(script)
        return

    def checkMaterial(self, *args):
        mtl = cmds.textField(self.widgets['mtlField'], q=True, tx=True)
        filesScroll = self.widgets["filesScroll"]
        cmds.textScrollList(filesScroll, e=True, removeAll=True)
        if not mtl:
            self.defaultFeedback()
            return
        if not pm.objExists(mtl):
            self.printFeedback('Error finding shader "%s"' % mtl, 'red')
            return
        # search and add file nodes
        fileNodes = gmt.findFileTxNode(mtl)
        for attr in fileNodes:
            for file in fileNodes[attr]:
                cmds.textScrollList(filesScroll, edit=True, append='%s  (%s)' % (file, attr))

    def findMaterial(self, objScroll):  # todo make sure mtl match in all objects
        allItems = cmds.textScrollList(objScroll, q=True, allItems=True)
        if not allItems:
            return
        allMtls = []
        for item in allItems:
            shp = pm.listRelatives(item, s=True)
            conn = pm.listConnections(shp)
            for con in conn:
                if con.classification()[0] == 'shadingEngine':
                    conn2 = pm.listConnections(con)
                    for mtl in conn2:
                        if 'shader' in mtl.classification()[0]:
                            if mtl not in allMtls:
                                allMtls.append(mtl)
                else:
                    if 'shader' in con.classification()[0]:
                        if con not in allMtls:
                            allMtls.append(con)
        mtlField = self.widgets['mtlField']
        if not allMtls:
            self.printFeedback('Failed to find shader, please select manually', 'red')
            cmds.textField(mtlField, e=True, tx='')
        if len(allMtls) > 1:
            self.mtlSelectionWin(allMtls)
        else:
            cmds.textField(mtlField, e=True, tx=allMtls[0].name())
        self.checkMaterial()

    def mtlSelectionWin(self, mtls):
        if pm.window("mtlSel_win", exists=True):
            pm.deleteUI("mtlSel_win")
        self.widgets["mtlSel_win"] = pm.window("mtlSel_win", title="Select Shader", sizeable=1, rtf=True)
        self.widgets["sel_main_Layout"] = cmds.rowColumnLayout(numberOfColumns=1, adj=True)
        mtlNames = []
        for mtl in mtls:
            mtlNames.append(mtl.name())
        hight = 20 * len(mtls)
        if hight < 100:
            hight = 100
        self.widgets["mtlSelScroll"] = pm.textScrollList(append=mtlNames, allowMultiSelection=False,
                                                         sii=1, w=250, h=hight)
        pm.button(l="Select Shader", h=40, c=partial(self.mtlWinSelection, mtls))
        pm.showWindow()
        pm.window(self.widgets["mtlSel_win"], e=True, h=100)

    def mtlWinSelection(self, mtls, *args):
        idx = pm.textScrollList(self.widgets["mtlSelScroll"], query=True, selectIndexedItem=True)[0]
        idx -= 1
        mtlName = mtls[idx].name()
        pm.textField(self.widgets['mtlField'], e=True, text=mtlName)
        pm.deleteUI(self.widgets["mtlSel_win"])
        self.checkMaterial()

    def updateMaps(self, objScroll):
        mapsScroll = self.widgets["mapsScroll"]
        allObjs = cmds.textScrollList(objScroll, q=True, allItems=True)
        cmds.textScrollList(mapsScroll, e=True, removeAll=True)
        if not allObjs:
            return
        maps = pm.polyUVSet(allObjs[0], q=True, auv=True)
        for map in maps:
            cmds.textScrollList(mapsScroll, edit=True, append='%s' % map)
        # add to ui
        for i in range(1, len(allObjs)):
            objMaps = pm.polyUVSet(allObjs[i], q=True, auv=True)
            raiseError = False
            error = "UV sets not matching in %s objects" % allObjs[i]
            error2 = ' // maps for "%s" = %s \n // maps for "%s" = %s' % (allObjs[0], maps, allObjs[i], objMaps)
            if len(objMaps) != len(maps):
                raiseError = True
            for map in objMaps:
                if map not in maps:
                    raiseError = True
            if raiseError:
                print('\n')
                self.printFeedback(error, 'red')
                print(error2)

    def updateTextField(self, field, objType='', multiple=False, *args):
        self.defaultFeedback()
        sele = pm.selected()
        if len(sele) == 0:
            self.printFeedback('select an object and try again')
            return
        if multiple:
            if objType:
                temp = []
                for obj in sele:
                    if objType != obj.type():
                        self.printFeedback('Selection must be a %s node, skipping "%s"' % (objType, obj.name()))
                        temp.append(obj)
                sele = temp
            if len(sele) == 1:
                cmds.textField(field, e=True, tx=sele[0].name())
            else:
                cmds.textField(field, e=True, tx=gmp.cleanListForPrint(sele))
        else:
            if len(sele) == 1:
                if objType:
                    if objType != sele[0].type():
                        self.printFeedback('Selection must be a %s node' % objType)
                        return
                cmds.textField(field, e=True, tx=sele[0].name())
            else:
                self.printFeedback('select a single object and try again')
        self.checkMaterial()

    def selectAndAddToField(self, parLay, buttonText, objType='', fieldTx='', width='', multiple=False):
        if width:
            pm.rowLayout(nc=2, columnOffset2=[0, 5], w=width, p=parLay)
        else:
            pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=parLay)
        but = pm.button(l=buttonText)
        txField = cmds.textField()
        pm.button(but, e=True, c=partial(self.updateTextField, txField, objType, multiple))
        if fieldTx:
            cmds.textField(txField, e=True, tx=fieldTx)
        return txField

    def updateScrolls(self, scrollName, remove=False, clear=False, *args):
        self.defaultFeedback()
        change = False
        scroll = self.widgets[scrollName + "Scroll"]
        if clear:
            cmds.textScrollList(scroll, e=True, removeAll=True)
            uim.resizeScroll(scroll)
            self.updateMaps(scroll)
            return
        if remove:
            selItem = cmds.textScrollList(scroll, query=True, selectIndexedItem=True)
            if not selItem:
                self.orangeFeedback('Nothing selected to remove')
                return
            selItem.reverse()
            for item in selItem:
                cmds.textScrollList(scroll, e=True, removeIndexedItem=item)
                change = True
        else:
            items = cmds.textScrollList(scroll, q=True, allItems=True)
            sele = pm.selected()
            for sel in sele:
                if items:
                    if sel.name() not in items:
                        cmds.textScrollList(scroll, edit=True, append='%s' % (sel.name()))
                        change = True
                    else:
                        self.printFeedback('%s already listed' % sel.name())
                else:
                    cmds.textScrollList(scroll, edit=True, append='%s' % (sel.name()))
                    change = True
        # resize scroll
        if change:
            uim.resizeScroll(scroll)
            self.updateMaps(scroll)
            self.findMaterial(scroll)

    def addAllObjScroll(self, mainLay):
        scrollName = 'AllObjs'
        # add title
        pm.separator(h=3, p=mainLay)
        pm.text('Add objects to affect', p=mainLay)
        pm.separator(h=7, p=mainLay)
        # control buttons
        cmds.rowColumnLayout(nc=3, cs=[[2, 4], [3, 4]], adj=True, p=mainLay)
        cmds.button('add from\nselection', c=partial(self.updateScrolls, scrollName))
        cmds.button('remove\nfrom list', c=partial(self.updateScrolls, scrollName, True))
        cmds.button('clear\nlist', c=partial(self.updateScrolls, scrollName, clear=True))
        # scroll
        self.widgets[scrollName + "Scroll"] = cmds.textScrollList(allowMultiSelection=True, h=130, p=mainLay)

    def mapSelected(self):
        objs = cmds.textScrollList(self.widgets['AllObjsScroll'], q=True, allItems=True)
        maps = cmds.textScrollList(self.widgets['mapsScroll'], q=True, selectItem=True)
        filesScroll = self.widgets['filesScroll']
        files = cmds.textScrollList(filesScroll, q=True, allItems=True)
        allLen = cmds.textScrollList(self.widgets['mapsScroll'], q=True, allItems=True)
        mapLen = len(allLen)
        if not objs:
            return
        if not maps:
            return
        if not files:
            return
        obj = pm.PyNode(objs[0])
        # check map name on obj
        i = self.findMapIdx(obj, maps[0], mapLen)
        linked = pm.uvLink(query=True, uvSet=obj.uvSet[i].uvSetName)
        filesIdx = []
        for i, file in enumerate(files):
            file = file.partition(' ')[0]
            if file in linked:
                filesIdx.append(i+1)
        cmds.textScrollList(filesScroll, e=True, deselectAll=True)
        cmds.textScrollList(filesScroll, e=True, selectIndexedItem=filesIdx)

    def addMapsScroll(self, parLay):
        mainLay = pm.columnLayout(adj=True, p=parLay)
        # add title
        pm.separator(h=3, p=mainLay)
        self.widgets['mapsText'] = pm.text('UV sets\Maps:', p=mainLay)
        pm.separator(h=3, p=mainLay)
        # scroll
        self.widgets["mapsScroll"] = cmds.textScrollList(allowMultiSelection=False, h=70, p=mainLay,
                                                         sc=self.mapSelected)

    def addFilesScroll(self, parLay):
        mainLay = pm.columnLayout(adj=True, p=parLay)
        # add title
        pm.separator(h=3, p=mainLay)
        pm.text('Connected Files:', p=mainLay)
        pm.separator(h=3, p=mainLay)
        # scroll
        self.widgets["filesScroll"] = cmds.textScrollList(allowMultiSelection=True, h=215, p=mainLay)

    def populateUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)
        pm.text(l=self.feedbackName, font='boldLabelFont', p=mainLay)
        pm.separator(h=7, p=mainLay)

        # split layout
        splitLay = cmds.paneLayout(configuration='vertical2', p=mainLay)
        L_Lay = pm.columnLayout(adj=True)
        R_Lay = pm.columnLayout(adj=True, p=splitLay)

        # left layout
        self.addAllObjScroll(L_Lay)
        self.addMapsScroll(L_Lay)

        # right layout
        pm.separator(h=3, p=R_Lay)
        pm.text(l='Select Material/Texture:', p=R_Lay)
        pm.separator(h=7, p=R_Lay)

        self.widgets['mtlField'] = self.selectAndAddToField(R_Lay, 'Select')
        cmds.textField(self.widgets['mtlField'], e=True, cc=self.checkMaterial)
        self.addFilesScroll(R_Lay)

        # buttons
        pm.separator(h=7, st='double', p=mainLay)
        cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
        cmds.button(l='Execute', h=28, c=self.execute)
        if scriptIt:
            cmds.button(l='Script it', w=100, c=self.scriptIt)
        else:
            pm.separator(w=100, style='none')
        # pm.separator(h=7, st='double', p=mainLay)

    def winBase(self, name, title, par):
        winName = name + "_window"
        mainLay = "mainLay"
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
            form = pm.formLayout(title, p=par)
        # form and main layout
        self.widgets['topForm'] = form
        self.widgets[mainLay] = pm.columnLayout(adj=True)
        mLay = self.widgets[mainLay]
        pm.formLayout(form, e=True, af=((mLay, 'top', 0), (mLay, 'left', 0),
                                        (mLay, 'right', 0), (mLay, 'bottom', 0)))

        # feedback layout
        fLay = pm.columnLayout(adj=True, p=self.widgets['topForm'])
        pm.separator(h=7)
        self.widgets["feedback"] = cmds.textField(tx="", editable=False)  # , p=self.widgets['topForm'])
        pm.formLayout(form, e=True, af=((fLay, 'left', 0),
                                        (fLay, 'right', 0), (fLay, 'bottom', 0)))

        if asWindow:
            cmds.showWindow()
        self.defaultFeedback()
        return self.widgets[mainLay]

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
