from maya import cmds, mel
import pymel.core as pm
import mgear.maya.icon as ic
import traceback


class CnsTool:

    def __init__(self):

        self.selection = []
        self.widgets = {}
        self.cnsToolWin()

    def cnsToolWin(self):
        if cmds.window("cnsTool_window", exists=True):
            cmds.deleteUI("cnsTool_window")
        self.widgets["cnsTool_window"] = cmds.window("cnsTool_window", title="Cns It", sizeable=1, rtf=True)
        self.widgets["cns_main_Layout"] = cmds.rowColumnLayout(numberOfColumns=1)
        self.widgets["cns_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=3, cw3=[100, 100, 100], select=2,
                                                        labelArray3=['Global only', 'All controllers', 'Selected'])
        #, onc=self.cnsToolFix)
        '''
        cmds.separator(h=7)
        self.widgets["all_radio"] = cmds.radioButtonGrp(numberOfRadioButtons=3, cw3=[100, 100, 100], select=1,
                                                        labelArray3=['_ctl', '_offset', 'both'],
                                                        onc=self.cnsToolFix)
        '''
        cmds.separator(h=7)
        self.widgets["cns_Layout"] = cmds.rowColumnLayout(numberOfColumns=2)
        cmds.button(l="Cns It", c=self.cnsTool, w=300)
        # self.widgets["cns_text"] = cmds.textField(text="_grp")
        cmds.showWindow()

    def cnsTool(self, *args):
        op = cmds.radioButtonGrp(self.widgets["cns_radio"], q=True, select=True)
        # grpText = cmds.textField(self.widgets["cns_text"], q=True, tx=True)
        globalCtl = pm.PyNode('global_C0_ctl')
        if op == 1:  # only global
            ctls = [globalCtl]
        elif op == 2:  # all ctls
            ctls = pm.ls('*_ctl')  #, '*_offset')
        else:  # by selected
            ctls = pm.ls(sl=True)
        try:
            pm.addAttr(globalCtl, ln="ShowCnsCtrls", at="double", dv=0, min=0, max=1)
            pm.setAttr((globalCtl + ".ShowCnsCtrls"), e=1, keyable=False, cb=1)
            pm.setAttr((globalCtl + ".ShowCnsCtrls"), 0)
        except:
            print traceback.print_exc()
            print '{} has cns show attribute'.format(globalCtl.name())
        for c in ctls:
            oParent = c.getParent()
            icon = ic.create(oParent, c.name() + "_cns", c.getMatrix(), [0, 0, 0], 'cross')
            icon.setTransformation(c.getMatrix())
            pm.parent(c, icon)
            iconShape = icon.getShape()
            pm.connectAttr(globalCtl.ShowCnsCtrls, iconShape.visibility)

            ro = pm.getAttr(c + '.rotateOrder')
            pm.setAttr(c.name() + "_cns" + '.rotateOrder', ro)

            print '[add cns controller] proccessed: {}'.format(c.name())
            print "[rotate order]" + " ro = " + str(ro)

    '''
    def cnsToolFix(self, *args):
        op = cmds.radioButtonGrp(self.widgets["cns_radio"], q=True, select=True)
        if op == 2:
            cmds.radioButtonGrp(self.widgets["all_radio"], e=True, vis=True)
        else:
            cmds.radioButtonGrp(self.widgets["all_radio"], e=True, vis=False)
    '''
