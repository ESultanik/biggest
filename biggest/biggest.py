import os

class Directory(object):
    def __init__(self, path, parent=None, num_biggest=None):
        self._path = path
        self._size = None
        self._children = None
        self._parent = parent
        self._num_biggest = num_biggest

    @property
    def parent(self):
        return self._parent

    @property
    def path(self):
        return self._path

    @property
    def children(self):
        if self._children is None:
            self._children = []
            for child in os.scandir(self.path):
                if child.is_dir(follow_symlinks=False):
                    self._children.append(Directory(child.path))
                else:
                    self._children.append(File(child.path))
        return self._children

    @property
    def size(self):
        if self._size is None:
            self._size = sum(child.size for child in self.children)
        return self._size

    def __str__(self):
        return self.path

    __repr__ = __str__

class File(object):
    def __init__(self, path):
        self._path = path
        self._size = None

    @property
    def path(self):
        return self._path

    @property
    def size(self):
        if self._size is None:
            self._size = os.stat(path, follow_symlinks=False).st_size
        return self._size

    def __str__(self):
        return self.path

    __repr__ = __str__

if __name__ == '__main__':
    import sys
    for path in sys.argv[1:]:
        print((path, Directory(path).size))
