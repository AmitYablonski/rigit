plusMin = pm.shadingNode('plusMinusAverage', asUtility=True, name="plusMin_" + name)

# change operation to average
plusMin.setAttr("op", 3)  # 2 is for subtract

# single attribute connections:
obj.attributeX >> plusMin.i1[0]
obj2.attributeX >> plusMin.i1[1]
plusMin.o1 >> obj.attributeX

# vector connections:
# example for connecting a list of multiplyDivide nodes
# (can work with all kinds of vector connections)
for ii in enumerate(transMult):
    pm.connectAttr(ii[1] + ".o", plusMin + ".i3%s" % [ii[0]])
    # index = ii[0]
    # node = ii[1]
plusMin.o3 >> obj.attribute

# find the next available input1 index for plusMin
plusmin = pm.PyNode("plusMinusAverage1")
idx=0
i=0
conn = plusmin.i1[0].listConnections()
while conn != []:
    conn = plusmin.i1[i].listConnections()
    if conn == []:
        idx=i
        break
    else:
        i+=1
print(idx)