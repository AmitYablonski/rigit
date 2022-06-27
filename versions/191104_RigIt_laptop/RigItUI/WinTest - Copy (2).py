from maya import cmds, mel
import pymel.core as pm
from functools import partial
import RigItWinBase as winBase

reload(winBase)


class WinTest(winBase):
    def __init__(self, *args):  # , makeWin=True):
        winBase.__init__('Test Win')
        print ' // topLay :'# %s' % self.widgets['topLay']
