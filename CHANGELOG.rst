Changelog
=========

0.9beta8
--------

New feature:

* Added the ability to pass in the function that walks the directory path,
  which allows for alternate implementations or supplying a mock function that
  provides values completely unrelated to the OS. This is available only from
  the API and not from the command line::

      files = ["CVS/error.py", "silly/silly1.txt", "1/2/3.py", "silly/silly3.txt", "1/2/4.py", "silly/silly3.txt"]
      for dir, file in FileSet(include="*.py", walk=walk_from_list(files)):
          print dir, file

Bug fixes:

* Fixed #10: Paths like "//network/dir" caused an infinite loop
* Fixed #11: Incorrect handling of globs ending "/**" and "/".
  Ant Glob semantics for::

      **/test/**

  are that they should match "all files that have a test element in their path,
  including test as a filename."

0.9beta7
--------

Bug fixes:

* Fixed #4 and #6: Handles mixed case correctly on Windows
* Fixed #8: Formic fails if it starts directory traversal at any drive's root
  directory on Windows
* Fixed #5: Formic had an unnecessary dependency on pkg_resources

Improvements:

* Fixed performance defect #7: Much faster searching for globs like "/a/b/**"
* Improved quickstart documentation: Explicitly mention that Formic searches
  from the *current* directory.


0.9beta6
--------

* Fixed issue #2: VERSION.txt was not being correctly packaged causing problems
  with source and pip installation
* Fixed issue #3: Incorrect behaviour when absolute directory was "/"
* Removed Google Analytics from documentation, and improved documentation template
* Improved publishing process.

0.9beta5
--------

This is a documentation and SCM release. No API changes.

* Updated documentation, changelogs and installation instructions
* Removed Google Analytics from Sphinx documentation
* Implemented `Dovetail <http://www.aviser.asia/dovetail>`_ build
  * Added coverage, pylint and sloccount metrics generation
  * Added command-line sanity tests

0.9beta4
--------

* Fixed issue `#1 <https://bitbucket.org/aviser/formic/issue/1/an-include-like-py-does-not-match-files>`_:
  In `3de0331450c0 <https://bitbucket.org/aviser/formic/changeset/3de0331450c0>`_

0.9beta3
--------

* API: FileSet is now a natural iterator::

    fs = FileSet(include="*.py")
    filenames = [ filename for filename in fs ]

* API: ``__str__()`` on Pattern and FileSet has been improved. Pattern now
  returns the just normalized string for the pattern (eg ``**/*.py``). FileSet
  now returns the details of the set include all the include and exclude
  patterns.

* Setup: Refactored setup.py and configuration to use only setuptools (removing
  distribute and setuptools_hg)

* Documentation: Renamed all ReStructured Text files to .rst. Small
  improvements to installation instructions.


0.9beta2
--------

* Refactored documentation files and locations to be more DRY:

  * Sphinx documentation
  * setup.py/Pypi readme
  * README/INSTALL/CHANGELOG/USAGE in topmost directory

* Removed the file-based distribute depending on explicit dependency
  in setup.py

0.9beta
-------

Date: 14 Apr 2011
First public release