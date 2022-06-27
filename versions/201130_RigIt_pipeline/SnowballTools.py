from maya import cmds, mel
import pymel.core as pm
import mgear

__author__ = 'Amir Ronen'


def disableOverride(*args):
    # turn off override also on shape
    selection = pm.ls(sl=True)
    if selection is []:
        print("make a selection and try again")
    for sel in selection:
        try:
            pm.setAttr(sel + '.overrideEnabled', 0)
        except:
            connection = pm.connectionInfo(sel + '.overrideEnabled', sourceFromDestination=True)
            pm.disconnectAttr(connection, pm.disconnectAttr(sel + '.overrideEnabled', getExactDestination=True))
            pm.setAttr(sel + '.overrideEnabled', 0)
        print(sel + " => Override disabled.")
        try:
            shape = pm.listRelatives(sel, type="shape")[0]
            # instead of taking "[0]", remove "Orig" shapes from the list
            pm.setAttr(shape + '.overrideEnabled', 0)
            print(shape + " => Override disabled.")
        except:
            print(sel + " => Has no shape.")


def disableOverrideAllOff(*args):
    selection = pm.ls(sl=True)
    highGrp = 'high_grp'
    selectionSet = pm.listRelatives(highGrp, ad=True, type='transform')
    pm.select(highGrp, selectionSet)
    disableOverride()
    pm.select(selection)


def disableOverrideAllOn(onn=False, *args):
    highGrp = 'high_grp'
    if onn:
        pm.setAttr(highGrp + '.overrideEnabled', 1)
        pm.setAttr(highGrp + '.overrideDisplayType', 2)
    else:
        selectionSet = pm.listRelatives(highGrp, ad=True, type='transform')
        selectionSet.append(highGrp)
        for sel in selectionSet:
            pm.setAttr(sel + '.overrideEnabled', 1)
            pm.setAttr(sel + '.overrideDisplayType', 2)

