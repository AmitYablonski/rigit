from maya import cmds, mel
import pymel.core as pm
from functools import partial


def updateTextField(parUI, field, objType='', multiple=False, *args):
    parUI.defaultFeedback()
    sele = pm.selected()
    if len(sele) == 0:
        parUI.printFeedback('select an object and try again')
        return
    if multiple:
        print("multiple object isn't made yet") # todo make this support multiple objects
    else:
        if len(sele) == 1:
            if objType:
                if objType != sele[0].type():
                    parUI.printFeedback('Selection must be a %s node' % objType)
                    return
            cmds.textField(field, e=True, tx=sele[0].name())
        else:
            parUI.printFeedback('select a single object and try again')


def selectAndAddToField(parUI, parLay, buttonText, objType='', fieldTx='', width=''):
    if width:
        pm.rowLayout(nc=2, columnOffset2=[0, 5], w=width, p=parLay)
    else:
        pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=parLay)
    but = pm.button(l=buttonText)
    txField = cmds.textField()
    pm.button(but, e=True, c=partial(updateTextField, parUI, txField, objType))
    if fieldTx:
        cmds.textField(txField, e=True, tx=fieldTx)
    return txField


def textAndField(parLay, buttonText, fieldTx='', width=''):
    if width:
        pm.rowLayout(nc=2, columnOffset2=[0, 5], w=width, p=parLay)
    else:
        pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=parLay)
    but = pm.text(buttonText)
    txField = cmds.textField()
    if fieldTx:
        cmds.textField(txField, e=True, tx=fieldTx)
    return txField
