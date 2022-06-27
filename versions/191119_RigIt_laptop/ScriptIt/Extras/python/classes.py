# super basic class examples
class MyClass:
    """A simple example class"""
    i = 12345

    def f(self):
        return 'hello worldsss'

x = MyClass()

print x.i
print x.f()
print x.__doc__
print x.__class__

# create, edit and delete attribute
x.counter = 1
while x.counter < 10:
    x.counter = x.counter * 2
print x.counter
del x.counter

# inheritance
class MyInherit(MyClass):
    """A simple inheritance example"""
    def e(self):
        return "whatsup?"

x = MyInherit()
print x.i
print x.f()
print x.e()

# check class relationships
print isinstance(x, MyClass)
print issubclass(MyClass, MyInherit)
print issubclass(MyInherit, MyClass)

# raise
class B:
    pass
class C(B):
    pass
class D(C):
    pass

# if B except clouse was first, it would have printed B, B, B
for c in [B, C, D]:
    try:
        raise c()
    except D:
        print "D"
    except C:
        print "C"
    except B:
        print "B"

# create an iterator class that Reverses the class's string
class Reverse:
    """Iterator for looping over a sequence backwards."""
    def __init__(self, data):
        self.data = data
        self.index = len(data)

    def __iter__(self):
        return self

    def next(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.data[self.index]
rev = Reverse('spam')
iter(rev)
for char in rev:
    print char

# Generators - another form of reverse
def reverse(data):  # compact: __iter__() and next() created automatically
    for index in range(len(data)-1, -1, -1):  # rangeStart, direction/skip, rangeEnd
        yield data[index]

for char in reverse('golf'):
    print char

