import heapq
import os
import sys

from .heap import MutableHeap

FAILED_PATHS = set()

class FilesystemObject(object):
    def __init__(self, path, parent=None):
        self._path = path
        self._parent = parent
        self._name = os.path.basename(path)
        self._selected = False

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
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, is_selected):
        self._selected = is_selected
        if self.parent is not None:
            if self.has_selected:
                self.parent._children.add(self)
            elif self in self.parent._children:
                self.parent._children.remove(self)
            self.parent._recalculate_children()

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

    @property
    def total_size(self):
        return self.size

    @property
    def children(self):
        return ()

    @property
    def all_children(self):
        return ()

    @property
    def has_selected(self):
        return self.selected
    
class Directory(FilesystemObject):
    def __init__(self, path, parent=None, num_biggest=None, include_directories=True):
        if path.endswith('/'):
            path = path[:-1]
        super().__init__(path, parent=parent)
        self._cached_biggest = None
        self._size = None
        self._recursive_size = None
        self._children = set()
        self._num_biggest = num_biggest
        self._all_children = None
        self._include_directories = include_directories

    @property
    def has_selected(self):
        return self.selected or bool(self.children)

    @FilesystemObject.selected.setter
    def selected(self, is_selected):
        FilesystemObject.selected.fset(self, is_selected)
        self._recalculate_children()

    def _recalculate_children(self):
        if self.selected:
            self._children = set(self.all_children)
        else:
            self._children = set(c for c in self._children if c.has_selected)
        if self.parent is not None:
            if self.has_selected:
                self.parent._children.add(self)
            elif self in self.parent._children:
                self.parent._children.remove(self)
            self.parent._recalculate_children()
            assert not self.has_selected or self.parent.has_selected

    def _get_children(self):
        to_yield = []
        try:
            for child in os.scandir(self.path):
                if child.is_dir(follow_symlinks=False):
                    ret = Directory(child.path, parent=self, num_biggest=self._num_biggest)
                else:
                    ret = File(child.path, parent=self)
                if self._size is None:
                    to_yield.append(ret)
                else:
                    yield ret
        except PermissionError:
            if self.path not in FAILED_PATHS:
                FAILED_PATHS.add(self.path)
                sys.stderr.write(f"Warning: Permission denied reading {self.path}\n")
        if self._size is None:
            self._size = sum(child.size for child in to_yield if isinstance(child, File))
            self._recursive_size = sum(child.total_size for child in to_yield)
            for child in to_yield:
                yield child

    def _biggest(self, n):
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
                if self._include_directories:
                    directories.append(child)
                    directories += child_dirs
        num_files = min(len(files), n)
        biggest_files = list(heapq.heappop(files)[2] for i in range(num_files))
        if self._include_directories:
            if biggest_files:
                biggest_directories = list(d for d in directories if d.size >= biggest_files[-1].size)
            else:
                biggest_directories = directories
        else:
            biggest_directories = ()
        return biggest_files, biggest_directories

    def biggest(self, n=None):
        if n is None:
            if self._cached_biggest is None:
                if self._num_biggest is None:
                    return self._get_children()
                self._cached_biggest = self.biggest(self._num_biggest)
            return self._cached_biggest
        biggest_files, biggest_directories = self._biggest(n)
        biggest_directories = MutableHeap(d for d in biggest_directories)
        ret = []
        returned_dirs = {}
        _max_possible = len(biggest_files) + len(biggest_directories)
        while len(ret) < n and (biggest_files or biggest_directories):
            if biggest_files and (not biggest_directories or biggest_directories.peek() <= biggest_files[0]):
                biggest_file = biggest_files[0]
                ret.append(biggest_file)
                if biggest_file.parent in biggest_directories:
                    value = biggest_directories[biggest_file.parent]
                    biggest_directories.remove(biggest_file.parent)
                    biggest_directories.push(biggest_file.parent, value=_ModifiedSize(value, value.size - biggest_file.size))
                elif biggest_file.parent is not None and biggest_file.parent.path in returned_dirs:
                    # we already returned this directory, but its size should decrease now that this file was added
                    parent_dir = returned_dirs[biggest_file.parent.path]
                    del returned_dirs[biggest_file.parent.path]
                    for i in range(len(ret)):
                        if ret[i].path == parent_dir.path:
                            del ret[i]
                            break
                    biggest_directories.push(biggest_file.parent, value=_ModifiedSize(parent_dir, parent_dir.size - biggest_file.size))
                biggest_files = biggest_files[1:]
            else:
                retdir = biggest_directories.pop()
                returned_dirs[retdir.path] = retdir
                if isinstance(retdir, _ModifiedSize):
                    retdir = retdir.original
                ret.append(retdir)
        assert len(ret) == min(_max_possible, n)
        return sorted(ret)

    @property
    def children(self):
        return tuple(sorted(self._children))

    @property
    def all_children(self):
        ret = set(self.children)
        for c in self._get_children():
            if c not in ret:
                ret.add(c)
        return tuple(sorted(ret))

    @property
    def size(self):
        if self._size is None:
            # self._size is set when we enumerate our children
            tuple(self._get_children())
        return self._size

    @property
    def total_size(self):
        if self._recursive_size is None:
            # self._size is set when we enumerate our children
            tuple(self._get_children())
        return self._recursive_size
    
if __name__ == '__main__':
    for path in sys.argv[1:]:
        for child in Directory(path, num_biggest=20).children:
            print(f"{child.size}\t{child.path}")
