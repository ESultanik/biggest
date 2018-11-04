import heapq
import os

class File(object):
    def __init__(self, path, parent=None):
        self._path = path
        self._name = os.path.basename(path)
        self._size = None
        self._parent = parent

    def __lt__(self, other):
        return (self.size > other.size) or (self.size == other.size and self.path < other.path)
        
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
        return (self.size > other.size) or (self.size == other.size and self.path < other.path)

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

    def _biggest(self, n, include_directories=True):
        files = []
        size = 0
        directories = []
        for child in self._get_children():
            if isinstance(child, File):
                heapq.heappush(files, (-child.size, child.path, child))
                size += child.size
            else:
                child_files, child_dirs = child._biggest(n)
                for descendant in child_files:
                    heapq.heappush(files, (-descendant.size, descendant.path, descendant))
                if include_directories:
                    directories.append(child)
                    directories += child_dirs
        num_files = min(len(files), n)
        biggest_files = list(heapq.heappop(files)[2] for i in range(num_files))
        if include_directories:
            if biggest_files:
                biggest_directories = list(d for d in directories if d.size >= biggest_files[-1].size)
            else:
                biggest_directories = directories
        else:
            biggest_directories = ()
        return biggest_files, biggest_directories

    def biggest(self, n, include_directories=True):
        biggest_files, biggest_directories = self._biggest(n, include_directories=include_directories)
        return biggest_files + biggest_directories

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
