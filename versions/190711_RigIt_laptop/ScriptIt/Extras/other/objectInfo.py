relatives = pm.listRelatives("myObject")
shape = pm.listRelatives("myObject", type="shape")
shape = pm.listRelatives("myObject", s=True)
parent = pm.listRelatives("myObject", p=True)


# find nodes through history
historyNodes = pm.listHistory("myObject")
for hist in history:
    types = pm.nodeType(hist, inherited=True)
    if 'geometryFilter' in types:
        if 'BlendShape' in pm.nodeType(hist, apiType=True):
            print("found a blend shape")
        if 'Wrap' in pm.nodeType(hist, apiType=True):
            print("found a wrap deformer")
        if 'Skin' in pm.nodeType(hist, apiType=True):
            print("found a skin")


# query object's attributes
allAttrs = pm.listAttr("obj", r=1, s=1, k=1)
# remove translate and rotate from list
import fnmatch
removeAttrs = fnmatch.filter(allAttrs, "translate*")
removeAttrs = removeAttrs + fnmatch.filter(allAttrs, "rotate*")
for attr in removeAttrs:
    allAttrs.remove(attr)


# attribute queries:
pm.getAttr("obj.attribute"))  # query value
pm.attributeQuery("attribute", node="obj", range=True)  # query attribute's range
# check if it is an enum attributes
pm.attributeQuery(attr, node=sel, e=True)


# xform query. ws=worldSpace. t=translate, ro=rotate, s=scale
translate = pm.xform("objName", query=True, t=True, ws=True)  # ws = worldSpace
