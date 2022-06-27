#############		treeView (like layer selection)
import maya.cmds as cmds

def selectTreeCallBack(*args):
  print 'selection :- str= ' + args[0] + ' onoff= ' + str(args[1])
  return True

def pressTreeCallBack(*args):
  print 'Right press :- str= ' + args[0] + ' onoff= ' + str(args[1])
def pressTreeCallBackMid(*args):
  print 'Mid press :- str= ' + args[0] + ' onoff= ' + str(args[1])
def pressTreeCallBackLeft(*args):
  print 'Left press :- str= ' + args[0] + ' onoff= ' + str(args[1])

from maya import cmds
window = cmds.window()
layout = cmds.formLayout()

control = cmds.treeView( parent = layout, numberOfButtons = 3, abr = False )

cmds.formLayout(layout,e=True, attachForm=(control,'top', 2))
cmds.formLayout(layout,e=True, attachForm=(control,'left', 2))
cmds.formLayout(layout,e=True, attachForm=(control,'bottom', 2))
cmds.formLayout(layout,e=True, attachForm=(control,'right', 2))

cmds.showWindow( window )

cmds.treeView( control, e=True, addItem = ("layer 1", ""))
cmds.treeView( control, e=True, addItem = ("layer 2", ""))
cmds.treeView( control, e=True, addItem = ("layer 3", ""))
cmds.treeView( control, e=True, addItem = ("layer 4", ""))
cmds.treeView( control, e=True, addItem = ("layer 5", ""))
cmds.treeView( control, e=True, addItem = ("layer 6", ""))
cmds.treeView( control, e=True, addItem = ("layer 7", "layer 2"))
cmds.treeView( control, e=True, addItem = ("layer 8", "layer 2"))
cmds.treeView( control, e=True, addItem = ("layer 9", "layer 2"))
cmds.treeView( control, e=True, addItem = ("layer 10", "layer 8"))
cmds.treeView( control, e=True, addItem = ("layer 11", "layer 2"))
cmds.treeView( control, e=True, addItem = ("layer 12", ""))
cmds.treeView( control, e=True, addItem = ("layer 13", "layer 10"))
cmds.treeView(control,edit=True,pressCommand=[(1,pressTreeCallBackLeft),(2,pressTreeCallBackMid),(3,pressTreeCallBack)])
cmds.treeView(control,edit=True,selectCommand=selectTreeCallBack)


cmds.treeView( control, edit=True, removeAll = True )




###################