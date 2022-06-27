def importsMaker(charName, varName, importFiles):
    '''
    Builds and returns the variant Runner's header
    :param charName: string with character name
    :param varName: string with variant name
    :param importFiles: a list of import files (must be a list)
    :return: variant runner's header
    '''
    if not charName or not varName:
        return ''
    # headline
    script = '# -------------------- variant %s %s RUNNER -------------------- #\n\n' % (charName, varName)
    # imports
    script += 'import sys\n' \
              'import pymel.core as pm\n' \
              'from maya import cmds, mel\n' \
              'import mgear.maya.skin as mSkin\n\n'
    # rigFunk import
    script += "# import RiggingFunctions\np = r'P:\MBA_SE02\scripts\\'\n" \
              "if p not in sys.path:\n\t" \
              "sys.path.append(p)\n" \
              "import rigging.VariantsFunctions as vf\n" \
              "import rigging.RiggingFunctions as rf\n\n"
    # variant association
    script += '# variant association\n' \
              'character_name = "%s"\n' \
              'var_name = "%s"\n' \
              'var_items = %s\n\n' % (charName, varName, importFiles)
    # file imports
    script += '# -------------------- import base -------------------- #\n\n' \
              'def import_base_rig(char_name):\n\t' \
              'cmds.file("P:/MBA_SE02/assets/characters/%s/public/%s_rigging.ma" % (char_name,char_name),\n' \
              '              i=True, typ="mayaAscii", ignoreVersion=True)\n\n' \
              'import_base_rig(character_name)\n\n\n'
    script += '# -------------------- import variant items -------------------- #\n\n' \
              'def import_var_items(var_name, var_items):\n\tfor item in var_items:\n\t\t' \
              'cmds.file("P:/MBA_SE02/assets/variants/%s/rigging/%s/importFiles/%s.ma" % (var_name,var_name,item),\n' \
              '                  i=True, typ="mayaAscii", ignoreVersion=True)\n\n' \
              'import_var_items(var_name, var_items)\n\n'
    return script



def colorMaker(colors):
    script = '# -------------------- color change --------------------#\n\n' \
             'color_change={'
    i = 1
    first = True
    for name, val, objs in colors:
        if first:
            script += '\n\t'
            first = False
        else:
            script += ',\n\t'
        script += '"color%s": {\n\t\t' \
                  '"mtl_name": "%s",\n\t\t' \
                  '"color": %s,\n\t\t' \
                  '"geo": %s\n\t' \
                  '}' % (i, name, val, objs)
    script += '\n}'
    # add method
    script += 'def add_var_colors(color_dict):\n\t' \
              'for clr in color_dict:\n\t\t' \
              'clr = color_dict[clr]\n\t\t' \
              'mtl_name = clr["mtl_name"]\n\t\t' \
              'color_rgb = clr["color"]\n\t\t' \
              'geo = clr["geo"]\n\t\t' \
              'mtl = pm.shadingNode("lambert", asShader=True, n=mtl_name)\n\t\t' \
              'mtl.attr("color").set(color_rgb)\n\t\t' \
              'pm.select(cl=1)\n\t\t' \
              'for item in geo:\n\t\t\t' \
              'pm.select(item, add=1)\n\t\t' \
              'pm.hyperShade(a=mtl)\n\t\t' \
              'pm.select(cl=1)\n\n\n' \
              'add_var_colors(color_change)'
    return script


def highGrpAdder(objs):
    script = "# -------------------- high_grp -------------------- #\n\n" \
             "# add objs to high_grp\nhighObjs=["
    first = True
    for obj in objs:
        if first:
            script += obj
            first = False
        else:
            script += ', ' + obj
    script += "]\n" \
              "pm.parent(highObjs, 'high_grp')\n\n"
    return script


def setupAdder(objs):
    script = "# -------------------- setup grp -------------------- #\n\n" \
             "# add objs to setup\nsetupObjs=["
    first = True
    for obj in objs:
        if first:
            script += obj
            first = False
        else:
            script += ', ' + obj
    script += "]\n" \
              "pm.parent(highObjs, 'high_grp')"
    return script
    # todo if animal: parent props to 'extraSetup' etc


def importShapes(var_name, bspName):
    script = '# import correctives\n'
    script += "mel.eval(\n\t" \
              "'source \"P:/MBA_SE02/assets/variants/%s/rigging/%s/shapesData/" \
              "%s.mel\"')\n\n" % (var_name, var_name, bspName)
    return script


def deleteUnsuedAdder():
    script = "# Delete unused nodes\n" \
             "mel.eval('MLdeleteUnused;')\n"
    return script
