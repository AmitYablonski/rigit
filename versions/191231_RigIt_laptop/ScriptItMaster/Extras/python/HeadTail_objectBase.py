from maya import cmds, mel
import pymel.core as pm

class SIBase:
    _next = ''
    _prev = ''
    _script = ''
    _idx = 0

    def __init__(self):

        self.inputs = []
        self.outputs = []
        self.vectorInputs = []
        self.vectorOutputs = []

        self.widgets = {}
        self.settings()

    def settings(self):
        # todo a place where the ui will sit (like settings window that can open)
        # todo the window should have a similar base that changes (class enheritance)
        return

    def hasNext(self):
        if self._next:
            return True
        else:
            return False

    def getNext(self):
        return self._next

    def hasPrev(self):
        if self._prev:
            return True
        else:
            return False

    def getPrev(self):
        return self._prev

    def setIdx(self, idx, add=False):
        if add:
            self._idx += idx
        else:
            self._idx = idx

    #@staticmethod
    def getScript(self):
        if self._script:
            return True, self._script
        else:
            return False, ""

    def scriptIt(self, *args):
        self._script = ''
        return

