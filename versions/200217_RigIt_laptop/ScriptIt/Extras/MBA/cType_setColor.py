############ C-Type types ################

#
def assosiateColor(selection, shader):
    pm.select(shader)
    shader_name = cmds.ls(sl=True)[0]
    shader_sg = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name="{}SG".format(shader_name))
    shader.outColor.connect(shader_sg.surfaceShader)
    for sel in selection:
        cmds.select(sel, tgl=True)
    cmds.sets(e=True, forceElement=shader_sg.name())