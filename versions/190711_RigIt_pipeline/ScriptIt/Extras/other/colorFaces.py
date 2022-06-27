# shader must be PyNode
# selection can be faces, objects and a list of objects/faces
def assosiateColor(selection, shader):
    shader_sg = ''
    for con in shader.listConnections():
        if not shader_sg and isinstance(con, pm.nodetypes.ShadingEngine) and "SG" in con.name():
            shader_sg = con
            print con
    if not shader_sg:
        shader_sg = pm.sets(renderable=True, noSurfaceShader=True, empty=True,
                            name="{}SG".format(shader.name()))
        shader.outColor.connect(shader_sg.surfaceShader)
    pm.sets(shader_sg, e=True, forceElement=selection)


faces = [u'pSphereShape1.f[260:299]']
shader = pm.PyNode("lambert1")

assosiateColor(faces, shader)

obj = ['pSphere1', 'pCube1']
shader = pm.PyNode("lambert2")

assosiateColor(obj, shader)