Formic: Apache Ant FileSet and Globs in Python
==============================================

.. image::
  https://img.shields.io/pypi/v/formic2.svg
  :target: https://pypi.python.org/pypi/formic2
  :alt: Last stable version (PyPI)

.. image::
  https://readthedocs.org/projects/formic/badge/?version=latest
  :target: https://formic.readthedocs.io/
  :alt: ReadTheDocs

History
-------

Formic is forked from https://bitbucket.org/aviser/formic. The original project only supports python2.7 and has not been maintained for a long time.

I added Python3 supports and fixed some issues.
Formic now can work on any Python 2.6+ or Python 3.4+ system. If not, please `file an issue <https://github.com/wolfhong/formic/issues/new>`_. Yet not tested on other Python version.

Formic has no runtime dependencies outside the Python system libraries.

Install
--------

Formic can be installed from the Cheeseshop with easy_install::

   $ easy_install formic2

Or pip::

   $ pip install formic2

Quickstart
----------

Once installed, you can use Formic either from the command line to find from the current directory::

   $ formic -i "*.py" -e "__init__.py" "**/*test*/" "test_*"

This will search for files all Python files under the current directory
excluding all `__init__.py` files, any file in directories whose name contains
the word 'test', and any files that start `test_`.

You can also find from the specified directory like below::

   $ formic /specified/directory/can/ignore/ -i "*.py" "**/test/**/*.txt" "*.ini"

Output from Formic is formatted like the Unix find command, and so can easily be combined with other executables, eg::

    $ formic -i "**/*.bak" | xargs rm

will delete all `.bak` files in or under the current directory (but excluding VCS directories such as `.svn` and `.hg`).

Formic can also be integrated right into your Python project:

.. code-block:: python

    import formic
    fileset = formic.FileSet(include="**.py",
                             exclude=["**/*test*/**", "test_*"],
                             directory="./",
                             symlinks=False, )

    for file_name in fileset:
        # Do something with file_name
        ...

Formic is always case-insensitive on NT, but can be either case-sensitive or case-insensitive on POSIX.

On NT:

.. code-block:: console

    $ formic ./test/ -i "upp*" "upp*/"
    /some/where/formic/test/lower/UPPER.txt
    /some/where/formic/test/UPPER/lower.txt
    /some/where/formic/test/UPPER/UPPER.txt

On POSIX with case-insensitive:

.. code-block:: console

    $ formic ./test/ --insensitive -i "upp*" "upp*/"
    /some/where/formic/test/lower/UPPER.txt
    /some/where/formic/test/UPPER/lower.txt
    /some/where/formic/test/UPPER/UPPER.txt

with case-sensitive::

    $ formic ./test/ -i "upp*" "upp*/"
    $


That's about it :)

Features
--------

Formic is a Python implementation of Apache Ant `FileSet and Globs
<http://ant.apache.org/manual/dirtasks.html#patterns>`_ including the directory wildcard `**`.

FileSet provides a terse way of specifying a set of files without having to enumerate individual files. It:

1. **Includes** files from one or more Ant Globs, then
2. Optionally **excludes** files matching further Ant Globs.

Ant Globs are a superset of ordinary file system globs. The key differences:

* They match whole paths, eg ``/root/myapp/*.py``
* \*\* matches *any* directory or *directories*, eg ``/root/**/*.py`` matches
  ``/root/one/two/my.py``
* You can match the topmost directory or directories, eg ``/root/**``, or
* The parent directory of the file, eg ``**/parent/*.py``, or
* Any parent directory, eg ``**/test/**/*.py``

This approach is the de-facto standard in several other languages and tools,
including Apache Ant and Maven, Ruby (Dir) and Perforce (...).

Python has built-in support for simple globs in `fnmatcher
<http://docs.python.org/library/fnmatch.html>`_ and `glob
<http://docs.python.org/library/glob.html>`_, but Formic:

* Can recursively scan subdirectories
* Matches arbitrary directories *in* the path (eg ``/1/**/2/**/3/**/*.py``).
* Has a high level interface:

  * Specify one or more globs to find files
  * Globs can be used to exclude files
  * Ant, and Formic, has a set of *default excludes*. These are files and
    directories that, by default, are automatically excluded from all searches.
    The majority of these are files and directories related to VCS (eg .svn
    directories). Formic adds ``__pycache__``.
  * Iterate through all matches in the sub-tree

* Is more efficient with many common patterns; it runs relatively faster on large directory trees with large numbers of files.

About
-----

Formic is originally written and maintained by `Andrew Alcock <mailto:formic@aviser.asia>`_ of `Aviser LLP <http://www.aviser.asia>`_, Singapore.

But now, I forked it on GitHub and will maintain this project voluntarily for a long time.

* `Origin Homepage <http://www.aviser.asia/formic>`_
* `Current Issue tracker <https://github.com/wolfhong/formic/issues?status=new&status=open>`_
* `Current Source <https://github.com/wolfhong/formic>`_ on GitHub
* `PyPI <https://pypi.python.org/pypi/formic2>`_
* `ReadTheDocs <https://formic.readthedocs.io/>`_
