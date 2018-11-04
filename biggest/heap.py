import heapq

class MutableHeapElement(object):
    def __init__(self, element, key=None, removed=False):
        self.element = element
        self.removed = removed
        if key is None:
            self.key = self.element
        else:
            self.key = key

    def __lt__(self, other):
        return self.key < other.key

class MutableHeap(object):
    def __init__(self, elements=None):
        self._elements = {}
        if elements is None:
            self._heap = []
        else:
            self._heap = list(MutableHeapElement(element) for element in elements)
            for e in self._heap:
                if e.element in self._elements:
                    self._elements[e.element].append(e)
                else:
                    self._elements[e.element] = [e]
        heapq.heapify(self._heap)

    def remove(self, element):
        if element in self._elements:
            for e in self._elements[element]:
                e.removed = True
            del self._elements[element]
            self._clear_removed()
            return True
        else:
            return False

    def _clear_removed(self):
        while self._heap and self._heap[0].removed:
            heapq.heappop(self._heap)

    def __len__(self):
        return sum(1 for e in self._heap if not e.removed)

    def __bool__(self):
        return bool(self._heap)

    def __contains__(self, element):
        return element in self._elements and sum(map(lambda e : not e.removed, self._elements[element]))

    def peek(self):
        if not self._heap:
            raise LookupError('The heap is empty')
        return self._heap[0].element

    def peek_value(self):
        if not self._heap:
            raise LookupError('The heap is empty')
        return self._heap[0].key

    def __getitem__(self, element):
        for e in sorted(self._elements[element]):
            if not e.removed:
                return e.key

    def pop(self):
        while self._heap:
            ret = heapq.heappop(self._heap)
            if not ret.removed:
                self._clear_removed()
                self._elements[ret.element].remove(ret)
                if not self._elements[ret.element]:
                    del self._elements[ret.element]
                return ret.element
        raise LookupError('The heap is empty')

    def push(self, element, value=None):
        e = MutableHeapElement(element, key=value)
        if element in self._elements:
            self._elements[element].append(e)
        else:
            self._elements[element] = [e]
        heapq.heappush(self._heap, e)

if __name__ == '__main__':
    import random
    to_remove = frozenset(random.randint(0, 99) for i in range(20))
    print(f"Removed: {', '.join(map(str, sorted(to_remove)))}")
    h = MutableHeap()
    for i in reversed(range(100)):
        h.push(i)
    for i in to_remove:
        assert h.remove(i)
    results = []
    while h:
        results.append(h.pop())
    print(f"Result: {', '.join(map(str, results))}")
    h = MutableHeap([1, 2, 3])
    h.remove(2)
    h.push(2)
    assert h.pop() == 1
    assert h.pop() == 2
    assert h.pop() == 3
    assert not h
    
