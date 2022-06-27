from maya import cmds, mel
import pymel.core as pm

# this allows the order of selection
pm.selectPref(trackSelectionOrder=1)

class CrvFromSelection:

    def __init__(self, makeWin=True, parent1=''):

        self.selection = []
        self.widgets = {}
        self.crvFromSelWin(makeWin, parent1)

    def crvFromSelWin(self, makeWin, parent1):
        step2txt = ' Step 2. Give base name for the curve and locators \n' \
                   ' (If name is left empty, it will get the objects name) '
        if makeWin and not parent1:
            if cmds.window("crvFromSel_window", exists=True):
                cmds.deleteUI("crvFromSel_window")
            self.widgets["crvFromSel_window"] = cmds.window("crvFromSel_window", title="Curve From Selection Tool",
                                                            sizeable=1, rtf=True)
        mainLayout = cmds.rowColumnLayout('Sel to Crv', numberOfColumns=1, adj=True)
        if parent1:
            #step2txt = ' Step 2: '
            cmds.rowColumnLayout(mainLayout, e=True, p=parent1)
        cmds.separator(p=mainLayout, h=7)
        #cmds.text('Step 1. Make vertices selection')
        #cmds.separator(h=3)
        #cmds.text(step2txt)
        #cmds.separator(h=5, vis=False)
        self.widgets["cfs_Layout"] = cmds.rowColumnLayout(numberOfColumns=2, adj=True, adjustableColumn=2)
        cmds.text(' Curve setup prefix : ')
        self.widgets["cfs_text"] = cmds.textField(text="")
        cmds.separator(p=mainLayout, h=7)
        #cmds.text(' Step 3: ', p=mainLayout)
        cmds.separator(h=5, vis=False, p=mainLayout)
        cmds.button(l="Step 3: Create", c=self.crvFromSel, p=mainLayout, w=100)
        cmds.separator(h=5, vis=False, p=mainLayout)
        if makeWin:
            cmds.showWindow()

    def crvFromSel(self, *args):
        #op = cmds.radioButtonGrp(self.widgets["cfs_radio"], q=True, select=True)
        nameField = cmds.textField(self.widgets["cfs_text"], q=True, tx=True)

        vertsList = pm.ls(fl=True, os=True)  # os = orderedSelection
        points = []
        for obj in vertsList:
            try:  # in case it's a PyNode
                name = obj.name()
            except:
                name = obj
            if ".vtx[" in name:
                pos = pm.xform(obj, query=True, t=True, ws=True)
                points.append(pos)
            else:
                print " // skipping: \"%s\". is it a vertex?" % obj
        if nameField:
            name = nameField
        else:
            name = name.rpartition('.vtx[')[0]
            if 'Shape' in name:
                name = name.rpartition('Shape')[0]
        crv = pm.curve(p=points, degree=1, n=name + "_crv")
        grp = pm.group(em=True, w=True, n=crv.name() + '_locCtl_grp')
        locs = []
        for i in range(0, (len(points))):
            loc = pm.pointCurveConstraint(crv + '.ep[%s]' % i, ch=True)[0]
            loc = pm.PyNode(loc)
            loc.rename('locCtl_%s_%s' % (crv.name(), i))
            pm.parent(loc, grp)
            pm.select(loc)
            mel.eval('CenterPivot;')
            locs.append(loc)
        return locs

    def crvFromSelFix(self, *args): # todo this...?
        op = cmds.radioButtonGrp(self.widgets["cfs_radio"], q=True, select=True)
        grpText = cmds.textField(self.widgets["cfs_text"], q=True, tx=True)
        print op
        print grpText
        '''
        if op == 1 and grpText == "_grp":
            cmds.textField(self.widgets["cfs_text"], edit=True, tx="grp_")
        if op == 2 and grpText == "grp_":
            cmds.textField(self.widgets["cfs_text"], edit=True, tx="_grp")
        '''