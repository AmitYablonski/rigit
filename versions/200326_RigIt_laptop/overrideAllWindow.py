from maya import cmds
import pymel.core as pm
from functools import partial


class Override:
    def __init__(self):
        self.overrideWin()

    def overrideWin(self):
        if cmds.window("override_window", exists=True):
            cmds.deleteUI("override_window")
        window = cmds.window("override_window", title="Override UI", sizeable=1, rtf=True)
        mainLay = cmds.rowColumnLayout(numberOfColumns=1)
        cmds.separator(h=7, p=mainLay)
        pm.text('Override all')
        cmds.separator(h=7, p=mainLay)
        cmds.rowColumnLayout(numberOfColumns=5)
        cmds.separator(w=30)
        cmds.button(l="Lock", c=partial(self.override, True))
        cmds.separator(w=10)
        cmds.button(l="Unlock", c=partial(self.override, False))
        cmds.separator(w=30)
        cmds.separator(h=10, p=mainLay)
        cmds.window(window, e=True, rtf=True)

        cmds.showWindow()

    def override(self, lock, *args):
        allObjs = []
        objs = pm.ls(g=True)
        for obj in objs:
            if obj:
                if obj.type() != 'nurbsCurve':
                    allObjs.append(obj)
                    par = obj.getParent()
                    if par not in allObjs:
                        allObjs.append(par)
        if pm.objExists('high_grp'):
            allObjs.append('high_grp')
            highObjs = pm.listRelatives('high_grp', ad=True, type='transform')
            for obj in highObjs:
                if obj:
                    if obj.type() != 'nurbsCurve':
                        allObjs.append(obj)
                        par = obj.getParent()
                        if par not in allObjs:
                            allObjs.append(par)
        pm.select('*:high_grp')
        highGrps = pm.selected()
        if highGrps:
            for hGrp in highGrps:
                allObjs.append(hGrp)
                highObjs = pm.listRelatives(hGrp, ad=True, type='transform')
                for obj in highObjs:
                    if obj:
                        if obj.type() != 'nurbsCurve':
                            allObjs.append(obj)
                            par = obj.getParent()
                            if par not in allObjs:
                                allObjs.append(par)
        self.disableOverride(allObjs, lock)
        pm.select(cl=True)

    def disableOverride(self, objs, lock):
        enable = 0
        if lock:
            enable = 1
        if not objs:
            return
        for obj in objs:
            try:
                pm.setAttr(obj + '.overrideEnabled', enable)
                try:
                    shps = pm.listRelatives(obj, s=True)
                    if shps:
                        #print 'da'
                        for shp in shps:
                            #print shp
                            pm.setAttr(shp + '.overrideEnabled', enable)
                except:
                    print 'no shapes found on %s' % obj
            except:
                connection = pm.connectionInfo(obj + '.overrideEnabled', sourceFromDestination=True)
                pm.disconnectAttr(connection, pm.disconnectAttr(obj + '.overrideEnabled', getExactDestination=True))
                pm.setAttr(obj + '.overrideEnabled', oe)
            pm.setAttr(obj + '.overrideDisplayType', 2)

Override()
