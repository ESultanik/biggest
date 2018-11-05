import os
import sys

def _print_single(obj, stdout, stderr, parent_indents, last, parent):
    for indent in parent_indents[:-1]:
        if indent:
            stderr.write('│   ')
        else:
            stderr.write('    ')
    if parent_indents:
        if last:
            sys.stderr.write('└── ')
        else:
            sys.stderr.write('├── ')
    sys.stderr.write(f"[{obj.size}] ")
    sys.stderr.flush()
    path = obj.path
    if parent is not None:
        path = os.path.relpath(path, start=parent.path)
        basepath = obj.path[:-len(path)]
    else:
        basepath = ''
    sys.stdout.write(f"{basepath}")
    sys.stdout.flush()
    sys.stderr.write('\x1B[1D \x1B[1D' * len(basepath))
    sys.stderr.flush()
    sys.stdout.write(f"{path}\n")
    sys.stdout.flush()    

def _print_tree(directory, stdout, stderr, parent_indents=(), last=False, parent=None):
    _print_single(directory, stdout, stderr, parent_indents, last, parent)
    for i, child in enumerate(directory.children):
        last_child = i == len(directory.children) - 1
        _print_tree(child, stdout, stderr, parent_indents + ([True,False][last],), last=last_child, parent=directory)

def print_tree(directory, stdout=sys.stdout, stderr=sys.stderr):
    _print_tree(directory, stdout, stderr)

if __name__ == '__main__':
    import biggest

    for path in sys.argv[1:]:
        print_tree(biggest.Directory(path, num_biggest=20))
