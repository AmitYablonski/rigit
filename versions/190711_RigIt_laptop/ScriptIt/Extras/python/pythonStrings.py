myStr = "check.one__two___check"

if myStr.endswith('check'):
    print(True)

# search mothods
part1 = myStr.partition('__')  # searches from the start
part2 = myStr.partition('.')  # searches from the start
rPart = myStr.rpartition('__')  # searches from the end
print(part1)
print(part2)
print(rPart)
'''
part1[0] == "check.one"
part1[1] == "__" 
part1[2] == "two___check"
part2[0] == "check"
part2[1] == "." 
part2[2] == "one__two___check"
'''
'''
rPart[0] == "check.one__two_"
rPart[1] == "__" 
rPart[2] == "check"
'''

# print list with 3 decimal points
vector = [-9.44596, 9.2248, 2.5272567664667136]
print("translate = [%0.3f, %0.3f, %0.3f]" % (vector[0], vector[1], vector[2]))

if isinstance(myStr, str):
    print("a string")
