import os

import pymel.core as pc
from studiolibrarymaya import animitem


basename = os.path.basename(pc.sceneName())
filename = os.path.splitext(basename)[0]
directory = os.path.dirname(pc.sceneName())

# Find *.anim folder starting with same name as current file
anim_folder = None
for f in os.listdir(directory):
    if f == (filename + ".anim"):
        anim_folder = f

# Loading an animation item
if anim_folder:
    item = animitem.AnimItem(os.path.join(directory, anim_folder))
    item.load(
        objects=[],
        namespaces=[],
        option=animitem.PasteOption.ReplaceCompletely,
        connect=False,
        currentTime=False
    )