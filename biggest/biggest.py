import heapq
import os

class File(object):
    def __init__(self, path):
        self._path = path
        self._size = None

    def __lt__(self, other):
        return (self.size < other.size) or (self.size == other.size and self.path < other.path)
        
    @property
    def path(self):
        return self._path

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
        self._path = path
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
                ret = File(child.path)
            if self._size is None:
                to_yield.append(ret)
            else:
                yield ret
        if self._size is None:
            self._size = sum(child.size for child in to_yield)
            for child in to_yield:
                yield child

    def biggest(self, n, include_self=False):
        ret = []
        size = 0
        children = set()
        for child in self._get_children():
            children.add(child)
            if isinstance(child, File):
                heapq.heappush(ret, (-child.size, child))
                size += child.size
            else:
                for descendant in child.biggest(n, include_self=True):
                    heapq.heappush(ret, (-descendant.size, descendant))
        num_to_yield = min(len(ret), n)
        for i in range(num_to_yield):
            _, element = heapq.heappop(ret)
            if element in children:
                # don't include the sizes of direct children we've yielded
                size -= element.size
            if include_self and i == num_to_yield - 1 and size > element.size:
                # we've already yielded all of our children and we are still bigger, so yield ourselves
                yield self
            else:
                yield element

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
