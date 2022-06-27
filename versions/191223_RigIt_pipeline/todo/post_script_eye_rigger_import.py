import os

import pymel.core as pc
import mgear.rigbits.facial_rigger.eye_rigger


basename = os.path.basename(pc.sceneName())
filename = os.path.splitext(basename)[0]
directory = os.path.dirname(pc.sceneName())

# Find *.eyes folder starting with same name as current file
eyes_files = []
for folder in os.listdir(directory):
    if folder == (filename + ".eyes"):
        path = os.path.join(directory, folder)
        for f in os.listdir(path):
            if f.endswith(".eyes"):
                eyes_files.append(os.path.join(path, f))

for eyes_file in eyes_files:
    path = os.path.join(directory, eyes_file)
    mgear.rigbits.facial_rigger.eye_rigger.rig_from_file(path)