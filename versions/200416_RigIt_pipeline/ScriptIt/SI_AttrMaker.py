from maya import cmds, mel
from functools import partial
import pymel.core as pm
import generalMayaTools as gmt


class AttrMaker:

    def __init__(self, parent):

        self.selection = []
        self.widgets = {}
        self.name = ""
        self.min = ""
        self.max = ""
        self.default = 0
        self.loop = ["", ""]
        self.attrMaker(parent)

    def attrMaker(self, parent='None'):
        if parent == 'None':
            return "Can't load attrMaker"
        self.widgets["attrMaker_mainLayout"] = cmds.columnLayout("Attr Maker", p=parent, adj=True)
        # todo make it optional for the object to be named and not only selected
        # todo make a check box to create check on highGrp
        '''
        try:
            pm.addAttr(highGrp, longName="attrName", attributeType="enum", enumName="off:on")
            highGrp.setAttr("attrName", keyable=True)
        except:
            print traceback.print_exc()
            print '{} has the attribute'.format(highGrp)
        pm.connectAttr(object + ".attr", highGrp + ".c_character")
        '''

        # Name
        cmds.text("Step 1: Name the attribute")
        cmds.rowColumnLayout(nc=2)
        cmds.text("Name: ")
        self.widgets["nameLine_text"] = cmds.textField(w=120, cc=self.nameTextChange)

        #  Data Type
        self.widgets["dataType_frameLayout"] = cmds.frameLayout(label="Data Type", collapsable=False, w=400,
                                                                parent=self.widgets["attrMaker_mainLayout"])
        cmds.text("Step 2: Select attribute type and settings")
        self.widgets["attr_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=4, cw4=[100, 100, 100, 100], select=2,
                                                         labelArray4=['Vector', 'Integer', 'Float', 'Enum'], h=19,
                                                         cc=self.attrRadioUpdate)

        cmds.rowColumnLayout(nc=2)
        cmds.text("    Add and connect to highGrp:    ")
        self.widgets["highGrp_checkBox"] = cmds.checkBox('yes')

        #   #   Attr options    #   #
        attrOpt = cmds.rowColumnLayout(nc=2, parent=self.widgets["attrMaker_mainLayout"])

        # Numeric attribute options
        self.widgets["numAttrs_frameLayout"] = cmds.frameLayout(label="Numeric Attrs:", collapsable=False, w=200,
                                                                enable=True, p=attrOpt)
        cmds.rowColumnLayout(nc=2)
        cmds.text("Min:")
        self.widgets["minLine_text"] = cmds.textField(w=120, cc=partial(self.minMaxTextChange, "minLine_text"))
        cmds.text("Max:")
        self.widgets["maxLine_text"] = cmds.textField(cc=partial(self.minMaxTextChange, "maxLine_text"))
        cmds.text("Default:    ")
        self.widgets["defaultLine_text"] = cmds.textField(tx="0", cc=partial(self.minMaxTextChange, "defaultLine_text"))

        # Enum options
        self.widgets["enumNames_frameLayout"] = cmds.frameLayout(label="Enum Names:", collapsable=False, w=200,
                                                                 enable=False, p=attrOpt)
        cmds.rowColumnLayout(nc=2)
        cmds.separator(visible=False, w=60)
        self.widgets["enumScroll"] = cmds.textScrollList(append=['On', 'Off', ''], allowMultiSelection=False, w=125,
                                                         sc=self.editScroll)

        # todo add right click to remove enum
        cmds.text("New name: ", w=60)
        self.widgets["enumTextFld"] = cmds.textField(w=125, cc=self.reNamer)

        # todo add option to connect it to something or something to it
        # todo add option to add something between the connection
        '''
        cmds.separator(w=400, h=7, p=self.widgets["attrMaker_mainLayout"])
        cmds.text("Step 3: Make a selection and Script it!", p=self.widgets["attrMaker_mainLayout"])

        scriptItButtons = cmds.rowColumnLayout(nc=2, adj=True, p=self.widgets["attrMaker_mainLayout"])
        cmds.columnLayout(adj=False)
        cmds.button(w=199, l="Script it!", c=partial(self.scriptIt, False))
        cmds.columnLayout(adj=True, p=scriptItButtons)
        cmds.button(w=199, l="add to script!", c=partial(self.scriptIt, True))
        cmds.separator(w=400, h=7, p=self.widgets["attrMaker_mainLayout"])
        # Data Type
        cmds.columnLayout(parent=self.widgets["attrMaker_mainLayout"], adj=True)
        self.widgets["dataType_frameLayout"] = cmds.frameLayout(label="Script:", collapsable=False, w=400)
        cmds.rowColumnLayout(adj=True)
        self.widgets["scriptField"] = cmds.scrollField(h=200)

        cmds.separator(w=400, h=7, p=self.widgets["attrMaker_mainLayout"])
        '''
        cmds.separator(h=7, p=self.widgets["attrMaker_mainLayout"])
        scriptItButtons = cmds.rowColumnLayout(nc=2, adj=True, p=self.widgets["attrMaker_mainLayout"])
        cmds.columnLayout(adj=False)
        cmds.button(w=199, l="Compile Script!", c=self.scriptIt)
        cmds.columnLayout(adj=True, p=scriptItButtons)
        # todo? self.widgets["signalButton"] = cmds.button(w=199, l="not compiled", bgc=[.5,.5,.5])
        cmds.separator(w=400, h=7, p=self.widgets["attrMaker_mainLayout"])

        self.widgets["feedbackTextField"] = cmds.textField(tx="Attr Maker", editable=False,
                                                           p=self.widgets["attrMaker_mainLayout"])
        self.defaultFeedback()

    @staticmethod
    def getScript(*args):
        if script:
            return script
        else:
            return False

    def scriptIt(self, *args):
        self.defaultFeedback()
        highGrp = cmds.checkBox(self.widgets["highGrp_checkBox"], query=True, v=True)
        script = ""
        # check name
        # todo make sure name is good for maya
        lineTx = cmds.textField(self.widgets["nameLine_text"], q=True, tx=True)
        if lineTx:
            script += 'attrName =  "%s"\n' % lineTx
            self.name = lineTx
        else:
            print("==> please name the attribute")
            self.errorFeedback("Please name the attribute")
            script = ""
            return

        #if highGrp:
        #    cmds.scrollField(self.widgets["scriptField"], e=True, it='highGrp = "high_grp"\n')
        # todo seperate the parts so adding the attr to an object or to high grp is one command
        '''
        self.getAttrInfo()
        self.create
        '''


        # list objects
        #if newText:
        selection = cmds.ls(sl=True)
        if len(selection) is 0:
            objTx = 'obj = "objectName"'
            self.loop[0] = ""
        elif len(selection) is 1:
            if highGrp:
                objTx = 'objList = ["%s", highGrp]' % selection[0]
                objTx += "]\nfor obj in objList:" # todo make sure this works
                self.loop[0] = "\t"
            else:
                objTx = 'obj = "%s"' % selection[0]
                self.loop[0] = ""
        else:
            if highGrp:
                self.errorFeedback('Cannot connect multiple attributes of the same name to "high_grp"')
                highGrp = False
            objTx = 'objList = ["%s"' % selection[0]
            for i in range(1, len(selection)):
                objTx += ', "%s"' % selection[i]
            self.loop[0] = "\t"
            objTx += "]\nfor obj in objList:"


        # check type
        attr = cmds.radioButtonGrp(self.widgets["attr_radio"], q=True, select=True)
        if attr is 2 or attr is 3:  # integer or float
            newTx = 'pm.addAttr(obj, ln=attrName, at='
            if attr is 2:
                newTx += '"long"'
            else:
                newTx += '"double"'
            if self.min:
                newTx += ", min=%s" % self.min
            if self.max:
                newTx += ", max=%s" % self.max
            newTx += ", dv=%s" % self.default
            newTx += ")\n"

        elif attr is 1:  # vector
            newTx = 'pm.addAttr(obj, ln=attrName, at="double3")\n' + \
                    self.loop[0] + 'for x in "XYZ":\n' + \
                    self.loop[0] + '\tpm.addAttr(obj, ln=attrName+x, p=attrName, at="double")\n' + \
                    self.loop[0] + 'pm.setAttr(obj+"."+attrName, keyable=True)\n' + \
                    self.loop[0] + 'for x in "XYZ":\n' + \
                    self.loop[0] + '\tpm.setAttr(obj+"."+attrName+x, keyable=True)\n'

        else:  # enum
            length = cmds.textScrollList(self.widgets["enumScroll"], query=True, numberOfItems=True)
            # set the shown list
            cmds.textScrollList(self.widgets["enumScroll"], edit=True, selectIndexedItem=1)
            enumVar = '"' + cmds.textScrollList(self.widgets["enumScroll"], query=True, selectItem=True)[0] + '"'
            for i in range(2, length):
                cmds.textScrollList(self.widgets["enumScroll"], edit=True, selectIndexedItem=i)
                temp = cmds.textScrollList(self.widgets["enumScroll"], query=True, selectItem=True)[0]
                enumVar += ', "%s"' % temp
            newTx = "enumVars = [%s]\n" % enumVar
            newTx += 'enumString = enumVars[0]\n' + \
                     'for i in range(1, len(enumVars)):\n' + \
                     '\tenumString += ":%s" %enumVars[i]\n'
            newTxEnum = 'pm.addAttr(obj, ln=attrName, at="enum", enumName=enumString)\n'

        setAttrTx = ""
        if attr is not 1:
            setAttrTx = self.loop[0] + 'pm.setAttr(obj+"."+ attrName, keyable=True)\n'
        if attr is 4:
            script += newTx + objTx + "\n" + self.loop[0] + newTxEnum + setAttrTx
        else:
            script += objTx + "\n" + self.loop[0] + newTx + setAttrTx

        if highGrp:
            script += "\n" + "pm.connectAttr(obj + '.' + attrName, highGrp + '.' + attrName)"
        # script += self.loop[0]+'pm.setAttr(obj+".'+self.name+'", keyable=True)\n'
        global script
        self.changeFeedback("Compiled!", "green")


    def reNamer(self, *args):
        item = cmds.textScrollList(self.widgets["enumScroll"], query=True, selectIndexedItem=True)[0]
        newText = cmds.textField(self.widgets["enumTextFld"], query=True, text=True)
        currentText = cmds.textScrollList(self.widgets["enumScroll"], query=True, selectItem=True)[0]

        cmds.textScrollList(self.widgets["enumScroll"], edit=True, appendPosition=[int(item), newText])
        cmds.textScrollList(self.widgets["enumScroll"], edit=True, removeIndexedItem=int(item) + 1)
        cmds.textScrollList(self.widgets["enumScroll"], edit=True, selectIndexedItem=int(item))
        if currentText == '':
            cmds.textScrollList(self.widgets["enumScroll"], edit=True, append='')

    def editScroll(self, *args):
        val = cmds.textScrollList(self.widgets["enumScroll"], query=True, selectItem=True)[0]
        cmds.textField(self.widgets["enumTextFld"], edit=True, text=val)

    def defaultFeedback(self):
        self.changeFeedback("Attr Maker")

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)

    def errorFeedback(self, message):
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=(.6, .3, .3), tx=message)

    def nameTextChange(self, *args):
        lineTx = cmds.textField(self.widgets["nameLine_text"], q=True, tx=True)
        # todo check if there's a number in the beginning or illegal characters
        self.name = lineTx

    def minMaxTextChange(self, line, *args):
        # todo check if int or float needed

        attr = cmds.radioButtonGrp(self.widgets["attr_radio"], q=True, select=True)
        type = int
        if attr is 3:
            type = float

        lineTx = cmds.textField(self.widgets[line], q=True, tx=True)
        var = self.isNumTextValid(lineTx, type)
        if line == "minLine_text":
            if var or var is 0:
                var = self.setMinCheck(type(var))
                self.min = var
            else:
                var = self.min
        elif line == "maxLine_text":
            if var or var is 0:
                var = self.setMaxCheck(type(var))
                self.max = var
            else:
                var = self.max
        else:  # defaultLine
            if var or var is 0:
                var = self.setDefaultCheck(type(var))
                self.default = var
            else:
                var = 0
        self.setLine(var, line)

    def setLine(self, var, line):
        cmds.textField(self.widgets[line], edit=True, tx=var)

    def setMinCheck(self, var):
        if var >= self.default:
            self.default = var
            self.setLine(var, "defaultLine_text")
        if (self.max or self.max is 0) and var > self.max:
            self.max = var
            self.setLine(var, "maxLine_text")
        return var

    def setMaxCheck(self, var):
        if var <= self.default:
            self.default = var
            self.setLine(var, "defaultLine_text")
        if (self.min or self.min is 0) and var < self.min:
            self.min = var
            self.setLine(var, "minLine_text")
        return var

    def setDefaultCheck(self, var):
        if (self.min or self.min is 0) and var <= self.min:
            self.min = var
            self.setLine(var, "minLine_text")
        if (self.max or self.max is 0) and var >= self.max:
            self.max = var
            self.setLine(var, "maxLine_text")
        return var

    def isNumTextValid(self, line, type):
        try:
            return type(line)
        except:
            temp = ""
            dot = False
            try:
                for i in line:
                    if not temp and i == "-":
                        temp += i
                    # for floats
                    elif type is float and i == ".":
                        temp += i
                        dot = True
                    elif type(i):
                        temp += i
                        dot = False
            except:
                if temp:
                    # for floats
                    if dot:
                        temp += "0"
                    return type(temp)
                else:
                    return ""

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
