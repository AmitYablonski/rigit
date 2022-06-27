from maya import cmds
import os, sys


def setupRigIt(scriptsPath, *args):
    path = scriptsPath + "/RigIt"

    if os.path.exists(path):
        if not path in sys.path:
            sys.path.append(path)

    import RigItUI
    reload(RigItUI)
    RigItUI.RigItUI(path)
