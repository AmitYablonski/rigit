import os

import pymel.core as pc
import ngSkinTools.importExport
import mgear


basename = os.path.basename(pc.sceneName())
filename = os.path.splitext(basename)[0]
directory = os.path.dirname(pc.sceneName())

# Find *.skin folder starting with same name as current file
json_files = []
for folder in os.listdir(directory):
    if folder == (filename + ".skin"):
        path = os.path.join(directory, filename + ".skin")
        for f in os.listdir(path):
            if f.endswith(".json"):
                json_files.append(os.path.join(path, f))

mismatch_files = []
for json_file in json_files:
    path = os.path.join(directory, json_file)
    importer = ngSkinTools.importExport.JsonImporter()
    with open(path) as f:
        data = importer.process(f.read())

        missing_nodes = []
        for name in data.getAllInfluences():
            if not pc.objExists(name):
                missing_nodes.append(name)

        if missing_nodes:
            raise ValueError(
                "Missing joints for {0}:\n{1}".format(
                    path, "\n".join(missing_nodes)
                )
            )

        # Setup skinned mesh from deformer members
        joints = pc.PyNode("rig_deformers_grp").members()

        # Find mesh from filename
        mesh_name = os.path.splitext(os.path.basename(json_file))[0]
        if not pc.objExists(mesh_name):
            mismatch_files.append(json_file)
            continue
        mesh = pc.PyNode(mesh_name)
        skinCluster = pc.skinCluster(
            joints, mesh, skinMethod=2, removeUnusedInfluence=False
        )
        data.saveTo(mesh.name())

if mismatch_files:
    mgear.log(
        "Missing meshes for files:\n{0}".format("\n".join(mismatch_files))
    )