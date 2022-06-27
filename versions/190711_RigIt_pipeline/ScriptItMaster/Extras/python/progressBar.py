import maya.cmds as cmds

# Create a custom progressBar in a windows ...

window = cmds.window()
cmds.columnLayout()

progressControl = cmds.progressBar(maxValue=10, width=300)
cmds.button(label='Make Progress!', command='cmds.progressBar(progressControl, edit=True, step=1)')

cmds.showWindow(window)

# Or, to use the progress bar in the main window ...

import maya.mel

gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar')

cmds.progressBar(gMainProgressBar,
                 edit=True,
                 beginProgress=True,
                 isInterruptable=True,
                 status='Example Calculation ...',
                 maxValue=5000)

for i in range(5000):
    if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
        break

    cmds.progressBar(gMainProgressBar, edit=True, step=1)

cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)

