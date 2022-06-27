import pymel.core as pm
import mGear_riggingTools as rt


def matachPivot(target, source):
    pivotTranslate = pm.xform(source, q=True, ws=True, rotatePivot=True)
    pm.xform(target, ws=True, pivots=pivotTranslate)

controls = ["control_C0_fk"]  # the mgear controller's name without the number and "_ctl"
simpleControl = "control_C"  # the new controller's name without the number etc

for obj in controls:
    for i in range(0, 3): # for 3 controllers in a chain
        trueControl = pm.PyNode(obj + str(i + 1) + "_ctl")  # make sure this matches the names for thw mgear controllers
        trueSimpleCtl = pm.PyNode(simpleControl + str(i) + "_ctl")  # make this match your new controllers
        npoGrp = pm.group(em=1, n=(trueControl.name() + "_simpleCtrl"))
        matachPivot(npoGrp, trueSimpleCtl)
        Parent1 = trueControl.listRelatives(p=True)[0]
        pm.parent(npoGrp, Parent1)
        pm.parent(trueControl, npoGrp)
        pm.select(npoGrp)
        rt.addNPO()
        trueSimpleCtl.t >> npoGrp.t
        trueSimpleCtl.r >> npoGrp.r
        trueSimpleCtl.s >> npoGrp.z
        pm.select(trueControl)
        rt.addNPO()
