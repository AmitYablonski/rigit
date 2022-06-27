import sys, os

path = "P:/MBA_SE02/scripts/rigging/RigIt"
if os.path.exists(path):
    if not path in sys.path:
        sys.path.append(path)

import generalMayaTools as gmt
import pymel.core as pm
from maya import mel, cmds

# pass a shape to get the skin
gmt.getSkin("objShape")

# make a selection with the desired skin and add an object to bind
# bindAndCopy will check what influences are in the skin (even if influence is 0)
# and will bind to it and will copy the skin
pm.select("objWithSkin")
pm.select("objToBind", add=True)
gmt.bindAndCopy()

# get namespace from selection
gmt.namespaceFinder()

# delete constraints
gmt.deleteConstraints()

# lock/unlock all attrs
gmt.lockAttributes(True)  # False is to unlock

# parent shape will take the first selections (select transforms or shapes)
# and will make their shapes children of the last selection (transform)
gmt.parentShape()

# use liteWrap
# "objToWrap" is where the wrap will be made
# "heavyMesh" is the object that will be followed
# "deleteFaces" is a list of faces to delete. example = [u'.f[1]', u'.f[4:6]', u'.f[8:17]']
# to create the deleteFaces easily - use the print component in Avalanch
# returns simpleGeo, newWrap  -  simpleGeo is the light wrapper obj without the faces to delete
gmt.liteWrap(objToWrap, heavyMesh, deleteFaces)

# lock/unlock attributes usage examples (works by selection):
gmt.lockAttributes(True)  # locks translate, rotate and scale
gmt.lockAttributes(False)  # unlocks translate, rotate and scale
gmt.lockAttributes(True, ["tx", "rz"])  # locks the listed attributes
gmt.lockAttributes(True, "rx")

# enable override and change color for selection
red = 13
gmt.colorOverride(red)

# main colors:
# blue=6, darkGreen=7, red=13, green=14, paleBlue=15, yellow=17
'''
# full color list:
0, 'gray' / 1, 'black' / 2, 'darkGray' / 3, 'lightGray' / 4, 'paleRed' / 5, 'navyBlue'
6, 'blue' / 7, 'darkGreen' / 8, 'purple' / 9, 'pink' / 10, 'brown' / 11, 'darkBrown'
12, 'otherRed' / 13, 'red' / 14, 'green' / 15, 'paleBlue' / 16, 'white' / 17, 'yellow'
18, 'azure' / 19, 'paleGreen' / 20, 'palePink' / 21, 'skin' / 22, 'paleYellow'
23, 'paleGreen2' / 24, 'orange' / 25, 'paleYellow2' / 26, 'paleGreen2' / 27, 'paleGreen3'
28, 'paleAzure' / 29, 'paleBlue2' / 30, 'palePurple' / 31, 'palePink'
'''
