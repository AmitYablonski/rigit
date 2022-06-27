from maya import cmds, mel
from functools import partial
import pymel.core as pm
import SnowRigMethodsUI as srm
import generalMayaTools as gmt
import subprocess

reload(srm)
reload(gmt)


class Varianter:

    def __init__(self, parent, scriptIt):

        self.varPath = "C:/Users/3dami/Documents/maya/2018/temp_variants/"
        # self.varPath = "P:/MBA_SE02/assets/variants/"
        self.feedbackName = 'Varianter'
        self.varDict = {}
        self.pathDict = {}
        self.widgets = {}
        self.char = ''
        self.var = ''
        self.scriptIt = scriptIt
        self.varianterLayout(parent)
        self.initializeVariants()

    def varianterLayout(self, parent='None'):
        if parent == 'None':
            return "Can't load varianter"
        self.widgets["top_paneLayout"] = cmds.paneLayout("Varianter", configuration='horizontal2', h=600,
                                                         paneSize=[1, 100, 50], p=parent)
        self.widgets["topLayout"] = cmds.paneLayout( configuration='top3', paneSize=[1, 50, 90])
        topLay = self.widgets["topLayout"]
        self.widgets["char_scroll"] = cmds.textScrollList(allowMultiSelection=False,# w=230, h=200,
                                                          sc=self.varListUpdate)
        self.widgets["var_scroll"] = cmds.textScrollList(allowMultiSelection=False,# w=230, h=200,
                                                         sc=self.varSelected)
        self.widgets["files_scroll"] = cmds.textScrollList(allowMultiSelection=False,# h=100,
                                                           sc=self.fileToScript)
        cmds.popupMenu(parent=self.widgets["char_scroll"])
        cmds.menuItem(label='Explore', c=partial(self.openFolder, 'base'))
        cmds.popupMenu(parent=self.widgets["var_scroll"])
        cmds.menuItem(label='Explore', c=self.openFolder)
        cmds.popupMenu(parent=self.widgets["files_scroll"])
        cmds.menuItem(label='Explore', c=partial(self.openFolder, 'steps'))

        self.widgets["runnerMakerLayoutParent"] = self.varScriptsTopLayout(self.widgets["top_paneLayout"])
        self.enableRunnerMaker(False)
        '''cmds.separator(h=7, p=mainTopLay)
        self.widgets["feedbackTextField2"] = cmds.textField(tx="", editable=False, p=mainTopLay)
        cmds.separator(h=7, p=mainTopLay)'''

        self.scriptIt.defaultFeedback()

    def enableRunnerMaker(self, enable=True):
        cmds.rowColumnLayout(self.widgets["runnerMakerLayout"], e=True, enable=enable)
        cmds.button(self.widgets['refreshButton'], e=True, enable=enable)

    def resetRunnerMaker(self):
        self.scriptIt.defaultFeedback()
        pm.text(self.widgets['runnerWarning'], e=True, l=' ')
        self.varScriptsLayout(self.widgets["runnerMakerLayoutParent"])
        self.enableRunnerMaker(False)

    def varScriptsTopLayout(self, parLay):
        mainLay = cmds.scrollLayout(p=parLay, childResizable=True)
        cmds.columnLayout(adj=True)
        #mainLay = cmds.rowColumnLayout(nc=1, p=parLay)
        #cmds.separator(h=7, p=parLay)
        cmds.rowColumnLayout(nc=3, cs=[[2,5],[3, 5]])
        pm.button('   Create New Runner   ', c=self.createNewRunner)
        self.widgets['runnerWarning'] = cmds.text('runnerWarning', l=' ', w=210)
        self.widgets['refreshButton'] = pm.button('   Refresh   ', c=self.refreshScrolls)
        self.varScriptsLayout(mainLay)
        return mainLay

    def varScriptsLayout(self, parLay):
        layName = 'runnerMakerLayout'
        if layName in self.widgets:
            cmds.deleteUI(self.widgets[layName])
        self.widgets[layName] = cmds.rowColumnLayout(nc=1, p=parLay)
        mainLay = self.widgets[layName]
        cmds.rowColumnLayout(nc=2, cs=[2,5])
        cmds.button('Add to hide selected')
        cmds.button('Add to vis switch')

        cmds.optionMenu(label='Colors') #, cc='')

    def varScriptsLayoutOld(self, parLay): # todo remove
        layName = 'runnerMakerLayoutOld'
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

    def scrollSelectCheck(self):
        if not self.char or not self.var:
            self.scriptIt.redError('Please select the desired character and variant')
            # todo possibly make it a popup warning
            return False
        else:
            return True

    def createNewRunner(self, *args):
        if not self.scrollSelectCheck():
            return
        filePath = self.pathDict[self.char][self.var] + '\customSteps'
        if not cmds.file(filePath, query=True, exists=True):
            self.scriptIt.redError("Path not found. Check if asset's folders exist, if not, populate through pipeline.")
            return
        self.enableRunnerMaker()
        self.refreshScrolls()
        self.scriptIt.changeFeedback('Runner layout', 'green')

    def refreshScrolls(self, *args):
        self.updateHighObjs()
        self.updateImportFiles()
        self.updateSkinFiles()

    def updateSkinFiles(self):
        if not self.scrollSelectCheck():
            return
        try: # todo remove this once srm is updated
            filePath = self.pathDict[self.char][self.var] + '\gSkin'
            skinFiles = srm.getSkinFiles(filePath)
            self.repopulateScrollList("imports_skin", skinFiles)
        except:
            print "//WARNING! srm isn't updated"

    def updateImportFiles(self):
        if not self.scrollSelectCheck():
            return
        filePath = self.pathDict[self.char][self.var] + '\importFiles'
        importFiles = srm.getMayaFiles(filePath)
        self.repopulateScrollList("imports_scroll", importFiles)

    def updateHighObjs(self):
        if not self.scrollSelectCheck():
            return
        charFile = "P:/MBA_SE02/assets/characters/%s/public/%s_rigging.ma" % (self.char, self.char)
        # todo remove following test line
        charFile = "C:/Users/3dami/Documents/maya/2018/scripts/Jali/JaliStuff/kermit_rigging_v013.ma"
        try: # todo once gmt is updated, remove the try/except
            highObjs = gmt.getChildrenFromFile(charFile, 'high_grp')
            print 'highObjs = %s' % highObjs
            self.repopulateScrollList("highObjs_scroll", highObjs)
        except:
            print "//WARNING! general maya tools isn't updated"


    def repopulateScrollList(self, scrollName, popuList):
        cmds.textScrollList(self.widgets[scrollName], e=True, removeAll=True)
        for pop in popuList:
            cmds.textScrollList(self.widgets[scrollName], e=True, append=pop)

    @staticmethod
    def getScript(*args):
        if script:
            return script
        else:
            return False

    def initializeVariants(self):
        try:
            folders = srm.getFoldersFromPath(self.varPath)
        except:
            print " // can't load variants folder"
            print ' // attempted path: %s' % self.varPath
            return

        for variant in folders:
            name, _, var = variant.partition('_')
            if name not in self.varDict:
                self.varDict[name] = []
            if name not in self.pathDict:
                self.pathDict[name] = {}
            self.varDict[name].append(var)
            path = self.varPath + variant + '/rigging/' + variant  # + '/customSteps'
            self.pathDict[name][var] = path.replace('/', '\\')
        # todo sort lists by abc before adding (character and variants)
        # path example: 'P:/mba_se02/assets/variants/summer_fancy/rigging/summer_fancy/customSteps'
        # path example: self.varPath + variant + '/rigging/' + variant + '/customSteps'
        sortList = []
        for char in self.varDict:
            sortList.append(char)
        sortList.sort()
        for char in sortList:
            cmds.textScrollList(self.widgets['char_scroll'], e=True, append=char)

    def varSelected(self, *args):
        self.resetRunnerMaker()
        var = cmds.textScrollList(self.widgets["var_scroll"], query=True, selectItem=True)
        if var:
            self.var = var[0]
        else:
            self.scriptIt.redError('variant selection failed')
            self.var = ''
            return
        filePath = self.pathDict[self.char][self.var] + '\customSteps'
        pyFiles = srm.getPythonFiles(filePath)
        self.repopulateScrollList('files_scroll', pyFiles)
        if not pyFiles:
            cmds.text(self.widgets['runnerWarning'], e=True, bgc=[.5, 0.8, 0.5], l=' no runner found ')
            return
        for pyFile in pyFiles:
            if pyFile == 'RUNNER.py':
                cmds.text(self.widgets['runnerWarning'], e=True, bgc=[.9, 0.2, 0.2],
                          l=' caution - runner exists - will overwrite ')
            elif pyFile.lower() == 'runner.py':
                cmds.text(self.widgets['runnerWarning'], e=True, bgc=[.6, .4, .2],
                          l=' caution - runner exists ')
        cmds.textScrollList(self.widgets["files_scroll"], e=True, selectIndexedItem=1)
        self.fileToScript()

    def fileToScript(self, *args):
        pyFile = cmds.textScrollList(self.widgets["files_scroll"], query=True, selectItem=True)
        if not self.scrollSelectCheck():
            return
        filePath = self.pathDict[self.char][self.var] + '\customSteps'
        script = ''
        if not pyFile:
            self.scriptIt.redError(' failed selecting file')
            return
        script = srm.readFile(filePath + '\\' + pyFile[0])
        if not script:
            print ' // failed to read or no content in pyFile: %s' % pyFile[0]
        else:
            global script

    def varListUpdate(self, *args):
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
            cmds.textScrollList(self.widgets['var_scroll'], e=True, append=var)

    def openFolder(self, folder='', *args):
        if self.char and self.var:
            char = self.char
            var = self.var
        else:
            print ' // Not enough items selected to open explorer! please select a character and a variant'
            return
        path = self.pathDict[char][var]
        if folder == 'steps':
            path += '\\customSteps'
        elif folder == 'base':
            path = self.varPath.replace('/', '\\')
        print ' // open file location: %s' % path
        subprocess.Popen('explorer %s' % path)
        # to open a file: subprocess.Popen(r'explorer /select %s' % path)