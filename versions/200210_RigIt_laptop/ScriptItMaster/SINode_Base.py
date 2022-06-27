from maya import cmds, mel
import pymel.core as pm
from functools import partial
import SI_commonScripts as sic


# todo if custom maya node, use this to edit attribute in the attr editor pm.editorTemplate

class SIBase:
    _neededImports = []
    _nodeName = "ScriptIt!"
    _inputs = {}
    _outputs = {}
    _script = ''
    _defaultFeedback = "Script It!"
    _showScript = _defaultFeedback

    def __init__(self, parentNode):
        '''
        :param parentNode: the main node where all the other nodes reside
        '''
        # todo decide if a tab layout is good for the connections - their own section
        self._parentNode = parentNode
        self.widgets = {"importFilePath": {}}
        self.settings()

    def settings(self, *args):
        self.widgets["window"] = cmds.window(title="Script It Settings", sizeable=1, rtf=True)
        self.widgets["menuBarLayout"] = cmds.menuBarLayout()
        self.widgets["topMainLayout"] = cmds.columnLayout(adj=True)

        # node name
        cmds.separator(h=7, p=self.widgets["topMainLayout"])
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[1, 80],
                       p=self.widgets["topMainLayout"])
        cmds.text(l="Node Name:")
        self.widgets["NodeName"] = cmds.textField(tx=self._nodeName, cc=self.updateNodeName)
        cmds.separator(h=3, p=self.widgets["topMainLayout"])
        self.widgets["importLayout"] = cmds.columnLayout(adj=True, p=self.widgets["topMainLayout"])
        cmds.separator(h=3, p=self.widgets["topMainLayout"])

        # populate drop down menu
        self.populateDropDownMenu()
        # the nodes UI will be created/initialized here
        self.editor(self.widgets["topMainLayout"])

        # todo every change that is done in the UI will get automatically updated with self.scriptIt
        # bottom buttons(compile / show)
        # todo create "compiled indication" (to show if _script is updated)
        cmds.separator(h=7, p=self.widgets["topMainLayout"])
        self.widgets["buttons_layout"] = cmds.rowColumnLayout(nc=3, adj=True, adjustableColumn=2,
                                                              p=self.widgets["topMainLayout"])
        # scriptItButtons = cmds.rowColumnLayout(nc=2, adj=True, p=self.widgets["topMainLayout"])
        cmds.button(w=199, l="Compile Script!", c=self.scriptIt)
        cmds.separator(vis=False)
        self.widgets["showScript"] = cmds.button(w=199, l="Show script", c=self.showScript,
                                                 enable=False)  # todo make it available only after it's compiled?

        cmds.separator(h=7, p=self.widgets["topMainLayout"])
        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False,
                                                           p=self.widgets["topMainLayout"])
        if self.widgets["importFilePath"]:
            self.rebuildFileImport()

        self.defaultFeedback()
        cmds.showWindow()

    def populateDropDownMenu(self):
        cmds.menu(label='Add', p=self.widgets["menuBarLayout"])
        cmds.menuItem(divider=True)
        cmds.menuItem(label='Import File', c=self.addImport)

        cmds.menu(label='Edit', p=self.widgets["menuBarLayout"])
        cmds.menuItem(label='Connections', enable=False)  # todo <<----

    def editor(self, parent1):
        # This is where you make the layout in Inheritance
        return

    def scriptIt(self, *args):
        '''
        Start compiling the script.
        '''
        self.defaultFeedback()
        if self.widgets["importFilePath"]:
            script = self.addFileImportScripts() + "\n\n" + self.customScriptIt()
        else:
            script = self.customScriptIt()
        self.scriptCompiled(script)

    def customScriptIt(self):
        script = 'Test Script It - well, does it work?'
        return script

    def scriptCompiled(self, script):
        '''
        updates the node with the compiled script
        :param script:
        '''
        self._script = script
        self.changeFeedback("Script Compiled!", "green")
        self.enableShowScript()

    def getScript(self):
        '''
        :return: if compiled, returns the script
        '''
        if self._script:
            return True, self._script
        else:
            return False, ""

    def addInput(self, inAttr, source):
        '''

        :param inAttr: in attr of the current node to connect
        :param source: the source to connect to the in attr
        :return: none
        '''
        self._inputs[inAttr] = source

    def hasInputs(self):
        '''
        :return: boolean - True if it has inputs
        '''
        if self._inputs:
            return True
        else:
            return False

    def getInputs(self):
        '''
        :return: a list with the node's inputs
        '''
        return self._inputs

    def addOutput(self, outAttr, destination):
        '''
        :param outAttr: out attr of the current node to connect
        :param destination: the destination to connect the out attr
        :return: none
        '''
        self._outputs[outAttr] = destination

    def hasOutputs(self):
        '''
        :return: boolean - True if it has outputs
        '''
        if self._outputs:
            return True
        else:
            return False

    def getOutputs(self):
        '''
        :return: a list with the node's outputs
        '''
        return self._outputs

    def getNeededImports(self):
        '''
        :return: a list with the needed imports
        '''
        return self._neededImports

    def getNodeName(self):
        return self._nodeName

    def updateNodeName(self, *args):
        newTx = cmds.textField(self.widgets["NodeName"], q=True, tx=True)
        self._nodeName = newTx
        self._parentNode.updateButtonName(self, newTx)

    def addImport(self, path="", clash="", *args):  # todo add the file import UI
        parent1 = pm.columnLayout(adj=True, p=self.widgets["importLayout"])

        pm.rowLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[1, 80], p=parent1)
        pm.text(l="Import File: ")
        if not path:
            path = ""
        pathField = pm.textField(tx=path)
        pm.textField(pathField, e=True, cc=partial(self.updateFilePath, parent1, pathField, "path"))

        pm.rowLayout(numberOfColumns=3, adjustableColumn=2, columnWidth=[1, 80], p=parent1)
        pm.text(l="Clash Prefix: ")
        if not clash:
            clash = ""
        clashField = pm.textField(tx=clash)
        pm.textField(clashField, e=True, cc=partial(self.updateFilePath, parent1, clashField, "clash"))
        pm.button(l="Remove Import", c=partial(self.removeFileImport, parent1))

        pm.separator(h=3, p=parent1)
        # update import dictionary
        self.widgets["importFilePath"][parent1] = [path, clash]

    def updateFilePath(self, key, field, type, *args):
        text = pm.textField(field, q=True, tx=True)
        # todo check if the string is passed with quotes. if not, add them
        if type == "path":
            self.widgets["importFilePath"][key][0] = text
        else:
            self.widgets["importFilePath"][key][1] = text

    def removeFileImport(self, layout, *args):
        self.widgets["importFilePath"].pop(layout)
        pm.columnLayout(layout, e=True, enable=False, visible=False)

    def rebuildFileImport(self):
        temp = self.widgets["importFilePath"]
        self.widgets["importFilePath"] = {}
        for i in temp:
            path = temp[i][0]
            clash = temp[i][0]
            self.addImport(path, clash)

    def addFileImportScripts(self):
        script = ""
        diction = self.widgets["importFilePath"]
        for i in diction:
            path = diction[i][0]
            clash = diction[i][1]
            script += "%s\n" % sic.importScript(path, clash)
        return script

    def defaultFeedback(self):
        self.changeFeedback(self._defaultFeedback)

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)

    def enableShowScript(self):
        cmds.button(self.widgets["showScript"], e=True, enable=True)

    def showScript(self, *args):
        if self._script:
            cmds.window(title=self._showScript, sizeable=1, rtf=True)
            cmds.rowColumnLayout(nc=1, adj=True)
            sField = cmds.scrollField(tx=self._script, w=550)
            numOfLines = cmds.scrollField(sField, q=True, numberOfLines=True)
            hight = numOfLines * 16
            if hight > 700:
                hight = 700
            if hight < 150:
                hight = 150
            cmds.scrollField(sField, e=True, h=hight)
            cmds.showWindow()
        else:
            self.changeFeedback("Script isn't compiled", "red")
