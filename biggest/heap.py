import heapq

class MutableHeap(object):
    def __init__(self, elements=None):
        self._removed = set()
        if elements is None:
            self._heap = []
        else:
            self._heap = list(elements)
        heapq.heapify(self._heap)

    def remove(self, element):
        self._removed.add(element)
        self._clear_removed()

    def _clear_removed(self):
        while self._heap and self._heap[0] in self._removed:
            heapq.heappop(self._heap)

    def __len__(self):
        return sum(1 for e in self._heap if e not in self._removed)

    def __bool__(self):
        return bool(self._heap)

    def __contains__(self, element):
        return element in self._heap
    
    def peek(self):
        if not self._heap:
            raise LookupError('The heap is empty')
        return self._heap[0]
        
    def pop(self):
        while self._heap:
            ret = heapq.heappop(self._heap)
            if ret not in self._removed:
                self._clear_removed()
                return ret
        raise LookupError('The heap is empty')

    def push(self, element):
        heapq.heappush(self._heap, element)

if __name__ == '__main__':
    import random
    to_remove = frozenset(random.randint(0, 100) for i in range(20))
    print(f"Removed: {', '.join(map(str, sorted(to_remove)))}")
    h = MutableHeap()
    for i in reversed(range(100)):
        h.push(i)
    for i in to_remove:
        h.remove(i)
    results = []
    while h:
        results.append(h.pop())
    print(f"Result: {', '.join(map(str, results))}")
