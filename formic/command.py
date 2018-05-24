###############################################################################
# Formic: An implementation of Apache Ant FileSet globs
# Copyright (C) 2012, Aviser LLP, Singapore.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
"""The command-line glue-code for :command:`formic`. Call :func:`formic.command.main()`
with the command-line arguments.

Full usage of the command is::

  usage: formic [-i [INCLUDE [INCLUDE ...]]] [-e [EXCLUDE [EXCLUDE ...]]]
               [--no-default-excludes] [--no-symlinks] [--insensitive] [-r] [-h] [--usage]
               [--version]
               [directory]
"""

from argparse import ArgumentParser, SUPPRESS, RawDescriptionHelpFormatter
import sys
import os
from pkg_resources import resource_string

if __name__ == "__main__":
    from formic import FileSet, FormicError, get_version
else:
    from .formic import FileSet, FormicError, get_version

DESCRIPTION = """Search the file system using Apache Ant globs"""

EPILOG = \
"""For documentation, source code and other information, please visit:
https://github.com/wolfhong/formic

This program comes with ABSOLUTELY NO WARRANTY. See license for details.

This is free software, and you are welcome to redistribute it
under certain conditions; for details, run
> formic --license

Formic is Copyright (C) 2012, Aviser LLP, Singapore"""


def create_parser():
    """Creates and returns the command line parser, an
     :class:`argparser.ArgumentParser` instance."""
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG,
        add_help=False)

    directory = parser.add_argument_group("Directory")
    directory.add_argument(
        dest='directory',
        action="store",
        default=None,
        nargs="?",
        help="The directory from which to start the search "
        "(defaults to current working directory)")

    globs = parser.add_argument_group("Globs")
    globs.add_argument(
        '-i',
        '--include',
        action="store",
        nargs="*",
        help="One or more Ant-like globs in include in the search."
        "If not specified, then all files are implied")
    globs.add_argument(
        '-e',
        '--exclude',
        action="store",
        nargs="*",
        help="One or more Ant-like globs in include in the search")
    globs.add_argument(
        '--no-default-excludes',
        dest="default_excludes",
        action="store_false",
        default=True,
        help="Do not include the default excludes")
    globs.add_argument(
        '--no-symlinks',
        action="store_true",
        default=False,
        help="Do not include symlinks")
    globs.add_argument(
        '--insensitive',
        action="store_true",
        default=False,
        help="Turn off case-sensitive, default sensitive on POSIX, always insensitive on NT.")

    output = parser.add_argument_group("Output")
    output.add_argument(
        '-r',
        '--relative',
        action="store_true",
        default=False,
        help="Print file paths relative to directory.")

    info = parser.add_argument_group("Information")
    info.add_argument(
        '-h',
        '--help',
        action='store_true',
        default=False,
        help="Prints this help and exits")
    info.add_argument(
        '--usage',
        action='store_true',
        default=False,
        help="Prints additional help on globs and exits")
    info.add_argument(
        '--version',
        action='store_true',
        default=False,
        help="Prints the version of formic and exits")
    info.add_argument('--license', action="store_true", help=SUPPRESS)
    return parser


def main(*kw):
    """Command line entry point; arguments must match those defined in
    in :meth:`create_parser()`; returns 0 for success, else 1.

    Example::

      command.main("-i", "**/*.py", "--no-default-excludes")

    Runs formic printing out all .py files in the current working directory
    and its children to ``sys.stdout``.

    If *kw* is None, :func:`main()` will use ``sys.argv``."""
    parser = create_parser()

    args = parser.parse_args(kw if kw else None)
    if args.help:
        parser.print_help()
    elif args.usage:
        print("""Ant Globs
=========

Apache Ant fileset is documented at the Apache Ant project:

* http://ant.apache.org/manual/dirtasks.html#patterns

Examples
--------

Ant Globs are like simple file globs (they use ? and * in the same way), but
include powerful ways for selecting directories. The examples below use the
Ant glob naming, so a leading slash represents the top of the search, *not* the
root of the file system.

    *.py
            Selects every matching file anywhere in the whole tree
                Matches /foo.py and /bar/foo.py
                but not /foo.pyc or /bar/foo.pyc/

    /*.py
            Selects every matching file in the root of the directory (but no
            deeper).

            Matches /foo.py but not /bar/foo.py

    /myapp/**
            Matches all files under /myapp and below.

    /myapp/**/__init__.py
            Matches all __init__.py files /myapp and below.

    dir1/__init__.py
            Selects every __init__.py in directory dir1. dir1
            directory can be anywhere in the directory tree

            Matches /dir1/file.py, /dir3/dir1/file.py and
            /dir3/dir2/dir1/file.py but not /dir1/another/__init__.py.

    **/dir1/__init__.py
            Same as above.

    /**/dir1/__init__.py
            Same as above.

    /myapp/**/dir1/__init__.py
            Selects every __init__.py in dir1 in the directory tree
            /myapp under the root.

            Matches /myapp/dir1/__init__.py and /myapp/dir2/dir1/__init__.py
            but not /myapp/file.txt and /dir1/file.txt

Default excludes
----------------

Ant FileSet (and Formic) has built-in patterns to screen out a lot of
development 'noise', such as hidden VCS files and directories. The full list is
at:

    * https://formic.readthedocs.io/en/latest/api.html#formic.formic.get_initial_default_excludes

Default excludes can be simply switched off on both the command line and the
API, for example::

    $ formic -i "*.py" -e "__init__.py" "**/*test*/" "test_*" --no-default-excludes
""")
    elif args.version:
        print("formic", get_version())
    elif args.license:
        print(resource_string(__name__, "LICENSE.txt"))
    else:
        try:
            fileset = FileSet(
                directory=args.directory,
                include=args.include if args.include else ["*"],
                exclude=args.exclude,
                default_excludes=args.default_excludes,
                symlinks=not args.no_symlinks,
                casesensitive=not args.insensitive)
        except FormicError as exception:
            parser.print_usage()
            print(exception.message)
            return 1

        prefix = fileset.get_directory()
        for directory, file_name in fileset.files():
            if args.relative:
                sys.stdout.write(".")
            else:
                sys.stdout.write(prefix)
            if directory:
                sys.stdout.write(os.path.sep)
                sys.stdout.write(directory)
            sys.stdout.write(os.path.sep)
            sys.stdout.write(file_name)
            sys.stdout.write("\n")

    return 0


def entry_point():
    """Entry point for command line; calls :meth:`formic.command.main()` and then
    :func:`sys.exit()` with the return value."""
    result = main()
    exit(result)


if __name__ == "__main__":
    main(*sys.argv[1:])
