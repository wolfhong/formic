Formic: Apache Ant FileSet and Globs in Python
==============================================

Features
--------

Formic is a Python implementation of Apache Ant `FileSet and Globs
<http://ant.apache.org/manual/dirtasks.html#patterns>`_ including the directory
wildcard `**`.

FileSet provides a terse way of specifying a set of files without having to
enumerate individual files. It:

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

* Is more efficient with many common patterns; it runs relatively faster on
  large directory trees with large numbers of files.

Quickstart
----------

Formic can be installed from the Cheeseshop with easy_install or pip::

   $ easy_install formic

Once installed, you can use Formic either from the command line::

   $ formic -i "*.py" -e "__init__.py" "**/*test*/" "test_*"

This will search for files all Python files under the current directory
excluding all `__init__.py` files, any file in directories whose name contains
the word 'test', and any files that start `test_`.

Or integrated right into your Python 2.7 project::

    import formic
    fileset = formic.FileSet(include="**.py",
                             exclude=["**/*test*/**", "test_*"]
                             )

    for file_name in fileset:
        # Do something with file_name
        ...

That's about it :)

About
-----

Formic is written and maintained by `Andrew Alcock <mailto:formic@aviser.asia>`_
of `Aviser LLP <http://www.aviser.asia>`_, Singapore.

* `Home page <http://www.aviser.asia/formic>`_
* `Issue tracker <https://bitbucket.org/aviser/formic/issues?status=new&status=open>`_
* `Source <https://bitbucket.org/aviser/formic>`_ on Atlassian BitBucket
* `Email maintainer <mailto:formic@aviser.asia>`_

Formic is Copyright (C) 2012, Aviser LLP and released under
`GPLv3 <http://www.gnu.org/licenses/gpl.html>`_. Aviser LLP would be happy to
discuss other licensing arrangements; for details, please email the maintainer.
