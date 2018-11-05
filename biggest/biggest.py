import heapq
import os

from heap import MutableHeap

class FilesystemObject(object):
    def __init__(self, path, parent=None):
        self._path = path
        self._parent = parent
        self._name = os.path.basename(path)

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return self.path == other.path

    def __lt__(self, other):
        return (self.size > other.size) or (self.size == other.size and self.path < other.path)

    def __le__(self, other):
        return (self.size >= other.size) or (self.size == other.size and self.path <= other.path)
    
    def __str__(self):
        return self.path

    __repr__ = __str__        

class _ModifiedSize(FilesystemObject):
    def __init__(self, original, size):
        super().__init__(original.path)
        while isinstance(original, _ModifiedSize):
            original = original.original
        self.original = original
        self.size = size

class File(FilesystemObject):
    def __init__(self, path, parent=None):
        super().__init__(path, parent=parent)
        self._size = None

    @property
    def size(self):
        if self._size is None:
            self._size = os.stat(self.path, follow_symlinks=False).st_size
        return self._size
    
class Directory(FilesystemObject):
    def __init__(self, path, parent=None, num_biggest=None):
        if path.endswith('/'):
            path = path[:-1]
        super().__init__(path, parent=parent)
        self._size = None
        self._children = None
        self._num_biggest = num_biggest
        self._all_children = None

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
            self._size = sum(child.size for child in to_yield if isinstance(child, File))
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
        biggest_directories = MutableHeap(d for d in biggest_directories)
        ret = []
        returned_dirs = {}
        while len(ret) < n and (biggest_files or biggest_directories):
            if not biggest_directories or (biggest_files and biggest_directories.peek() >= biggest_files[0]):
                ret.append(biggest_files[0])
                if biggest_files[0].parent in biggest_directories:
                    value = biggest_directories[biggest_files[0].parent]
                    biggest_directories.remove(biggest_files[0].parent)
                    biggest_directories.push(biggest_files[0].parent, value=_ModifiedSize(value, value.size - biggest_files[0].size))
                elif biggest_files[0].parent is not None and biggest_files[0].parent.path in returned_dirs:
                    # we already returned this directory, but its size should decrease now that this file was added
                    parent_dir = returned_dirs[biggest_files[0].parent.path]
                    del returned_dirs[biggest_files[0].parent.path]
                    for i in range(len(ret)):
                        if ret[i].path == parent_dir.path:
                            del ret[i]
                            break
                    biggest_directories.push(biggest_files[0].parent, value=_ModifiedSize(parent_dir, parent_dir.size - biggest_files[0].size))
                biggest_files = biggest_files[1:]
            else:
                retdir = biggest_directories.pop()
                returned_dirs[retdir.path] = retdir
                if isinstance(retdir, _ModifiedSize):
                    retdir = retdir.original
                ret.append(retdir)
        return sorted(ret)

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

if __name__ == '__main__':
    import sys
    for path in sys.argv[1:]:
        for child in Directory(path, num_biggest=20).children:
            print(f"{child.size}\t{child.path}")
