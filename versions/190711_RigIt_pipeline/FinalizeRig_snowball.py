from maya import cmds, mel
import pymel.core as pm
import traceback
import mgear.maya.icon as ic


class FinalizeRig_snowball:

    def __init__(self):

        self.selection = []
        self.widgets = {}
        self.finalizeRigWin()

    def finalizeRigWin(self):
        if cmds.window("finalizeRig_window", exists=True):
            cmds.deleteUI("finalizeRig_window")
        self.widgets["finalizeRig_window"] = cmds.window("finalizeRig_window", title="Finalize Rig",
                                                         widthHeight=(250, 100), sizeable=1, rtf=True)

        form = pm.formLayout(numberOfDivisions=100)

        self.widgets['radio0'] = pm.radioButtonGrp(label='Create Cns: ', labelArray2=['All', 'Selected'], numberOfRadioButtons=2, sl=1,
                                   cal=[(1, "left"), (2, "left"), (3, "left")], cw3=(70, 40, 40))
        radio0 = self.widgets['radio0']
        btn0 = pm.button(label='Finalize', command=self.dofunc)

        cmds.formLayout(form, edit=True, attachForm=[(radio0, 'top', 10), (radio0, 'left', 10), (radio0, 'right', 5),
                                                     (btn0, 'left', 10), (btn0, 'right', 10)],
                        attachControl=(btn0, 'top', 10, radio0))

        cmds.showWindow()

    def create_cns(self):
        ctls = pm.ls('*_ctl')

        gloabl = pm.PyNode('global_C0_ctl')

        try:
            pm.addAttr(gloabl, ln="ShowCnsCtrls", at="double", dv=0, min=0, max=1)
            pm.setAttr((gloabl + ".ShowCnsCtrls"), e=1, keyable=False, cb=1)
            pm.setAttr((gloabl + ".ShowCnsCtrls"), 0)
        except:
            print traceback.print_exc()
            print '{} has cns show attribute'.format(gloabl.name())

        for c in ctls:
            oParent = c.getParent()
            if not pm.objExists(c.name() + "_cns"):
                icon = ic.create(oParent, c.name() + "_cns", c.getMatrix(), [1, 0, 0], 'cross')
                icon.setTransformation(c.getMatrix())
                pm.parent(c, icon)
                iconShape = icon.getShape()
                pm.connectAttr(gloabl.ShowCnsCtrls, iconShape.visibility)

                print '[add cns controller] proccessed: {}'.format(c.name())
            else:
                print '[add cns controller] already exists: {}'.format(c.name())

    def create_cns_selected(self):
        excList = pm.ls(sl=True)
        ctls = pm.ls('*_ctl')

        gloabl = pm.PyNode('global_C0_ctl')

        try:
            pm.addAttr(gloabl, ln="ShowCnsCtrls", at="double", dv=0, min=0, max=1)
            pm.setAttr((gloabl + ".ShowCnsCtrls"), e=1, keyable=False, cb=1)
            pm.setAttr((gloabl + ".ShowCnsCtrls"), 0)
        except:
            print traceback.print_exc()
            print '{} has cns show attribute'.format(gloabl.name())

        for c in ctls:
            if c in excList:
                oParent = c.getParent()
                if not pm.objExists(c.name() + "_cns"):
                    icon = ic.create(oParent, c.name() + "_cns", c.getMatrix(), [1, 0, 0], 'cross')
                    icon.setTransformation(c.getMatrix())
                    pm.parent(c, icon)
                    iconShape = icon.getShape()
                    pm.connectAttr(gloabl.ShowCnsCtrls, iconShape.visibility)

                    print '[add cns controller] proccessed: {}'.format(c.name())
                else:
                    print '[add cns controller] already exists: {}'.format(c.name())
    # finelaize rig

    def override_ref_on(self, item):
        pm.setAttr(item + ".overrideEnabled", 1)
        pm.setAttr(item + ".overrideDisplayType", 2)

    def finalize_rig(self):
        try:
            pm.setAttr("rig.jnt_vis", 0)
        except:
            print "rig.jnt_vis failed"

        pm.parent("rig", "main")
        hg = "high_grp"
        hg_items = pm.listRelatives(hg, c=1)
        for item in hg_items:
            self.override_ref_on(item)
            pm.select(item)
            mel.eval(
                'displaySmoothness -divisionsU 0 -divisionsV 0 -pointsWire 4 -pointsShaded 1 -polygonObject 1;')
            pm.select(cl=1)

    def dofunc(self, *args):
        radio_input = pm.radioButtonGrp(self.widgets['radio0'], q=1, select=1)
        if radio_input == 1:
            self.create_cns()
        else:
            self.create_cns_selected()
        self.finalize_rig()
