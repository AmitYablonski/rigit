from maya import cmds, mel
import pymel.core as pm
from functools import partial
import UI_modules as uim
import RigItMethodsUI as rim
reload(uim)
reload(rim)

class multiUVConnect:
    def __init__(self, par='', scriptIt=False):
        self.widgets = {}
        self.feedbackName = 'Multi UV Set Connection tool'
        mainLay = self.winBase('MultiUVConnect', self.feedbackName, par)
        self.populateUI(mainLay, scriptIt)
        self.defaultFeedback()

    def execute(self, *args):
        maps = pm.polyUVSet(obj, q=True, auv=True)
        return

    def scriptIt(self, *args):
        script = ''
        rim.showScript(script)
        return

    def updateScrolls(self, scrollName, remove=False, clear=False, *args):
        scroll = self.widgets[scrollName + "Scroll"]
        if clear:
            cmds.textScrollList(scroll, e=True, removeAll=True)
            uim.resizeScroll(scroll)
            return
        if remove:
            #selItem = cmds.textScrollList(scroll, query=True, selectItem=True)
            selItem = cmds.textScrollList(scroll, query=True, selectIndexedItem=True)
            if not selItem:
                self.orangeFeedback('Nothing selected to remove')
                return
            selItem.reverse()
            for item in selItem:
                #cmds.textScrollList(scroll, e=True, removeItem=item)
                cmds.textScrollList(scroll, e=True, removeIndexedItem=item)
        else:
            sele = pm.selected()
            for sel in sele:
                cmds.textScrollList(scroll, edit=True, append='%s' % (sel.name()))
        # resize scroll
        uim.resizeScroll(scroll)
        # todo remove? self.renumberScroll(scroll)

    def addScrollSetup(self, scrollName, parLay):
        mainLay = pm.columnLayout(adj=True, p=parLay)

        pm.text('Objects to apply connection', p=mainLay)

        cmds.rowColumnLayout(nc=3, cs=[[2, 4], [3, 4]], adj=True, p=mainLay)
        cmds.button('add from\nselection', c=partial(self.updateScrolls, scrollName))
        cmds.button('remove\nfrom list', c=partial(self.updateScrolls, scrollName, True))
        cmds.button('clear\nlist', c=partial(self.updateScrolls, scrollName, clear=True))
        self.widgets[scrollName + "Scroll"] = cmds.textScrollList(allowMultiSelection=True, h=100, p=mainLay) # , w=w

    def populateUI(self, mainLay, scriptIt):
        pm.separator(h=7, p=mainLay)
        pm.text(l=self.feedbackName, font='boldLabelFont', p=mainLay)
        pm.separator(h=7, p=mainLay)
        pm.text(l='Select Material:', p=mainLay)
        self.widgets['exObj'] = uim.selectAndAddToField(self, mainLay, 'Select')

        self.addScrollSetup('AllObjs', mainLay)

        # todo find maps
        # todo find file nodes

        #self.widgets['allObj'] = uim.selectAndAddToField(self, mainLay, 'Select', multiple=True)

        # buttons
        cmds.rowColumnLayout(nc=2, cs=[2, 5], adj=True, p=mainLay)
        cmds.button(l='Execute', h=28, c=self.execute)
        if scriptIt:
            cmds.button(l='Script it', w=100, c=self.scriptIt)
        else:
            pm.separator(w=100, style='none')

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
                                        (mLay, 'right', 0), (mLay, 'bottom', 30)))

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

