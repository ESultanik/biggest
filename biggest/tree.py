import os
import sys

from colorama import Fore, Back, Style, init
init()

from .biggest import Directory

def human_readable_size(num_bytes):
    if num_bytes >= 1024**4:
        return str(int(num_bytes / 1024**4 + 0.5)) + ' TB'
    elif num_bytes >= 1024**3:
        return str(int(num_bytes / 1024**3 + 0.5)) + ' GB'
    elif num_bytes >= 1024**2:
        return str(int(num_bytes / 1024**2 + 0.5)) + ' MB'
    elif num_bytes >= 1024:
        return str(int(num_bytes / 1024 + 0.5)) + ' KB'
    else:
        return str(num_bytes) + ' B'

def _print_single(obj, stdout, stderr, parent_indents, last, parent, human_readable):
    stderr.write(Style.RESET_ALL)
    stderr.write(Style.DIM)
    for indent in parent_indents[:-1]:
        if indent:
            stderr.write('│   ')
        else:
            stderr.write('    ')
    if parent_indents:
        if last:
            stderr.write('└── ')
        else:
            stderr.write('├── ')
    size = obj.total_size
    if human_readable:
        size = human_readable_size(size)
    stderr.write(f"{Style.NORMAL}{Fore.WHITE}[{Fore.RED}{size}{Fore.WHITE}]{Style.RESET_ALL} ")
    stderr.flush()
    path = obj.path
    if parent is not None:
        path = os.path.relpath(path, start=parent.path)
        basepath = obj.path[:-len(path)]
    else:
        basepath = ''
    if obj.selected:
        stderr.write(Style.BRIGHT)
        out_stream = stdout
    else:
        stderr.write(Style.DIM)
        out_stream = stderr
    if isinstance(obj, Directory):
        stderr.write(Fore.BLUE)
    else:
        stderr.write(Fore.WHITE)
    stderr.flush()
    out_stream.write(f"{basepath}")
    out_stream.flush()
    stderr.write('\x1B[1D \x1B[1D' * len(basepath))
    stderr.flush()
    out_stream.write(f"{path}\n")
    out_stream.flush()    

def _print_tree(directory, stdout, stderr, parent_indents=(), last=False, parent=None, human_readable=False):
    _print_single(directory, stdout, stderr, parent_indents, last, parent, human_readable=human_readable)
    if last and parent_indents:
        parent_indents = parent_indents[:-1] + (False,)
    children = directory.children
    for i, child in enumerate(children):
        last_child = i == len(children) - 1
        _print_tree(child, stdout, stderr, parent_indents + (not last_child,), last=last_child, parent=directory, human_readable=human_readable)
    stderr.write(Style.RESET_ALL)

def print_tree(directory, stdout=sys.stdout, stderr=sys.stderr, human_readable=False):
    _print_tree(directory, stdout, stderr, human_readable=human_readable)

if __name__ == '__main__':
    import biggest

    for path in sys.argv[1:]:
        print_tree(biggest.Directory(path, num_biggest=20), human_readable=True)
