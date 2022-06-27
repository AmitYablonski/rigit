from maya import cmds, mel
import pymel.core as pm
from functools import partial
import RigItWinBase as winBase

reload(winBase)


class WinTest():
    def __init__(self, makeWin=True):
        self.widgets = {}
        topLay = winBase.winBase(self, 'testWin', 'Test Win')
        print ' // topLay :'# %s' % self.widgets['topLay']
