from maya import cmds, mel
import pymel.core as pm
from functools import partial
import SnowRigMethodsUI as srm


class ColorIt:
    def __init__(self, parent):

        self.widgets = {}
        self.colorCount = 0
        self.colorIt(parent)
        self.faces = ''
        global script

    def colorIt(self, parent='None'):
        if parent == 'None':
            return ("Can't load ColorIt")
        self.widgets["colorIt_mainLayout"] = cmds.columnLayout("Color It", p=parent, adj=True)

        cmds.separator(h=7)
        cmds.text("The object should receive:", al='left')
        self.widgets["color_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=2, select=1,
                                                          labelArray2=['Single Color', 'Multiple Colors'],
                                                          onc=self.colorEditorRadio)
        cmds.separator(h=7)
        cmds.text("Color Type:", al='left')
        self.widgets["colorType_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=3, select=1,
                                                              labelArray3=['lambert', 'blinn', 'surfaceShader'])
        cmds.separator(h=7)
        # TODO - add option to add texture
        # single color layout
        scroller = cmds.scrollLayout(p=self.widgets["colorIt_mainLayout"], h=350, childResizable=True)
        self.widgets["singleColorLayout"] = cmds.rowColumnLayout(nc=1, adj=True, p=scroller)

        cmds.text("Object/s to assign the color to: ", al='left')
        self.widgets["objects_Layout"] = cmds.rowColumnLayout(nc=2, cs=[2, 5], adjustableColumn=2, columnWidth=[1, 100],
                                                              p=self.widgets["singleColorLayout"])
        self.widgets["objects_button"] = cmds.button(l='Select object/s', w=20,
                                                     c=lambda *_: self.updateTextField('objects_text'))
        self.widgets['objects_text'] = cmds.textField(w=300)
        cmds.separator(h=7, p=self.widgets["colorIt_mainLayout"])
        # color name and picker
        self.widgets["colorName_rowLayout"] = cmds.rowLayout(nc=2, adjustableColumn=2, columnWidth=[1, 103],
                                                             p=self.widgets["singleColorLayout"])
        cmds.text("  Color Name:")
        self.widgets["color_name"] = cmds.textField(tx="")
        cmds.text('** if no name assigned, it will recieve objects name + suffix.\n\texample: "shoes_lambert" **',
                  al='left', p=self.widgets["singleColorLayout"])
        self.widgets["singleColorInput"] = cmds.colorInputWidgetGrp(label='Color : ', rgb=(1, 0, 0), p=self.widgets["singleColorLayout"])

        # multiple colors layout
        self.widgets["multiColorLayout"] = cmds.rowColumnLayout(nc=1, adj=True, p=scroller)
        self.multiColorAdd(self.widgets["multiColorLayout"])
        # todo make it possible to add more and count it
        # cmds.separator(h=7, p=self.widgets["colorIt_mainLayout"])
        cmds.button("add another color", c=partial(self.multiColorAdd, self.widgets["multiColorLayout"]),
                    p=self.widgets["colorIt_mainLayout"])

        cmds.separator(h=7, p=self.widgets["colorIt_mainLayout"])
        scriptItButtons = cmds.rowColumnLayout(nc=2, adj=True, p=self.widgets["colorIt_mainLayout"])
        cmds.columnLayout(adj=False)
        cmds.button(w=199, l="Compile Script!", c=self.scriptIt)
        cmds.columnLayout(adj=True, p=scriptItButtons)
        # todo? self.widgets["signalButton"] = cmds.button(w=199, l="not compiled", bgc=[.5,.5,.5])
        cmds.separator(w=400, h=7, p=self.widgets["colorIt_mainLayout"])

        self.widgets["feedbackTextField"] = cmds.textField(tx="", editable=False,
                                                           p=self.widgets["colorIt_mainLayout"])
        self.defaultFeedback()
        self.colorEditorRadio()  # this sets the multiColor correctly

    @staticmethod
    def getScript(*args):
        if script:
            return script
        else:
            return False

    def scriptIt(self, *args):  # todo - All of this
        self.defaultFeedback()
        mult = cmds.radioButtonGrp(self.widgets["color_radio"], q=True, select=True)

        # define shader
        shaders = ['None', 'lambert', 'blinn', 'surfaceShader']
        colorRadio = cmds.radioButtonGrp(self.widgets["colorType_radio"], q=True, select=True)
        shader = shaders[colorRadio]

        # start of script creation (excluding import)
        script = ''
        if mult is 1:  # single color
            scriptS = self.singleColorScript(shader)
            if scriptS == "ERROR":
                return
            else:
                script += scriptS
        else:  # MULTI COLOR
            script += self.multipleColorScript(shader)
        global script
        self.changeFeedback("Compiled!", "green")

    def singleColorScript(self, shader):  # todo this
        self.changeFeedback("Single color creation process")
        scriptS = ''
        # checkups
        objName = cmds.textField(self.widgets["objects_text"], q=True, tx=True)
        colorName = cmds.textField(self.widgets["color_name"], q=True, tx=True)
        colorIn = cmds.colorInputWidgetGrp(self.widgets["singleColorInput"], q=True, rgb=True)
        if not objName:
            self.changeFeedback("No Object/s to assign color/s to", "red")
            return "ERROR"
        else:  # start of script creation
            scriptS += 'obj = pm.PyNode("%s")\n' % objName
        if colorName:
            scriptS += 'shader = pm.shadingNode("%s", asShader=True, n="%s")\n' % (shader, colorName)
        else:
            scriptS += 'shader = pm.shadingNode("%s", asShader=True, n=obj + "_%s")\n' % (shader, shader)  #obj.name()
        #scriptS += 'shader.setAttr("c", [%0.3f, %0.3f, %0.3f])\n' % (colorIn[0], colorIn[1], colorIn[2])
        scriptS += 'shader.attr("color").set([%0.3f, %0.3f, %0.3f])\n' % (colorIn[0], colorIn[1], colorIn[2])
        scriptS += 'pm.select(obj)\n' \
                   'pm.hyperShade(assign=shader)\n\n'
        return scriptS

    def multipleColorScript(self, shader):  # todo this
        self.changeFeedback("Multiple color creation process")
        count = self.colorCount
        scriptM = self.assosDef()
        for num in range(0, count):
            faceAssos = cmds.textField(self.widgets["face_assos_%s" % num], q=True, tx=True)
            colorName = cmds.textField(self.widgets["color_name%s" % num], q=True, tx=True)
            colorIn = cmds.colorInputWidgetGrp(self.widgets["multColorInput%s" % num], q=True, rgb=True)
            scriptM += 'faceAssos%s = %s\n' % (num, faceAssos)
            scriptM += 'shader = pm.shadingNode("%s", asShader=True, n="%s")\n' % (shader, colorName)
            #scriptM += 'shader.setAttr("color", [%0.3f, %0.3f, %0.3f])\n' % (colorIn[0], colorIn[1], colorIn[2])
            scriptM += 'shader.attr("color").set([%0.3f, %0.3f, %0.3f])\n' % (colorIn[0], colorIn[1], colorIn[2])
            scriptM += 'assosiateColor(faceAssos%s , shader)\n\n' % num
        return scriptM

    def assosDef(self):
        '''
        # original def taken from bsp script it
        aScript = 'def assosiateColor(selection, shader):\n\t' \
                  'pm.select(shader)\n\t' \
                  'shader_name = cmds.ls(sl=True)[0]\n\t' \
                  'shader_sg = pm.sets(renderable=True, noSurfaceShader=True, empty=True, ' \
                  'name="{}SG".format(shader_name))\n\t' \
                  'shader.outColor.connect(shader_sg.surfaceShader)\n\t' \
                  'for sel in selection:\n\t\t' \
                  'pm.select(sel, tgl=True)\n\t' \
                  'cmds.sets(e=True, forceElement=shader_sg.name())\n\n'
        '''
        aScript = 'def assosiateColor(selection, shader):\n\t' \
                  'pm.select(shader)\n\t' \
                  'shader_sg = pm.sets(renderable=True, noSurfaceShader=True, empty=True, ' \
                  'name="%sSG" % shader.name())\n\t' \
                  'shader.outColor.connect(shader_sg.surfaceShader)\n\t' \
                  'for sel in selection:\n\t\t' \
                  'pm.select(sel, tgl=True)\n\t' \
                  'cmds.sets(e=True, forceElement=shader_sg.name())\n\n'
        return aScript

    def updateTextField(self, field, *args):
        self.defaultFeedback()
        op = cmds.radioButtonGrp(self.widgets["color_radio"], q=True, select=True)
        selection = cmds.ls(sl=True)
        if len(selection) > 0:
            if len(selection) == 1:
                sel = selection[0]
            else:
                sel = '["%s"' % selection[0]
                for i in range(1, len(selection)):
                    sel += ', "%s"' % selection[i]
                sel += "]"
            cmds.textField(self.widgets[field], e=True, tx=sel)
            return
        self.changeFeedback('Please make a selection', 'red')

    def colorEditorRadio(self, *args):
        self.defaultFeedback()
        op = cmds.radioButtonGrp(self.widgets["color_radio"], q=True, select=True)
        if op is 2:  # multi color
            cmds.rowColumnLayout(self.widgets["singleColorLayout"], e=True, manage=False)
            cmds.rowColumnLayout(self.widgets["multiColorLayout"], e=True, manage=True)
        else:  # single color
            cmds.rowColumnLayout(self.widgets["singleColorLayout"], e=True, manage=True)
            cmds.rowColumnLayout(self.widgets["multiColorLayout"], e=True, manage=False)

    def updateFaceAssos(self, num, add, *args):
        self.defaultFeedback()
        selection = pm.ls(sl=True)
        if len(selection) == 0:
            self.changeFeedback("Please make a selection and try again", "red")
            return
        if ".f[" not in selection[0].name():  # todo check nodeType? (it returns "mesh" for face/edge/vert)
            self.changeFeedback("Invalid selection. Please select polygon faces.", "red")
            return
        if add:
            # facesTx = cmds.textField(self.widgets["face_assos_%s" % num], q=True, tx=True)
            if self.faces:
                pm.select(self.faces)
                pm.select(selection, add=True)
                selection = pm.ls(sl=True)
        scripted = "['%s' " % selection[0]
        for i in range(1, len(selection)):
            scripted += ", '%s'" % selection[i]
        scripted += "]"
        cmds.textField(self.widgets["face_assos_%s" % num], e=True, tx=scripted)
        self.faces = selection
        self.changeFeedback("Selected faces are %s" % selection)

    def multiColorAdd(self, parent, *args):
        num = self.colorCount
        self.widgets["multiColorLayout%s" % num] = cmds.rowColumnLayout(nc=1, adj=True, p=parent)
        cmds.text("Color %s:" % num, al="left")
        # name
        cmds.rowColumnLayout(nc=2, adj=True, adjustableColumn=2)
        cmds.text("colorText%s" % num, l="Name : ")
        self.widgets["color_name%s" % num] = cmds.textField(tx="", w=170)
        # face selection
        cmds.rowColumnLayout(nc=2, columnSpacing=[[2, 3]],  #, [3, 3]], adj=True, adjustableColumn=3
                             p=self.widgets["multiColorLayout%s" % num])
        cmds.button("Update Selected Faces ", c=partial(self.updateFaceAssos, num, False))
        cmds.button("  Add Selected   ", c=partial(self.updateFaceAssos, num, True))
        cmds.rowColumnLayout(nc=2, columnSpacing=[[2, 3]], adj=True, adjustableColumn=2,
                             p=self.widgets["multiColorLayout%s" % num])
        cmds.text("Faces: ")
        self.widgets["face_assos_%s" % num] = cmds.textField(tx="")
        # name and picker
        colorLayout = cmds.rowColumnLayout(nc=1, adj=True, p=self.widgets["multiColorLayout%s" % num])
        self.widgets["multColorInput%s" % num] = cmds.colorInputWidgetGrp(label='Color %s: ' % num, rgb=(1, 0, 0), p=colorLayout)
        cmds.separator(h=7, p=parent)
        self.colorCount += 1

    def defaultFeedback(self):
        self.changeFeedback("Assign Colors Script Editor")

    def changeFeedback(self, messege, error=''):
        bg = (.25, .25, .25)
        if error == "red":
            bg = (.6, .3, .3)
        if error == "green":
            bg = (.3, .6, .3)
        cmds.textField(self.widgets["feedbackTextField"], e=True, bgc=bg, tx=messege)
