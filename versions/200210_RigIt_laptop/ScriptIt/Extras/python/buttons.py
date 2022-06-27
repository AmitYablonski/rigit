class HeadTailList:
    _head = ''
    _tail = ''
    _listLen = 0

    def __init__(self, obj):
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
        sel