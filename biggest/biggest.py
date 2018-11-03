import heapq
import os

class File(object):
    def __init__(self, path, parent=None):
        self._path = path
        self._name = os.path.basename(path)
        self._size = None
        self._parent = parent

    def __lt__(self, other):
        return (self.size < other.size) or (self.size == other.size and self.path < other.path)
        
    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def size(self):
        if self._size is None:
            self._size = os.stat(self.path, follow_symlinks=False).st_size
        return self._size

    def __str__(self):
        return self.path

    __repr__ = __str__

class Directory(object):
    def __init__(self, path, parent=None, num_biggest=None):
        if path.endswith('/'):
            path = path[:-1]
        self._path = path
        self._name = os.path.basename(path)
        self._size = None
        self._children = None
        self._parent = parent
        self._num_biggest = num_biggest
        self._all_children = None

    def __lt__(self, other):
        return (self.size < other.size) or (self.size == other.size and self.path < other.path)
        
    @property
    def parent(self):
        return self._parent

    @property
    def path(self):
        return self._path

    def _get_children(self):
        to_yield = []
        for child in os.scandir(self.path):
            if child.is_dir(follow_symlinks=False):
                ret = Directory(child.path, parent=self, num_biggest=self._num_biggest)
            else:
                ret = File(child.path, parent=self)
            if self._size is None:
                to_yield.append(ret)
            else:
                yield ret
        if self._size is None:
            self._size = sum(child.size for child in to_yield)
            for child in to_yield:
                yield child

    def biggest(self, n):
        ret = []
        size = 0
        for child in self._get_children():
            if isinstance(child, File):
                heapq.heappush(ret, (-child.size, child.path, child))
                size += child.size
            else:
                child_size = child.size
                for descendant in child.biggest(n):
                    if descendant.parent == child:
                        child_size -= descendant.size
                    heapq.heappush(ret, (-descendant.size, descendant.path, descendant))
                heapq.heappush(ret, (-child_size, child.path, child))
        num_to_yield = min(len(ret), n)
        for i in range(num_to_yield):
            yield heapq.heappop(ret)[2]

    @property
    def children(self):
        if self._children is None:
            if self._num_biggest is None:
                self._children = tuple(self._get_children())
            else:
                self._children = tuple(self.biggest(self._num_biggest))
        return self._children

    @property
    def size(self):
        if self._size is None:
            # self._size is set when we enumerate our children
            tuple(self._get_children())
        return self._size
    
    def __str__(self):
        return self.path

    __repr__ = __str__

if __name__ == '__main__':
    import sys
    for path in sys.argv[1:]:
        for child in Directory(path, num_biggest=20).children:
            print(f"{child.size}\t{child.path}")
