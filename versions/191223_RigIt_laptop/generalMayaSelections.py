from maya import cmds, mel
import pymel.core as pm
import generalMayaTools as gmt
import fnmatch
import re
import os, sys

__author__ = 'Amir Ronen'

def selLocalCns(filter=False, *args):
    constraints = pm.ls(type='constraints')
    if not filter:
        pm.select(constraints)
        return
    selList = []
    for obj in constraints:
        if not ":" in obj:
            selList.append(obj)
    pm.select(selList)

