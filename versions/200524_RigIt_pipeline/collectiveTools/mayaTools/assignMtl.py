import pymel.core as pm

#assign mtl from obj to obj
#works only from first selection to second selection

sel_list = pm.ls(sl=True) 
source = sel_list[0]

pm.select(source)
pm.hyperShade(shaderNetworksSelectMaterialNodes=True)
for shd in pm.selected(materials=True):
    if [c for c in shd.classification() if 'shader/surface' in c]:
        print 'obj:', source
        print 'mtl:', shd
        #assign mtl
        for i in range(1, len(sel_list)):
            pm.select(sel_list[i])
            pm.hyperShade(a=shd)