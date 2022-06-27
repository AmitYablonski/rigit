from maya import cmds, mel
from functools import partial
import pymel.core as pm
import RigItMethodsUI as rim
import generalMayaTools as gmt
import subprocess
import VarianterRunnerMaker as vrm

reload(rim)
reload(gmt)
reload(vrm)


class VarMaker:

    def __init__(self, parent, scriptIt):

        global script
        self.varPath = "C:/Users/3dami/Documents/maya/2018/temp_variants/"
        # self.varPath = "P:/MBA_SE02/assets/variants/"
        self.feedbackName = 'Variant Maker'
        self.resetLay = 'varMakerResetLayout'
        self.varDict = {}
        self.pathDict = {}
        self.widgets = {}
        self.char = ''
        self.charList = []
        self.var = ''
        self.varList = []
        self.width = 300
        self.collapse = False  # todo make this collapsed when done?
        self.scriptIt = scriptIt
        self.varianterLayout(parent)
        self.initializeVariants()
        self.initializeScrolls()

    def varianterLayout(self, parLay):
        if parLay == 'None':
            print("Can't load " + self.feedbackName)
            return
        self.widgets["topLayout"] = cmds.rowColumnLayout("VarMaker", numberOfColumns=1, adj=True, p=parLay)
        self.widgets[self.resetLay] = cmds.scrollLayout(childResizable=True, h=600)
        mainLay = self.widgets[self.resetLay]
        # todo test self.varListUpdate (test what's needed from there)
        ''' 
        # R-click
        cmds.popupMenu(parent=self.widgets["char_scroll"])
        cmds.menuItem(label='Explore', c=partial(self.openFolder, 'base'))
        '''
        # self.widgets[self.resetLay] = self.varScriptsTopLayout(self.widgets["topLayout"])

        cmds.columnLayout(adj=True, p=mainLay)
        # mainLay = cmds.rowColumnLayout(nc=1, p=parLay)
        # cmds.separator(h=7, p=parLay)
        self.varMakerPopulate(mainLay)

        cmds.rowColumnLayout(nc=2, cs=[2, 5], p=mainLay)
        # pm.button('   Compile Runner   ', c=self.compileRunner)
        # self.widgets['compileFeedback'] = cmds.text('runnerWarning', l=' ', w=210)

        self.scriptIt.defaultFeedback()

    def varMakerPopulate(self, parLay):
        layName = 'runnerMakerLayout'
        if layName in self.widgets:
            cmds.deleteUI(self.widgets[layName])
        self.widgets[layName] = cmds.rowColumnLayout(nc=1, p=parLay)
        mainLay = self.widgets[layName]

        cmds.separator(h=10, p=mainLay)  # this changes top width
        pm.text('Variant Runner Creator', font='boldLabelFont')
        cmds.separator(h=10, p=mainLay)

        charVarLayout = cmds.rowColumnLayout(nc=3, p=mainLay)
        charVarMain = cmds.rowColumnLayout(nc=1)
        self.widgets['charOptLayout'] = cmds.rowColumnLayout(nc=1, p=charVarMain)
        self.widgets['varOptLayout'] = cmds.rowColumnLayout(nc=1, p=charVarMain)
        cmds.separator(w=10, vis=False, p=charVarLayout)
        cmds.rowColumnLayout(nc=1, p=charVarLayout)
        cmds.separator(h=17, vis=False)
        pm.button('Explore', w=92, c=self.openFolder)

        cmds.separator(h=6, p=mainLay)
        cmds.separator(h=4, p=mainLay)
        pm.button('Compile Runner', p=mainLay, c=self.compileRunner)
        cmds.separator(h=13, p=mainLay)

        layoutSets = [['importFiles', 'Import Files'],
                      ['importSkins', 'Import Skins']]
        self.populateImportLayouts(layoutSets, mainLay)

        cmds.separator(h=7, p=mainLay)

        self.populateHighGrpLayout('highGrp', 'High Grp Objects', mainLay)

        cmds.separator(h=7, p=mainLay)

    def populateHighGrpLayout(self, name, title, parLay):
        frameName = name + "Frame"
        mainFrame = name + 'L'
        self.widgets[frameName] = cmds.frameLayout(l=title, collapsable=True, w=400, cl=self.collapse, p=parLay)

        frameLay = cmds.rowColumnLayout(nc=2, cs=[[2, 3], [3, 3]], p=parLay)
        self.widgets[mainFrame] = cmds.textScrollList(allowMultiSelection=True, h=400, w=180)
        rightMainLay = cmds.rowColumnLayout(nc=1, rs=[2, 10], p=frameLay)

        rightLay = cmds.rowColumnLayout(nc=2, cs=[[2, 3], [3, 3]], p=rightMainLay)
        for op in ['Hide', 'Vis']:
            cmds.rowColumnLayout(nc=1, rs=[2, 10], p=rightLay)
            cmds.separator(h=35, vis=False)
            pm.button('  >>  ', h=25, c=partial(self.addToScroll, mainFrame, name + op))
            pm.button('  <<  ', h=25, c=partial(self.removeFromScroll, name + op))
            cmds.rowColumnLayout(nc=1, p=rightLay)
            cmds.text('Mesh ' + op)
            self.widgets[name + op] = cmds.textScrollList(allowMultiSelection=True, h=120, w=180)


    def populateImportLayouts(self, layoutSets, mainLay):
        for name, title in layoutSets:
            frameName = name + "Frame"
            self.widgets[frameName] = cmds.frameLayout(l=title, collapsable=True, w=400, cl=self.collapse, p=mainLay)
            if "highGrp" in name:
                self.addScrollListLayout(name, self.widgets[frameName])
            else:
                self.addScrollListLayout(name, self.widgets[frameName])

    def enableImportLayout(self, name, val, *args):  # todo remove?
        cmds.frameLayout(self.widgets[name + "Frame"], e=True, enable=val)


    def addScrollListLayout(self, name, parLay, scrollH=120, scrollW=180):  # todo take this to main rigIt files
        frameLay = cmds.rowColumnLayout(nc=3, cs=[[2, 3], [3, 3]], p=parLay)
        self.widgets[name + 'L'] = cmds.textScrollList(allowMultiSelection=True, h=scrollH, w=scrollW)
        cmds.rowColumnLayout(nc=1, rs=[2, 10])
        cmds.separator(h=20, vis=False)
        pm.button('  >>  ', h=25, c=partial(self.addToScroll, name + 'L', name + 'R'))
        pm.button('  <<  ', h=25, c=partial(self.removeFromScroll, name + 'R'))
        self.widgets[name + 'R'] = cmds.textScrollList(allowMultiSelection=True, h=scrollH, w=scrollW, p=frameLay)
        return frameLay

    def addToScroll(self, orig, dest, *args):
        self.scriptIt.defaultFeedback()
        sele = cmds.textScrollList(self.widgets[orig], q=True, selectItem=True)
        allItems = cmds.textScrollList(self.widgets[dest], q=True, allItems=True)
        if not allItems:
            cmds.textScrollList(self.widgets[dest], e=True, append=sele)
            return
        for sel in sele:
            if sel in allItems:
                self.scriptIt.changeFeedback('"%s" is already added' % sel, 'orange')
                continue
            cmds.textScrollList(self.widgets[dest], e=True, append=sel)

    def removeFromScroll(self, name, *args):
        self.scriptIt.defaultFeedback()
        sele = cmds.textScrollList(self.widgets[name], q=True, selectItem=True)
        if sele:
            for sel in sele:
                cmds.textScrollList(self.widgets[name], e=True, removeItem=sel)

    def updateCharVar(self, *args):
        charV = pm.optionMenu(self.widgets['charSel'], q=True, sl=True)
        self.char = self.charList[charV - 1]
        varV = pm.optionMenu(self.widgets['varSel'], q=True, sl=True)
        self.var = self.varList[varV - 1]
        self.initializeScrolls()

    def varMakerPopulateOld(self, parLay):  # todo remove
        layName = 'runnerMakerLayout'
        if layName in self.widgets:
            cmds.deleteUI(self.widgets[layName])
        self.widgets[layName] = cmds.rowColumnLayout(nc=1, p=parLay)
        # self.widgets['optionMenu'] = cmds.optionMenu(label='optionMenu:')

        cmds.text('  High Grp Objs:', al='left')
        cmds.rowColumnLayout(nc=2, p=self.widgets[layName])
        self.widgets["highObjs_scroll"] = cmds.textScrollList(allowMultiSelection=True, w=170, h=200)
        highObjLay = cmds.rowColumnLayout(nc=1)
        cmds.rowColumnLayout(nc=2)
        cmds.button('Add to hide selected')
        cmds.button('Add to vis switch')
        cmds.rowColumnLayout(nc=1, p=highObjLay)
        cmds.text('add switches')

        cmds.text('  Import Files:', al='left', p=self.widgets[layName])
        cmds.rowColumnLayout(nc=2, p=self.widgets[layName])
        self.widgets["imports_scroll"] = cmds.textScrollList(allowMultiSelection=True, w=170, h=100)
        importObjLay = cmds.rowColumnLayout(nc=1)
        cmds.rowColumnLayout(nc=2)
        cmds.button('Add to hide selected')
        cmds.button('Add to vis switch')
        cmds.rowColumnLayout(nc=1, p=importObjLay)
        cmds.text('add switches')

        cmds.text('  Import Skin:', al='left', p=self.widgets[layName])
        cmds.rowColumnLayout(nc=2, p=self.widgets[layName])
        self.widgets["imports_skin"] = cmds.textScrollList(allowMultiSelection=True, w=170, h=100)
        cmds.rowColumnLayout(nc=1)
        cmds.button('import skin')
        # todo show what is under "world" in the selected import files
        # todo allow parenting them (probably either to high_grp or setup)

    def resetRunnerMaker(self):  # todo make reset work with current UI (or delete the reset)
        self.scriptIt.defaultFeedback()
        pm.text(self.widgets['runnerWarning'], e=True, l=' ')
        self.varMakerPopulate(self.widgets[self.resetLay])
        self.enableRunnerMaker(False)

    def scrollSelectCheck(self):
        if not self.char or not self.var:
            self.scriptIt.printFeedback('Please select the desired character and variant')
            # todo possibly make it a popup warning
            return False
        else:
            return True

    def compileRunner(self, *args):
        if not self.scrollSelectCheck():
            return
        script = vrm.importsMaker(self.char, self.var, [])  # todo import files

        # filePath = self.pathDict[self.char][self.var] + '\customSteps'
        # if not cmds.file(filePath, query=True, exists=True):
        #    self.scriptIt.printFeedback(
        #        "Path not found. Check if asset's folders exist, if not, populate through pipeline.")
        #    return
        if script:
            global script
            self.scriptIt.changeFeedback("Compiled!", "green")
        else:
            self.scriptIt.printFeedback("Compiling failed!", "red")

    def refreshScrolls(self, *args):
        # todo refreshScrolls
        return

    def initializeVariants(self):
        try:
            folders = rim.getFoldersFromPath(self.varPath)
        except:  # todo make it red error?
            print(" // can't load variants folder")
            print(' // attempted path: %s' % self.varPath)
            return
        # path example: 'P:/mba_se02/assets/variants/summer_fancy/rigging/summer_fancy/customSteps'
        # path example: self.varPath + variant + '/rigging/' + variant + '/customSteps'
        for variant in folders:
            name, _, var = variant.partition('_')
            if name not in self.varDict:
                self.varDict[name] = []
            if name not in self.pathDict:
                self.pathDict[name] = {}
            self.varDict[name].append(var)
            path = self.varPath + variant + '/rigging/' + variant  # + '/customSteps'
            self.pathDict[name][var] = path.replace('/', '\\')
        sortList = []
        for char in self.varDict:
            sortList.append(char)
        sortList.sort()
        self.widgets['charSel'] = pm.optionMenu(label='   Character  ', cc=self.updateVarList, w=300, h=20,
                                                p=self.widgets['charOptLayout'])
        self.charList = []
        for char in sortList:
            pm.menuItem(label=char)
            self.charList.append(char)
        self.updateVarList(sortList[0])

    def updateHighObjs(self):
        if not self.scrollSelectCheck():
            return
        charFile = "P:/MBA_SE02/assets/characters/%s/public/%s_rigging.ma" % (self.char, self.char)
        # todo remove following test line
        charFile = "C:/Users/3dami/Documents/maya/2018/scripts/Jali/JaliStuff/kermit_rigging_v013.ma"
        highObjs = gmt.getChildrenFromFile(charFile, 'high_grp')
        self.repopulateScrollList("highGrpL", highObjs)  # todo check why it's not populating

    def initializeScrolls(self):
        # todo clear all scrolls
        mainPath = self.pathDict[self.char][self.var]
        importsPath = mainPath + '\importFiles'
        skinsPath = mainPath + '\gSkin'

        importFiles = rim.getMayaFiles(importsPath)
        # print('importFiles: %s' % importFiles)
        self.repopulateScrollList("importFilesL", importFiles)
        self.clearScroll("importFilesR")

        skinFiles = rim.getFilesFromPath(skinsPath, 'gSkin')
        # print('skinFiles: %s' % skinFiles)
        self.repopulateScrollList("importSkinsL", skinFiles)
        self.clearScroll("importSkinsR")
        self.clearScroll("highGrpR")
        # print('highGrp: %s' % skinFiles)
        self.updateHighObjs()

    def repopulateScrollList(self, scrollName, popuList):
        cmds.textScrollList(self.widgets[scrollName], e=True, removeAll=True)
        sel = False
        for pop in popuList:
            cmds.textScrollList(self.widgets[scrollName], e=True, append=pop)
            sel = True
        if sel:
            cmds.textScrollList(self.widgets[scrollName], e=True, selectIndexedItem=1)

    def clearScroll(self, scroll):
        cmds.textScrollList(self.widgets[scroll], e=True, removeAll=True)

    def updateVarList(self, charSel, *args):
        if 'varSel' in self.widgets:
            cmds.deleteUI(self.widgets['varSel'])
        self.widgets['varSel'] = pm.optionMenu(label='   Variant      ', w=300, h=20, p=self.widgets['varOptLayout'],
                                               cc=self.updateCharVar)
        self.varList = []
        for var in self.varDict[charSel]:
            pm.menuItem(label=var)
            self.varList.append(var)
        self.updateCharVar()

    '''def varListUpdate(self, *args):  # todo remove?
        selected = cmds.textScrollList(self.widgets["char_scroll"], query=True, selectItem=True)
        cmds.textScrollList(self.widgets["var_scroll"], e=True, removeAll=True)
        self.resetRunnerMaker()
        self.var = ''
        if selected:
            selected = selected[0]
            self.char = selected
        else:
            self.char = ''
            return
        sortList = []
        for var in self.varDict[selected]:
            sortList.append(var)
        sortList.sort()
        for var in sortList:
            cmds.textScrollList(self.widgets['var_scroll'], e=True, append=var)'''

    def openFolder(self, folder='', *args):
        if self.char and self.var:
            char = self.char
            var = self.var
        else:
            self.scriptIt.printFeedback('Not enough items selected to open explorer!')
            return
        path = self.pathDict[char][var]
        if folder == 'steps':
            path += '\\customSteps'
        elif folder == 'base':
            path = self.varPath.replace('/', '\\')
        print
        ' // open file location: %s' % path
        subprocess.Popen('explorer %s' % path)
        # to open a file: subprocess.Popen(r'explorer /select %s' % path)

    @staticmethod
    def getScript(*args):
        if script:
            return script
        else:
            return False
