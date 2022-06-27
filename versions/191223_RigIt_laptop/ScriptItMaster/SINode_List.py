from maya import cmds, mel
import pymel.core as pm
import SINode_Base as SIBase


class SIList:
    _head = ''
    _tail = ''
    _listLen = 0

    def __init__(self, obj):
        if issubclass(obj.__class__, SIBase.SIBase):
            self._head = obj
            self._tail = obj
            obj._idx = 0
            self._listLen = 1

    def addEnd(self, obj):
        if not self._head:
            return
        self._head._next = obj
        self._head = obj
        obj._idx = self._listLen
        self._listLen += 1

    def addStart(self, obj):
        if not self._tail:
            return
        self._tail._prev = obj
        self._tail = obj
        obj._idx = 0
        self._listLen += 1
        self.incrementAllNextIdx(obj._next)

    def addAtIdx(self, obj, idx):
        temp = self._tail
        i = 0
        if i <= idx:
            while i < idx:
                if temp.hasNext():
                    temp = temp.getNext()
                else:
                    print()
                    return
            prev = temp.getPrev()
            obj.setNext(temp)
            obj.setPrev(prev)
            obj.setIdx = idx
            self.incrementAllNextIdx(temp)


    def incrementAllNextIdx(self, obj):
        while obj.hasNext():
            obj.setIdx(1, add=True)
            obj = obj.getNext

