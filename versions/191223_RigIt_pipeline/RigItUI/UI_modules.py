from maya import cmds, mel
import pymel.core as pm
from functools import partial
import generalMayaPrints as gmp
reload(gmp)


def updateTextField(parUI, field, objType='', multiple=False, *args):
    parUI.defaultFeedback()
    sele = pm.selected()
    if len(sele) == 0:
        parUI.printFeedback('select an object and try again')
        return
    if multiple:
        if objType:
            temp = []
            for obj in sele:
                if objType != obj.type():
                    parUI.printFeedback('Selection must be a %s node, skipping "%s"' % (objType, obj.name()))
                    temp.append(obj)
            sele = temp
        if len(sele) == 1:
            cmds.textField(field, e=True, tx=sele[0].name())
        else:
            cmds.textField(field, e=True, tx=gmp.cleanListForPrint(sele))
    else:
        if len(sele) == 1:
            if objType:
                if objType != sele[0].type():
                    parUI.printFeedback('Selection must be a %s node' % objType)
                    return
            cmds.textField(field, e=True, tx=sele[0].name())
        else:
            parUI.printFeedback('select a single object and try again')


def selectAndAddToField(parUI, parLay, buttonText, objType='', fieldTx='', width='', multiple=False):
    if width:
        pm.rowLayout(nc=2, columnOffset2=[0, 5], w=width, p=parLay)
    else:
        pm.rowLayout(nc=2, columnOffset2=[0, 5], adjustableColumn=2, p=parLay)
    but = pm.button(l=buttonText)
    txField = cmds.textField()
    pm.button(but, e=True, c=partial(updateTextField, parUI, txField, objType, multiple))
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


def resizeScroll(scroll):
    allItems = cmds.textScrollList(scroll, q=True, allItems=True)
    if not allItems:
        cmds.textScrollList(scroll, e=True, h=100)
        return
    if len(allItems) > 16:
        cmds.textScrollList(scroll, e=True, h=300)
    elif len(allItems) > 13:
        cmds.textScrollList(scroll, e=True, h=250)
    elif len(allItems) > 6:
        cmds.textScrollList(scroll, e=True, h=200)
    elif len(allItems) <= 6:
        cmds.textScrollList(scroll, e=True, h=100)


def addScrollSetup(parUI, scrollName, parLay, title='', upDown = False):
    mainLay = pm.columnLayout(adj=True, p=parLay)
    if title:
        pm.separator(h=3, p=mainLay)
        pm.text(title, p=mainLay)
        pm.separator(h=3, p=mainLay)
    # control buttons
    cmds.rowColumnLayout(nc=3, cs=[[2, 4], [3, 4]], adj=True, p=mainLay)
    cmds.button('add from\nselection', c=partial(updateScrolls, parUI, scrollName))
    cmds.button('remove\nfrom list', c=partial(updateScrolls, parUI, scrollName, True))
    cmds.button('clear\nlist', c=partial(updateScrolls, parUI, scrollName, clear=True))
    # scroll
    parUI.widgets[scrollName + "Scroll"] = cmds.textScrollList(allowMultiSelection=True, h=100, p=mainLay)
    # add up/down buttons
    if upDown:  # todo test this
        cmds.rowColumnLayout(nc=3, cs=[[2, 5], [3, 5]], p=mainLay)
        pm.text('Move : ')
        cmds.button(l='Down', w=50, c=partial(moveScrollItem, parUI, scrollName))
        cmds.button(l='Up', w=50, c=partial(moveScrollItem, parUI, scrollName, True))


def updateScrolls(parUI, scrollName, remove=False, clear=False, *args):
    scroll = parUI.widgets[scrollName + "Scroll"]
    if clear:
        cmds.textScrollList(scroll, e=True, removeAll=True)
        resizeScroll(scroll)
        return
    if remove:
        selItem = cmds.textScrollList(scroll, query=True, selectIndexedItem=True)
        if not selItem:
            parUI.orangeFeedback('Nothing selected to remove')
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
    print 'resize'
    resizeScroll(scroll)


def moveScrollItem(parUI, scrollName, up=False, *args):  # todo test this
    scroll = parUI.widgets[scrollName + "Scroll"]
    selItem = cmds.textScrollList(scroll, query=True, selectItem=True)
    selIdx = cmds.textScrollList(scroll, query=True, selectIndexedItem=True)
    if not selIdx or not selItem:
        parUI.orangeFeedback('Nothing selected')
        return
    selIdx = selIdx[0]
    appendPos = selIdx + 1
    if up:
        appendPos = selIdx - 1
    cmds.textScrollList(scroll, edit=True, removeIndexedItem=selIdx)
    cmds.textScrollList(scroll, edit=True, appendPosition=[appendPos, selItem[0]])
    cmds.textScrollList(scroll, edit=True, selectIndexedItem=appendPos)


# todo test below ?

def addSplitLayout(parLay, split=False):
    if split:
        splitLay = pm.rowColumnLayout(nc=5, adj=True, p=parLay)
    else:
        splitLay = pm.rowColumnLayout(nc=2, adj=True, p=parLay)
    L_Lay = pm.columnLayout(adj=True)
    if split:
        pm.separator(w=2, p=splitLay)
        pm.separator(w=1, bgc=[.2,.2,.2], p=splitLay)
        pm.separator(w=2, p=splitLay)
    R_Lay = pm.columnLayout(adj=True, p=splitLay)
    return L_Lay, R_Lay

def addScrollSetup_old(parUI, scrollName='', parLay='', w=170, upDown=True):
    if parLay:
        mainLay = cmds.rowColumnLayout(nc=1, p=parLay)
    else:
        mainLay = cmds.rowColumnLayout(nc=1)

    pm.text(scrollName + ' List', p=mainLay)

    cmds.rowColumnLayout(nc=2, cs=[2, 4], p=mainLay)
    # todo edit so it won't need parUI ?
    cmds.button('add from\nselection', w=w / 2 - 2, c=partial(updateScrolls, parUI, scrollName))
    cmds.button('remove\nfrom list', w=w / 2 - 2, c=partial(updateScrolls, parUI, scrollName, True))
    parUI.widgets[scrollName + "Scroll"] = cmds.textScrollList(allowMultiSelection=True, h=100, w=w, p=mainLay)
    if upDown:
        cmds.rowColumnLayout(nc=3, cs=[[2, 5], [3, 5]], p=mainLay)
        pm.text('Move : ')
        cmds.button(l='Down', w=50, c=partial(moveScrollItem, scrollName))
        cmds.button(l='Up', w=50, c=partial(moveScrollItem, scrollName, True))

def renumberScroll(scroll):  # todo remove
    allItems = cmds.textScrollList(scroll, q=True, allItems=True)
    tempList = []
    i = 1
    for item in allItems:
        tempList.append('%s - %s' % (i, item.partition(' - ')[2]))
        i += 1
    cmds.textScrollList(scroll, e=True, removeAll=True)
    for item in tempList:
        cmds.textScrollList(scroll, edit=True, append=item)
