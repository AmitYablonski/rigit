import pymel.core as pm

# select the entire guide and run this step
fozzieGuide = pm.ls(sl=True)
guideDict = {}
for obj in fozzieGuide:
    trans = pm.xform(obj, query=True, t=True, ws=True)
    for i in range(0, 3):
        trans[i] = round(trans[i], 3)
    rot = pm.xform(obj, query=True, ro=True, ws=True)
    for i in range(0, 3):
        rot[i] = round(rot[i], 3)
    parent1 = ''
    parent1 += obj.listRelatives(p=True)[0].name()
    guideDict[obj.name()] = [trans, rot, parent1]

# this step takes the dictionary and print it nicely to paste into another scene
string = 'guideCtrls = {'
for obj in guideDict:
    string += '"%s" : %s,\n\t\t\t  ' % (obj, guideDict[obj])
print string + "}"

# run this part after copying the dictionary ro a scene with a guide to position
for i in range(0, 5):  # running it a few times to work well with the hierarchy
    for obj in guideCtrls:
        try:
            pm.select(obj)
            pm.xform(obj, t=guideCtrls[obj][0], ws=True)
            pm.xform(obj, ro=guideCtrls[obj][1], ws=True)
        except:  # tells you what's missing - after adding it, you may run this part again
            print("Can't find '%s' in scene. - parent: %s" % (obj, guideCtrls[obj][2]))
