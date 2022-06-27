# wrappers
import pymel.core as pm

#1.
with open('myfile.txt') as f:
    text = f.read()

#2. This is pretty much what the "with" does:
# open can fail,
# so make sure the variable is referenced
f = None
try:
    f = open('myfile.txt')
    text = f.read() # only happens if open succeeds
finally:
    if f: # If open failed, f is still None
        f.close()

#3. object considered context manager, can be used by the with statement:
#  if it has the following two methods:
def __enter__(self):
    ...
def __exit__(self, exc_type, exc_value, exc_tb):
    ...

#4. basically how open as a context manager can be thought of
class safeopen(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.f = None
    def __enter__(self):
        self.f = open(*self.args, **self.kwargs)
        return self.f
    def __exit__(self, *exc_info):
        if self.f:
            self.f.close()

#5. We can use this new type just like the open builtin.
with safeopen('myfile.txt') as f:
    text = f.read()

#6.
class demo(object):
    def __init__(self):
        print 'init' #(1)
    def __enter__(self):
        print 'entered' #(2)
        return 'hello!' #(3)
    def __exit__(self, *exc_info):
        print 'exited. Exc_info:', exc_info #(4)

#7.
with demo() as d:
    print 'd is', d

#8. If we raise an error while under the context manager, we see different feedback:
# NOTE: rare to handle exceptions inside of the __exit__ method.
# Just think about it as you would a finally block.
# There are other details to its behavior, such as special return values.
with demo() as d:
    raise RuntimeError('hi')

'''
NOTE
There is also a "contextlib "module that has a contextmanager decorator that can turn a function into a context manager.
This form ends up being much more convenient than the explicit __enter__ and __exit__ methods on a custom class.
However it is also more magical so I've chosen not to present it here.
If you find yourself writing a significant number of context managers, you should learn how to use it.
It can really streamline your code, especially for simple cases.
'''

#9.
class undo_chunk(object):
    def __enter__(self):
        pm.undoInfo(openChunk=True)
    def __exit__(self, *_):
        pm.undoInfo(closeChunk=True)

#10. if it's in a file called mayautils.py
with mayautils.undo_chunk():
    pm.joint(), pm.joint()
print pm.ls(type='joint')
pm.undo()
print pm.ls(type='joint')
