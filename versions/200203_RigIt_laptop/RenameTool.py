from maya import cmds, mel
import pymel.core as pm
import generalMayaTools as gmt
from functools import partial


class RenameTool:

    def __init__(self):

        self.selection = []
        self.widgets = {}
        self.renameToolWin()

    def renameToolWin(self):
        if cmds.window("renameTool_window", exists=True):
            cmds.deleteUI("renameTool_window")
        self.widgets["renameTool_window"] = cmds.window("renameTool_window", title="Renamer Tool", sizeable=1,
                                                        rtf=True)  # w=SnowRigUI.buttonW3*6+10)
        self.widgets["menuBarLayout"] = cmds.menuBarLayout()
        cmds.menu(label='presets', p=self.widgets["menuBarLayout"])
        cmds.menuItem(divider=True, l="Default")
        cmds.menuItem(label='Reset', c=self.resetMenu)
        cmds.menuItem(divider=True, l="Other")
        cmds.menuItem(label='Remove "1" from suffix', c=self.removeOneSuffix)
        cmds.menuItem(label='Add "_ghost" suffix', c=self.makeGhostCtls)
        cmds.menu(label='extras', p=self.widgets["menuBarLayout"])
        cmds.menuItem(divider=True, l="Rename selection...")
        cmds.menuItem(label='to Upper case', c=partial(self.caseUpdater, True))
        cmds.menuItem(label='to Lower case', c=partial(self.caseUpdater, False))
        cmds.menuItem(label='to Camel case', c=self.camelCase)

        # tabs
        self.widgets["tabLayout"] = cmds.tabLayout(childResizable=True)
        # widgets["settingsMenuBar"] = cmds.menuBarLayout()
        self.widgets["renameTool_mainLayout"] = cmds.columnLayout('Renamer Options', p=self.widgets["tabLayout"])
        cmds.separator(h=7, w=300)
        cmds.text("Select renaming operation", al='center', w=200)
        cmds.separator(h=7, w=300)
        self.widgets["operation_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=4, cw4=[75, 75, 75, 75], select=2,
                                                              labelArray4=['Add', 'Replace', 'Remove', 'Rename'],
                                                              onc=self.renameChange)

        cmds.separator(h=7, w=300)
        self.widgets["method"] = cmds.text("Select renaming method", al='center', w=200)
        self.widgets["padding"] = cmds.text("Select padding if desired", al='center', w=200, visible=False)
        cmds.separator(h=7, w=300)
        self.widgets["padding_field"] = cmds.intSliderGrp(field=True, label='Padding', minValue=1, maxValue=10,
                                                          fieldMinValue=1, fieldMaxValue=30, w=300, columnWidth=[1, 50],
                                                          visible=False, h=19)
        self.widgets["part_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=3, cw3=[100, 100, 100], select=1,
                                                         labelArray3=['In Name', 'Prefix', 'Suffix'], h=19)

        cmds.separator(h=7, w=300, p=self.widgets["renameTool_mainLayout"])
        self.widgets['line1_text'] = cmds.textField(w=300)
        self.widgets["padding_chkBox"] = cmds.checkBox(label="Pad parent with lower value",
                                                       value=True, visible=False)
        self.widgets['line2_text'] = cmds.textField(w=300)
        cmds.separator(h=7, w=300, p=self.widgets["renameTool_mainLayout"])
        self.widgets["hierarchy_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=2, cw2=[120, 120], select=1,
                                                              labelArray2=['Hierarchy', 'Selected'],
                                                              p=self.widgets["renameTool_mainLayout"])
        cmds.separator(h=7, w=300, p=self.widgets["renameTool_mainLayout"])
        cmds.rowColumnLayout(nc=2, p=self.widgets["renameTool_mainLayout"])
        self.widgets['flipSel'] = cmds.checkBox(l='Flip selection\norder', w=115)
        cmds.button(l='Execute', w=160, h=50, c=self.executer)

        # upper\lower case layout
        self.widgets["extras_mainLayout"] = cmds.rowColumnLayout('Renamer Extras', numberOfColumns=1,
                                                                 p=self.widgets["tabLayout"])
        exMainLayout = self.widgets["extras_mainLayout"]
        cmds.separator(h=5, w=300, bgc=[.2, .2, .2])
        exLaySplit = cmds.rowColumnLayout(nc=1, p=exMainLayout)
        w = 81 * 1.5
        exLeftLay = cmds.rowColumnLayout(nc=1, p=exLaySplit)  # , w=w*2)
        pm.text('Rename Pre/Suffix by\namount of characters at end of string:')  # , al='left')
        cmds.separator(h=3)
        self.widgets["exOp_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=2, select=1, cw2=[w, w],
                                                         labelArray2=['Remove', 'Replace'], cc=self.exRadioUpdate)
        cmds.separator(h=3)
        self.widgets["exPart_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=2, select=2, cw2=[w, w],
                                                           labelArray2=['Prefix', 'Suffix'])
        cmds.separator(h=7)
        self.widgets["exAmt_field"] = cmds.intSliderGrp(field=True, label='amount', minValue=0, maxValue=5,
                                                        fieldMinValue=0, fieldMaxValue=99, columnWidth=[1, 50])
        cmds.separator(h=7)
        self.widgets['exLine_text'] = cmds.textField(w=300)
        cmds.separator(h=7)
        pm.button(l='execute', c=self.exPreSuffixEdit)
        cmds.separator(h=5, w=300, p=self.widgets["extras_mainLayout"], bgc=[.2, .2, .2])
        cmds.separator(h=7, w=300, p=self.widgets["extras_mainLayout"])
        self.widgets["case_Layout"] = cmds.rowColumnLayout(numberOfColumns=3, cs=[[1, 2], [2, 4], [3, 4]],
                                                           p=self.widgets["extras_mainLayout"])
        butW = 97
        cmds.button(l='Selection\nTo Upper Case', w=butW, h=40, c=partial(self.caseUpdater, True))
        cmds.button(l='Selection\nTo Lower Case', w=butW, c=partial(self.caseUpdater, False))
        cmds.button(l='Selection\nTo Camel Case', w=butW, c=partial(self.camelCase, False))
        cmds.separator(h=7, w=300, p=self.widgets["extras_mainLayout"])
        cmds.separator(h=5, w=300, p=self.widgets["extras_mainLayout"], bgc=[.2, .2, .2])

        cmds.showWindow()
        self.exRadioUpdate()

    def renameChange(self, *args):
        op = cmds.radioButtonGrp(self.widgets["operation_radio"], q=True, select=True)
        method = cmds.radioButtonGrp(self.widgets["part_radio"], q=True, select=True)
        # enable/disable text line
        if op == 2:
            cmds.textField(self.widgets["line1_text"], e=True, enable=True)
        else:
            cmds.textField(self.widgets["line1_text"], e=True, enable=False)
        # enable/disable radio button (prefix, suffix etc..)
        if op == 1:
            if method == 1:
                cmds.radioButtonGrp(self.widgets["part_radio"], e=True, select=2)
            cmds.radioButtonGrp(self.widgets["part_radio"], e=True, enable1=False)
        else:
            cmds.radioButtonGrp(self.widgets["part_radio"], e=True, enable1=True)
        # set rename mode
        if op == 4:
            cmds.text(self.widgets["method"], e=True, visible=False)
            cmds.text(self.widgets["padding"], e=True, visible=True)
            cmds.intSliderGrp(self.widgets["padding_field"], edit=True, visible=True)
            cmds.textField(self.widgets['line1_text'], e=True, visible=False)
            cmds.checkBox(self.widgets["padding_chkBox"], e=True, visible=True)
            cmds.radioButtonGrp(self.widgets["part_radio"], e=True, enable=False, visible=False)
        else:
            cmds.text(self.widgets["method"], e=True, visible=True)
            cmds.text(self.widgets["padding"], e=True, visible=False)
            cmds.intSliderGrp(self.widgets["padding_field"], edit=True, visible=False)
            cmds.textField(self.widgets['line1_text'], e=True, visible=True)
            cmds.checkBox(self.widgets["padding_chkBox"], e=True, visible=False)
            cmds.radioButtonGrp(self.widgets["part_radio"], e=True, enable=True, visible=True)

    def exRadioUpdate(self, *args):
        op = cmds.radioButtonGrp(self.widgets["exOp_radio"], q=True, select=True)
        if op == 1:
            cmds.textField(self.widgets["exLine_text"], e=True, enable=False)
        else:
            cmds.textField(self.widgets['exLine_text'], e=True, enable=True)

    def exPreSuffixEdit(self, *args):
        op = cmds.radioButtonGrp(self.widgets["exOp_radio"], q=True, select=True)
        method = cmds.radioButtonGrp(self.widgets["exPart_radio"], q=True, select=True)
        amt = pm.intSliderGrp(self.widgets["exAmt_field"], q=True, value=True)
        line = cmds.textField(self.widgets["exLine_text"], q=True, tx=True)
        sele = pm.selected()
        for obj in sele:
            name = obj.name()
            if method == 1:  # prefix
                name = name[amt:]
                if op == 2:
                    name = line + name
            else:  # suffix
                name = name[:-amt]
                if op == 2:
                    name = name + line
            print name
            self.renameObj(obj, name)

    def executer(self, *args):
        selection = pm.ls(sl=True)
        op = cmds.radioButtonGrp(self.widgets["operation_radio"], q=True, select=True)
        method = cmds.radioButtonGrp(self.widgets["part_radio"], q=True, select=True)
        hierarchy = cmds.radioButtonGrp(self.widgets["hierarchy_radio"], q=True, select=True)
        flip = cmds.checkBox(self.widgets['flipSel'], q=True, v=True)

        line1 = cmds.textField(self.widgets["line1_text"], q=True, tx=True)
        line2 = cmds.textField(self.widgets["line2_text"], q=True, tx=True)
        if not line2 or (op == 2 and not line1):
            print("missing variables for renaming")
            return
        if hierarchy == 1:
            selection = gmt.updateToHierarchy(selection)
        if flip:
            temp = []
            for sel in reversed(selection):
                temp.append(sel)
            selection = temp
        if op == 1:  # add
            self.addMethod(selection, method, line2)
        elif op == 2:  # "replace"
            self.replaceMethod(selection, method, line1, line2)
        elif op == 3:  # remove
            self.removeMethod(selection, method, line2)
        if op == 4:  # rename
            self.renameMethod(selection, line2)

    def removeOneSuffix(self, *args):
        cmds.radioButtonGrp(self.widgets["operation_radio"], e=True, select=3)
        cmds.radioButtonGrp(self.widgets["part_radio"], e=True, select=3)
        self.renameChange()
        cmds.textField(self.widgets['line2_text'], e=True, tx="1")

    def makeGhostCtls(self, *args):
        cmds.radioButtonGrp(self.widgets["operation_radio"], e=True, select=1)
        cmds.radioButtonGrp(self.widgets["part_radio"], e=True, select=3)
        self.renameChange()
        cmds.textField(self.widgets['line2_text'], e=True, tx="_ghost")

    def resetMenu(self, *args):
        cmds.radioButtonGrp(self.widgets["operation_radio"], e=True, select=2)
        cmds.radioButtonGrp(self.widgets["part_radio"], e=True, select=1)
        cmds.radioButtonGrp(self.widgets["hierarchy_radio"], e=True, select=1)
        self.renameChange()
        cmds.textField(self.widgets['line1_text'], e=True, tx="")
        cmds.textField(self.widgets['line2_text'], e=True, tx="")
        cmds.checkBox(self.widgets['flipSel'], e=True, v=False)

    def renameObj(self, obj, name):
        obj.rename(name)
        shps = obj.listRelatives(s=True)
        if shps:
            for shp in shps:
                shp.rename(name + 'Shape')

    def addMethod(self, selection, method, line2, *args):
        '''
        if method == 1:  # "entireName"
            for sel in selection:
                self.renameObj(sel, line2)
        '''
        for sel in selection:
            newName = sel.name()
            if '|' in newName:
                newName = newName.rpartition('|')[2]
            if method == 2:  # "prefix"
                newName = line2 + newName
            elif method == 3:  # "suffix"
                newName = newName + line2
            self.renameObj(sel, newName)

    def replaceMethod(self, selection, method, line1, line2, *args):
        if method == 1:  # "entireName"
            for sel in selection:
                parts = sel.partition(line1)
                name = parts[0]
                while (parts[1] == line1):
                    name += line2
                    parts = parts[2].partition(line1)
                    name += parts[0]
                temp = parts[2]
                self.renameObj(sel, name + temp)
        elif method == 2:  # "prefix"
            for sel in selection:
                name = sel.partition(line1)
                if name[0] == "" and name[1] == line1:
                    self.renameObj(sel, line2 + name[2])
                else:
                    print("couldn't find \"%s\" prefix in %s" % (line1, sel))
        elif method == 3:  # "suffix"
            for sel in selection:
                name = sel.rpartition(line1)
                if name[2] == "" and name[1] == line1:
                    self.renameObj(sel, name[0] + line2)
                else:
                    print("couldn't find \"%s\" suffix in %s" % (line1, sel))

    def removeMethod(self, selection, method, line2, *args):
        if method == 1:  # "entireName"
            for sel in selection:
                parts = sel.partition(line2)
                while (parts[1] == line2):
                    name = parts[0] + parts[2]
                    self.renameObj(sel, name)
                    parts = name.partition(line2)
        elif method == 2:  # "prefix"
            for sel in selection:
                name = sel.partition(line2)
                if name[0] == "" and name[1] == line2:
                    self.renameObj(sel, name[2])
                else:
                    print("couldn't find \"%s\" prefix in %s" % (line2, sel))
        elif method == 3:  # "suffix"
            for sel in selection:
                name = sel.rpartition(line2)
                if name[2] == "" and name[1] == line2:
                    self.renameObj(sel, name[0])
                else:
                    print("couldn't find \"%s\" suffix in %s" % (line2, sel))

    def renameMethod(self, selection, line2, *args):
        padding = pm.intSliderGrp(self.widgets["padding_field"], q=True, value=True)
        reverse = cmds.checkBox(self.widgets["padding_chkBox"], q=True, value=True)
        if reverse:
            selection = reversed(selection)
        if padding:
            i = 1
            for sel in selection:
                self.renameObj(sel, line2 + "_" + str(format(i, '0' + str(padding))))
                i += 1
        else:
            for sel in selection:
                self.renameObj(sel, line2)

    def caseUpdater(self, high, *args):
        selection = pm.selected()
        for sel in selection:
            if high:
                self.renameObj(sel, sel.name().upper())
            else:
                self.renameObj(sel, sel.name().lower())

    def camelCase(self, *args):
        sel_list = pm.ls(sl=True)
        for sel in sel_list:
            gmt.camelCase(sel.name())
