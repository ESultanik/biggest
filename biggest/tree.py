import os
import sys

def _print_single(obj, stdout, stderr, parent_indents, last, parent, biggest):
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
    if obj in biggest:
        out_stream = sys.stdout
    else:
        out_stream = sys.stderr
    out_stream.write(f"{basepath}")
    out_stream.flush()
    sys.stderr.write('\x1B[1D \x1B[1D' * len(basepath))
    sys.stderr.flush()
    out_stream.write(f"{path}\n")
    out_stream.flush()    

def _print_tree(directory, stdout, stderr, parent_indents=(), last=False, parent=None, _biggest=None):
    if _biggest is None:
        _biggest = frozenset(directory.children)
    _print_single(directory, stdout, stderr, parent_indents, last, parent, biggest=_biggest)
    for i, child in enumerate(directory.children):
        last_child = i == len(directory.children) - 1
        _print_tree(child, stdout, stderr, parent_indents + ([True,False][last],), last=last_child, parent=directory, _biggest=_biggest)

def print_tree(directory, stdout=sys.stdout, stderr=sys.stderr):
    _print_tree(directory, stdout, stderr)

if __name__ == '__main__':
    import biggest

    for path in sys.argv[1:]:
        print_tree(biggest.Directory(path, num_biggest=20))
