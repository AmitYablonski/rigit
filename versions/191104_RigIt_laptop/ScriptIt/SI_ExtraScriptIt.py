from maya import cmds, mel
from functools import partial
import RigItMethodsUI as rim
import pymel.core as pm
import generalMayaTools as gmt


class ExtraScriptIt:

    def __init__(self, parent, path):

        self.widgets = {}
        self.path = path
        self.pathEx = path + "/Extras"
        print
        "Ex path is: %s" % self.pathEx
        self.extraTab(parent)

    def extraTab(self, parent='None'):
        if parent == 'None':
            return "Can't load extraTab"
        self.widgets["extra_mainLayout"] = cmds.columnLayout("Extra", p=parent, adj=True, w=445)
        mainL = self.widgets["extra_mainLayout"]

        self.populateExtras(mainL)
        cmds.separator(h=7, p=mainL)
        '''
        self.widgets["scriptField"] = cmds.scrollField(h=300, p=mainL)
        cmds.separator(h=7, p=mainL)
        '''

        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False, p=mainL)
        self.defaultFeedback()

    def scriptIt(self, file, folder, *args):
        self.defaultFeedback()
        filePath = self.pathEx + "/" + folder + "/" + file + ".py"
        print
        filePath
        if cmds.file(filePath, query=True, exists=True):
            f = open(filePath, 'r')
            read = ""
            for line in f:
                read += line
            self.showScript(read + " ")
        else:
            self.errorFeedback("error reading file %s\n" % file)

    def showScript(self, text):
        # todo query add from radio button
        cmds.window(title="Extra ScripIt!", sizeable=1, rtf=True)
        cmds.rowColumnLayout(nc=1, adj=True)
        sField = cmds.scrollField(tx=text, w=550)
        numOfLines = cmds.scrollField(sField, q=True, numberOfLines=True)
        hight = numOfLines * 16
        if hight > 700:
            hight = 700
        if hight < 150:
            hight = 150
        cmds.scrollField(sField, e=True, h=hight)
        cmds.showWindow()

    def populateExtras(self, parent='None'):
        if parent == 'None':
            return "Can't load populate layout"
        buttonLayout = cmds.rowColumnLayout(p=parent, nc=1, adj=True)
        self.listScripts(buttonLayout)

    def listScripts(self, parent):
        folders = rim.getFoldersFromPath(self.pathEx)
        countAll = 0
        wi = 425 / 4
        hue = 0
        for folder in folders:
            cmds.separator(p=parent, h=7)
            cmds.text(folder, font="boldLabelFont", bgc=[.15, .15, .15], p=parent)
            cmds.separator(p=parent, h=7)
            count = 0
            buttonLayout = cmds.rowColumnLayout(p=parent, nc=4, cs=[[2, 5], [3, 5], [4, 5]])
            pyFiles = rim.getPythonFiles(self.pathEx + "/" + folder)
            for file in pyFiles:
                self.addPythonButton(file.partition(".")[0], folder, w=wi)  # , bgc=[hue, hue, hue]
                count += 1
            countAll += count
            for i in range(2, (count / 4) + 2):
                cmds.rowColumnLayout(buttonLayout, e=True, rs=[i, 5])
        return countAll

    def addPythonButton(self, file, folder, w='', bgc=''):
        ann = "Add " + file + "script to ScripIt"
        if bgc:
            button = cmds.button(l=file, c=partial(self.scriptIt, file, folder), ann=ann, bgc=bgc)
        else:
            button = cmds.button(l=file, c=partial(self.scriptIt, file, folder), ann=ann)
        if w:
            cmds.button(button, e=True, w=w)

    def defaultFeedback(self):
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=(.25, .25, .25), tx="Extras for ScriptIt")

    def errorFeedback(self, message):
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=(.6, .3, .3), tx=message)

    def attrRadioUpdate(self, *args):
        attr = cmds.radioButtonGrp(self.widgets["attr_radio"], q=True, select=True)
        if attr is 4:
            cmds.frameLayout(self.widgets["enumNames_frameLayout"], edit=True, enable=True)
        else:
            cmds.frameLayout(self.widgets["enumNames_frameLayout"], edit=True, enable=False)
        if attr is 2 or attr is 3:
            cmds.frameLayout(self.widgets["numAttrs_frameLayout"], edit=True, enable=True)
        else:
            cmds.frameLayout(self.widgets["numAttrs_frameLayout"], edit=True, enable=False)
