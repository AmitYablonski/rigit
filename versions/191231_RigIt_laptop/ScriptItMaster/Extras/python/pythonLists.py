myList = ["one", "two", "tree", "bark", "this_two", "two"]
myList.remove("tree")
myList.append("three")

# loop list in reverse oreder
for i in myList[::-1]:
    print i
# reverse the list
myList.reverse()
print myList

# to search in list and remove from it
import fnmatch
removeList = fnmatch.filter(myList, "two")
removeList = removeList + fnmatch.filter(myList, "one*")
for rem in removeList:
    myList.remove(rem)


elif isinstance(rPart, list) or isinstance(rPart, tuple):
    print("a list or tuple")

