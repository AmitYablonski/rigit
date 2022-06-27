from maya import cmds, mel
import pymel.core as pm
from functools import partial
import UI_modules as uim
import RigItMethodsUI as rim
import generalMayaTools as gmt


class MaterialCopier:
    def __init__(self, par='', scriptIt=False):
        self.widgets = {}
        self.feedbackName = 'Material Copier'

        # todo setup basic layout

        # todo copy mtl by world space for geometry with different vert order

        topLay, mainLay = self.winBase('MaterialCopier', self.feedbackName, par)
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def execute(self, *args):
        self.defaultFeedback()
        return

    def executeSelection(self, *args):
        self.defaultFeedback()

        sel_list = pm.ls(sl=True)
        source = sel_list[0]
        targets = []
        for i in range(1, len(sel_list)):
            targets.append(sel_list[i])
        errors = False
        pm.select(source)
        # todo make it not a hypershade command?
        pm.hyperShade(shaderNetworksSelectMaterialNodes=True)
        mtl_list = pm.selected(materials=True)
        if len(mtl_list) == 1:
            pm.select(targets)
            pm.hyperShade(assign=mtl_list[0])
        else:
            self.printFeedback('Copying multiple materials', mark_as_error=False)
            for target in targets:
                is_identical = gmt.is_obj_identical(source, target)
                if is_identical:
                    for mtl in mtl_list:
                        pm.hyperShade(objects=mtl)
                        face_sel = pm.ls(sl=True)
                        pm.select(face_sel[0].replace(source.name(), target.name()))
                        pm.hyperShade(a=mtl)
                else:
                    source_faces = gmt.get_face_center_pos(source)
                    target_faces = gmt.get_face_center_pos(target)
                    closest_assos = {}
                    for face_num in target_faces:
                        current_face_pos = target_faces[face_num]  # center position
                        current_face = '%s.f[%s]' % (target, face_num)
                        closest_face = 0
                        closest_assos[face_num] = 0
                        closest_dist = gmt.get_distance(current_face_pos, source_faces[0])
                        for i in range(0, len(source_faces)):
                            temp = gmt.get_distance(current_face_pos, source_faces[i])
                            if temp < closest_dist:
                                closest_face = i
                                closest_dist = temp
                                closest_assos[face_num] = i
                        face = '%s.f[%s]' % (source, closest_face)
                        pm.select(face)
                        pm.hyperShade(shaderNetworksSelectMaterialNodes=True)
                        shader = pm.ls(sl=True)
                        if not shader:
                            shader = 'lambert1'
                            self.printFeedback('Error finding a shader on %s, assigning lambert1 instead' % face)
                            errors = True
                        else:
                            shader = shader[0]
                        pm.select(current_face)
                        pm.hyperShade(assign=shader)
        pm.selectMode(object=True)
        pm.select(sel_list)

        if errors:
            self.printFeedback('Errors during process - check script editor')
        else:
            self.greenFeedback('Done')

    def scriptIt(self, *args):  # todo script it
        self.orangeFeedback('Script isn\'t done yet')
        script = ''
        rim.showScript(script)
        return

    def populateUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)
        pm.button(l='transfer for selection', c=self.executeSelection, p=mainLay)
        pm.separator(h=7, p=mainLay)
        # self.widgets['objField'] = uim.selectAndAddToField(self, mainLay, 'Select', 'transform')
        # self.widgets['attrField'] = uim.textAndField(mainLay, 'Text example: ', 'new string')

        # buttons
        cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay, enable=False)
        cmds.button(l='Execute', h=28, c=self.execute)
        if scriptIt:
            cmds.button(l='Script it', w=100, c=self.scriptIt)
        else:
            pm.separator(w=100, style='none')

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

    def printFeedback(self, text, color='', mark_as_error=True):
        error = ' // %s : %s' % (self.feedbackName, text)
        print(error)
        fColor = 'red'
        if color:
            fColor = color
        if mark_as_error:
            self.changeFeedback(error, fColor)
        else:
            self.changeFeedback(error)

    def defaultFeedback(self):
        self.changeFeedback('// %s' % self.feedbackName)

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.7, .3, .3)
            bg = [1, .4, .4]
        if error == "green":
            bg = (.3, .6, .3)
        if error == 'orange':
            bg = (.6, .4, .2)
        cmds.textField(self.widgets["feedback"], e=True, bgc=bg, tx=messege)
