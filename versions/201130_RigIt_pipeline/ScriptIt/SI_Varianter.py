from maya import cmds, mel
from functools import partial
import pymel.core as pm
import RigItMethodsUI as rim
import subprocess

reload(rim)


class Varianter:

    def __init__(self, parent):

        #self.varPath = "C:/Users/3dami/Documents/maya/2018/temp_variants/"
        self.varPath = "P:/MBA_SE02/assets/variants/"
        self.varDict = {}
        self.pathDict = {}
        self.widgets = {}
        self.varianterLayout(parent)
        self.initializeVariants()

    def varianterLayout(self, parent='None'):
        if parent == 'None':
            return "Can't load varianter"
        self.widgets["mainLayout"] = cmds.columnLayout("Varianter", p=parent, adj=True)

        cmds.rowColumnLayout(numberOfColumns=2)
        self.widgets["char_scroll"] = cmds.textScrollList(allowMultiSelection=False, w=230, h=300,
                                                          sc=self.varListUpdate)
        self.widgets["var_scroll"] = cmds.textScrollList(allowMultiSelection=False, w=230, h=300,
                                                         sc=self.varSelected)
        self.widgets["files_scroll"] = cmds.textScrollList(allowMultiSelection=False, h=150,
                                                           sc=self.fileToScript, p=self.widgets["mainLayout"])
        cmds.popupMenu(parent=self.widgets["char_scroll"])
        cmds.menuItem(label='Explore', c=partial(self.openFolder, 'base'))
        cmds.popupMenu(parent=self.widgets["var_scroll"])
        cmds.menuItem(label='Explore', c=self.openFolder)
        cmds.popupMenu(parent=self.widgets["files_scroll"])
        cmds.menuItem(label='Explore', c=partial(self.openFolder, 'steps'))

    @staticmethod
    def getScript(*args):
        if script:
            return script
        else:
            return False

    def initializeVariants(self):
        try:
            folders = rim.getFoldersFromPath(self.varPath)
        except:
            print " // can't load variants folder"
            print ' // attempted path: %s' % self.varPath
            return
        print folders

        for variant in folders:
            name, _, var = variant.partition('_')
            if name not in self.varDict:
                self.varDict[name] = []
            if name not in self.pathDict:
                self.pathDict[name] = {}
            self.varDict[name].append(var)
            path = self.varPath + variant + '/rigging/' + variant  # + '/customSteps'
            self.pathDict[name][var] = path.replace('/', '\\')
        print self.varDict
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
        char = cmds.textScrollList(self.widgets["char_scroll"], query=True, selectItem=True)
        var = cmds.textScrollList(self.widgets["var_scroll"], query=True, selectItem=True)
        filePath = self.pathDict[char[0]][var[0]] + '\customSteps'
        pyFiles = rim.getPythonFiles(filePath)
        cmds.textScrollList(self.widgets["files_scroll"], e=True, removeAll=True)
        if not pyFiles:
            return
        for pyFile in pyFiles:
            cmds.textScrollList(self.widgets['files_scroll'], e=True, append=pyFile)
        cmds.textScrollList(self.widgets["files_scroll"], e=True, selectIndexedItem=1)
        self.fileToScript()

    def fileToScript(self, *args):
        char = cmds.textScrollList(self.widgets["char_scroll"], query=True, selectItem=True)
        var = cmds.textScrollList(self.widgets["var_scroll"], query=True, selectItem=True)
        pyFile = cmds.textScrollList(self.widgets["files_scroll"], query=True, selectItem=True)
        filePath = self.pathDict[char[0]][var[0]] + '\customSteps'
        script = ''
        if not char or not var or not pyFile:
            print 'missing something to show the file'
            return
        script = rim.readFile(filePath + '\\' + pyFile[0])
        if not script:
            print ' // failed to read or no content in pyFile: %s' % pyFile[0]
        else:
            global script

    def varListUpdate(self, *args):
        selected = cmds.textScrollList(self.widgets["char_scroll"], query=True, selectItem=True)
        cmds.textScrollList(self.widgets["var_scroll"], e=True, removeAll=True)
        if selected:
            selected = selected[0]
        else:
            return
        sortList = []
        for var in self.varDict[selected]:
            sortList.append(var)
        sortList.sort()
        for var in sortList:
            cmds.textScrollList(self.widgets['var_scroll'], e=True, append=var)

    def openFolder(self, folder='', *args):
        char = cmds.textScrollList(self.widgets["char_scroll"], query=True, selectItem=True)
        var = cmds.textScrollList(self.widgets["var_scroll"], query=True, selectItem=True)
        if char and var:
            char = char[0]
            var = var[0]
        else:
            print ' // Not enough items selected to open explorer! please select a character and a var'
            return
        path = self.pathDict[char][var]
        if folder == 'steps':
            path += '\\customSteps'
        elif folder  == 'base':
            path = self.varPath.replace('/', '\\')
        print ' // open file location: %s' % path
        subprocess.Popen('explorer %s' % path)
        # to open a file: subprocess.Popen(r'explorer /select %s' % path)
