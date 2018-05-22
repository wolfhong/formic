Installing Formic
=================

Prequisites
-----------

Platform and dependencies:

* Formic requires Python 2.7
* It has been tested on

  * Mac OS X (Lion and Mountain Lion)
  * Ubuntu 11.10 and 12.04LTS
  * Windows XP and Windows 7 (Home Premium).

Formic should work on any Python 2.7 system; if not, please contact the
maintainer or `file an issue
<https://bitbucket.org/aviser/formic/issues/new>`_.

Formic has no runtime dependencies outside the Python system libraries.

Installation options
--------------------

There are three ways to obtain Formic shown below, in increasing difficulty
and complexity. You need only pick one:

**Option 1: Automated install**

Simplest: use::

    $ easy_install formic

or::

    $ pip install formic

**Option 2: Source install**

1. Download the appropriate package from Formics page on the `Python
   Package Index <http://pypi.python.org/pypi/formic>`_. This is a GZipped TAR
   file.
2. Extract the package using your preferred GZip utility.
3. Navigate into the extracted directory and perform the installation::

    $ python setup.py install

**Option 3: Check out the project**

If you like, you could download the source and compile it yourself. The
source is on a Mercurial DVCS at `Atlassian BitBucket
<https://bitbucket.org/aviser/formic.>`_. BitBucket provides several different
approaches for download on the site, the simplest being::

    $ hg clone https://bitbucket.org/aviser/formic

.. note:: To build, Formic requires setuptools. We strongly recommend building
          in a virtual environment using virtualenv.

After checking out the source, navigate to the top level directory and build::

    $ python setup.py install

Validating the installation
---------------------------

After installing, you should be able to execute Formic from the command line::

    $ formic --version
    formic xxxx http://www.aviser.asia/formic

(xxxx will be the version of Formic that you downloaded and installed)

If you downloaded the source, you can additionally run the unit tests. This
requires py.test::

    $ easy_install pytest
    $ cd formic
    $ py.test
    ========================== test session starts ==========================
    platform darwin -- Python 2.7.1 -- pytest-2.2.3
    collected 40 items

    test_formic.py ........................................

    ======================= 40 passed in 2.55 seconds =======================

Compiling the documentation
---------------------------

Formic uses `Sphinx <http://sphinx.pocoo.org/>`_ for documentation. The source
files are in the 'doc' subdirectory. To build the documentation,

1. Ensure that formic has been installed and is visible on the path so you can
   start Python and import formic, eg::

    $ cd /anywhere/on/filesystem
    $ python
    Python 2.7.1 (r271:86832, Jul 31 2011, 19:30:53)
    [GCC 4.2.1 (Based on Apple Inc. build 5658) (LLVM build 2335.15.00)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import formic
    >>> exit()
    $

2. Navigate to Formic's top level directory, then::

    $ sphinx-build doc htmlout

The documentation will be in the ./htmlout subdirectory.

.. note:: Only HTML generation has been tested.

.. note:: If you get errors that Sphinx cannot import Formic's packages, you
          may not have installed the module correctly. Try reinstalling it,
          eg 'python setup.py develop' or 'python setup.py install'
