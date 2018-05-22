Ant Globs
=========

Apache Ant fileset is documented at the Apache Ant project:

* http://ant.apache.org/manual/dirtasks.html#patterns

Examples
--------

Ant Globs are like simple file globs (they use ? and * in the same way), but
include powerful ways for selecting directories. The examples below use the
Ant glob naming, so a leading slash represents the top of the search, *not* the
root of the file system.

    ``*.py``
            Selects every matching file anywhere in the whole tree
                Matches ``/foo.py`` and ``/bar/foo.py``
                but not ``/foo.pyc`` or ``/bar/foo.pyc/``

    ``/*.py``
            Selects every matching file in the root of the directory (but no
            deeper).

            Matches ``/foo.py`` but not ``/bar/foo.py``

    ``/myapp/**``
            Matches all files under ``/myapp`` and below.

    ``/myapp/**/__init__.py``
            Matches all ``__init__.py`` files ``/myapp`` and below.

    ``dir1/__init__.py``
            Selects every ``__init__.py`` in directory ``dir1``. ``dir1``
            directory can be anywhere in the directory tree

            Matches ``/dir1/file.py``, ``/dir3/dir1/file.py`` and
            ``/dir3/dir2/dir1/file.py`` but not ``/dir1/another/__init__.py``.

    ``**/dir1/__init__.py``
            Same as above.

    ``/**/dir1/__init__.py``
            Same as above.

    ``/myapp/**/dir1/__init__.py``
            Selects every ``__init__.py`` in dir1 in the directory tree
            ``/myapp`` under the root.

            Matches ``/myapp/dir1/__init__.py`` and ``/myapp/dir2/dir1/__init__.py``
            but not ``/myapp/file.txt`` and ``/dir1/file.txt``

Default excludes
----------------

Ant FileSet (and Formic) has built-in patterns to screen out a lot of development
'noise', such as hidden VCS files and directories. The full list is at
:func:`~formic.formic.get_initial_default_excludes`.

Default excludes can be simply switched off on both the command line and the
API, for example::

    $ formic -i "*.py" -e "__init__.py" "**/*test*/" "test_*" --no-default-excludes

