import pymel.core as pm
import mGear_riggingTools as rt
import fnmatch

################# Create Global Jiggle Volume Control ######################
mainCtrl = 'local_C0_ctl'
attrName = 'GlobalSpringVolume'
pm.addAttr(mainCtrl, ln=attrName, at="double", dv=0, min=0, max=1)
pm.setAttr(mainCtrl + "." + attrName, e=1, keyable=True)
pm.setAttr(mainCtrl + "." + attrName, 0)

pm.select('*UI_*')  # if it should get connected to all UIs (add to selection other controllers if needed)
uiObjects = pm.ls(sl=True)

theAttributeList = []
for o in uiObjects:
    filtered = []
    attrs = pm.listAttr(o, r=1, s=1, k=1)
    filtered = fnmatch.filter(attrs, '*intensity*')
    if filtered.count > 0:
        for i in filtered:
            FullName = (o + "." + i)
            theAttributeList.append(FullName)

numOfMults = len(theAttributeList) / 3 + sorted((0, (len(theAttributeList) % 3), 1))[1]

counter = 0
for i in range(0, numOfMults):
    MultNode = pm.createNode("multiplyDivide")
    for multCon in "XYZ":
        if counter < len(theAttributeList):
            origOutputConnections = pm.listConnections(theAttributeList[counter], d=True, s=False, scn=True, p=1)
            for con in origOutputConnections:
                pm.disconnectAttr(theAttributeList[counter], con)
            pm.connectAttr(theAttributeList[counter], (MultNode + ".input1" + multCon))
            pm.connectAttr(mainCtrl + "." + attrName, (MultNode + ".input2" + multCon))
            for con in origOutputConnections:
                pm.connectAttr((MultNode + ".output" + multCon), con)
            counter = counter + 1

for attr in theAttributeList:
    pm.setAttr(attr, 1)

pm.currentTime(2)
pm.currentTime(1)
