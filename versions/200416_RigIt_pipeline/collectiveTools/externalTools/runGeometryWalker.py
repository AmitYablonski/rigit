import os, sys

path = "P:/MBA_SE02/scripts/rigging"

if os.path.exists(path):
    if not path in sys.path:
        sys.path.append(path)

import geometryWalker.QT.pickWalker_UI as pickWalker_UI

pickWalker_UI.pickWalkerUI()
