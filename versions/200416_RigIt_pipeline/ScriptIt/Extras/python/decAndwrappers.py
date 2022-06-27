# wrappers
import pymel.core as pm

#1. example to preserve selection
def preserve_selection(func):
    def inner(*args, **kwargs): #(1) inner that takes any positional and keyword arguments.
        sel = list(pm.selected()) #(2) Store the current selection.
        result = func(*args, **kwargs) #(3) Invoke the passed function func and store the result
        pm.select(sel, replace=True) #(4) Restore the original selection.
        return result #(5) Return the value the passed function returned.
    return inner #(6) Return the closure, which will replace the decorated function.

#2. just for the logic - doesn't work without adding the superExporter
@preserve_selection
def export_char_meshes(path):
    objs = [o for o in pm.ls(type='mesh') 
            if '_char_' in o.name()]
    pm.select(objs)
    pm.superExporter(path)




