import argparse
import sys

import biggest
import tree

def main(argv = None):
    parser = argparse.ArgumentParser(description='A utility for finding the largest files and directories', add_help=False)
    parser.add_argument('directory', type=str, help='Path to the directory to analyze')
    parser.add_argument('-n', type=int, default=10, help='The maximum number of largest files and directories to find (default=10)')
    parser.add_argument('--only-files', '-f', action='store_true', help='Ignore directories and only find the largest files')
    parser.add_argument('--human-readable', '-h', action='store_true', help='Print file sizes with human-readable unit suffixes like "MB" and "GB"')
    parser.add_argument('--help', action='help', help='show this help message and exit')

    if argv is None:
        argv = sys.argv
    
    args = parser.parse_args(argv[1:])

    tree.print_tree(biggest.Directory(args.directory, num_biggest=args.n, include_directories=not args.only_files), human_readable=args.human_readable)

if __name__ == '__main__':
    main()
