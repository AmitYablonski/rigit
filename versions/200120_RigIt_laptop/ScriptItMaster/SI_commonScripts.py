def importScript(path, clashName):
    script = 'cmds.file(%s, i=True, typ="mayaAscii", ignoreVersion=True, rpr=%s)' % (path, clashName)
    return script


