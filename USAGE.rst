Usage
=====

Command Line
------------

The formic command provides shell access to Ant glob functionality. Some
examples are shown below.

Find all Python files under ``myapp``::

    $ formic myapp -i "*.py"

(Note that if a root directory is specified, it must come before the -i or -e)

Find all Python files under the current directory, but exclude ``__init__.py``
files::

    $ formic -i "*.py" -e "__init__.py"

... and further refined by removing test directories and files::

    $ formic -i "*.py" -e "__init__.py" "**/*test*/" "test_*"

This will search for files all Python files under the current directory
excluding all `__init__.py` files, any file in directories whose name contains
the word 'test', and any files that start `test_`.

Output from Formic is formatted like the Unix find command, and so can easily
be combined with other executables, eg::

    $ formic -i "**/*.bak" | xargs rm

... will delete all ``.bak`` files in or under the current directory (but excluding
VCS directories such as ``.svn`` and ``.hg``).

Full usage is documented in the `formic.command
<http://www.aviser.asia/formic/doc/api.html#module-formic.command>`_ package.

Library
-------

The API provides the same functionality as the command-line but in a form
more readily consumed by applications which need to gather collections of files
efficiently.

The API is quite simple for normal use. The example below will gather all the
Python files in and under the current working directory, but exclude all
directories which contain 'test' in their name, and all files whose name
starts with 'test\_'::

    import formic
    fileset = formic.FileSet(include="**.py",
                             exclude=["**/*test*/**", "test_*"]
                             )

    for file_name in fileset:
        # Do something with file_name
        ...

A more detailed description can be found in the `API <http://www.aviser.asia/formic/doc/api.html>`_.