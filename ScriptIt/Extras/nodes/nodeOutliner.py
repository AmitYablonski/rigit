import maya.cmds as cmds

mywindow = cmds.window()
myform = cmds.formLayout( numberOfDivisions=100 )

# Create an outliner that will print the name of
# every object added to it to history pane of the
# script editor, then display all available input
# plugs on the node.
def onAddNode(name):
    print name
myoutliner = cmds.nodeOutliner( showInputs=True, addCommand=onAddNode )

# Attach the nodeOutliner to the layout
cmds.formLayout( myform, edit=True, attachForm=((myoutliner, 'top', 5), (myoutliner, 'left', 5), (myoutliner, 'bottom', 5), (myoutliner, 'right', 5)) )

# Display the window with the node Outliner
cmds.showWindow( mywindow )

# Create a sphere
objectName = cmds.sphere()

# Have the outliner display the sphere
cmds.nodeOutliner( myoutliner, e=True, a='nurbsSphere1' )
