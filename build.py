"""Formic build - uses Dovetail (available on PyPi)"""
from dovetail import *
import subprocess
import os
import sys
import re

################################################################################
# Build directory layout and language-independent app names
BUILD           = os.path.abspath(os.path.join(os.path.dirname(__file__), "build"))
BUILD_DOC       = os.path.join(BUILD, "html")
BUILD_PYLINT    = os.path.join(BUILD, "pylint", "pylint.out")
BUILD_SLOCCOUNT = os.path.join(BUILD, "sloccount", "sloccount.sc")
BUILD_PYTEST    = os.path.join(BUILD, "pytest", "junit.xml")
BUILD_COVER     = os.path.join(BUILD, "coverage")


if os.name == "nt":
    PYLINT_EXE = "pylint.bat"
    PYTEST_EXE = "py.test.exe"
    COVERAGE   = "coverage.exe"
    SPHINX     = "sphinx-build.exe"
else:
    PYLINT_EXE = "pylint"
    PYTEST_EXE = "py.test"
    COVERAGE   = "coverage"
    SPHINX     = "sphinx-build"

################################################################################
# Metrics' subtasks
@task
@requires("pylint")
@check_result
def pylint():
    """Runs pylint report and saves into build directory"""
    return subprocess.call("{0} formic".format(PYLINT_EXE).split(" "))

@task
@do_if(Env("WORKSPACE"))
@mkdirs(os.path.dirname(BUILD_PYLINT))
@requires("pylint")
def pylint_jenkins():
    """Run PyLint on the code and produce a report suitable for the
    Jenkins plugin 'violations'.

    Note that there is a bug in the Violations plugin which means that
    absolute paths to source (produced by PyLint) are not read. The sed command
    removes the workspace part of the path making everything good again. This
    requires the environment variable WORKSPACE from Jenkins"""
    cmd = '{0} formic -f parseable'.format(PYLINT_EXE).split(' ')
    return call(cmd, stdout=BUILD_PYLINT)

@task
@do_if(Which("sloccount"))
@mkdirs(os.path.dirname(BUILD_SLOCCOUNT))
@fail_if(StdErr())
@check_result
@adjust_env(LC_ALL="C") # Internationalisation issues in Perl on the build platform
def sloccount():
    """If David A Wheeler's excellent SLOCcount is installed, run it capturing
    results.

    The format used is suitable for processing by the sloccount plugin in Jenkins."""
    return call("sloccount --duplicates --wide --details formic".split(" "), stdout=BUILD_SLOCCOUNT)

################################################################################
# Main tasks

@task
@requires("pytest>2.2")
@mkdirs(os.path.dirname(BUILD_PYTEST))
@fail_if(StdErr())
def unit_test():
    subprocess.check_call('{0} --junitxml {1} formic'.format(PYTEST_EXE, BUILD_PYTEST).split(" "))

@task
@fail_if(StdErr())
def sanity_test():
    import formic
    version = formic.get_version()
    line = subprocess.check_output("formic --version".split()).strip()
    print(line)
    assert line.startswith("formic")
    assert line.endswith("http://www.aviser.asia/formic")
    assert version in line

    subprocess.check_call("formic --help".split())
    subprocess.check_call("formic --usage".split())


@task
@depends(unit_test, sanity_test)
def test():
    """Runs py.test on the development files"""

@task
@depends(pylint_jenkins, test, sloccount)
def metrics():
    """Run various metrics-gatherers on formic, capturing results in a way
    that Jenkins can interpret them"""
    pass

@task
def develop():
    """Run 'python setup.py develop' so formic is present in the current
    Python environment"""
    return subprocess.call("python setup.py develop".split())

@task
@requires("sphinx")
@depends(develop)
def doc():
    """Runs Sphinx to produce the documentation (output to ./build/htmldoc)"""
    return subprocess.call("{0} doc {1}".format(SPHINX, BUILD_DOC).split())

@task
def configure_google_analytics():
    """An optional task; if run, this will switch on Google Analystics, reporting
    documentation usage to Aviser.

    This is meant to be run only by Aviser when producing HTML for the main
    web site.
    """
    f = open(os.path.join("doc", "_templates", "google-analytics.html"), "w")
    f.write("""<script type="text/javascript">
var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-31981784-1']);
_gaq.push(['_setDomainName', 'aviser.asia']);
_gaq.push(['_setAllowLinker', true]);
_gaq.push(['_trackPageview']);

(function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
</script>""")
    f.close()

@task
@requires("coverage", "pytest>2.2", "pytest-cov")
@mkdirs(BUILD_COVER)
@cwd("formic")
def coverage():
    """Runs the whole test suite with Coverage

    Reports are in ./build/coverage"""
    subprocess.check_call('{0} --cov-config ../coveragerc --cov-report html --cov-report xml --cov formic'.format(PYTEST_EXE).split(" "))


@task
@depends(test, doc)
@requires('yolk')
def publish():
    """Publishes Formic to PyPi (don't run unless you are the maintainer)"""
    print("To be ready for release, remember:")
    print("      1) Update the version number (and associated test)")
    print("      2) Update the ChangeLog.rst (and other documentation)")
    print("         ChangeLog should have an line (title) consisting of the version number")
    print("      3) Tag Mercurial with 'Release <version>'")
    print("      4) Push updates to BitBucket")
    print("      5) Set the RELEASE environment variable")
    print("           $ export RELEASE=formic")

    cmd = ['bash', '-c', 'yolk -M formic | grep "^version: " | sed "s/^version: \\(.*\\)$/\\1/"']
    published_version = subprocess.check_output(cmd).strip()
    our_version = open(os.path.join("formic", "VERSION.txt"), "r").read()

    # sanity test on version
    if "\n" in published_version or\
       len(published_version) < 3 or len(published_version) > 10:
        raise Exception("Published version number seems weird: " + published_version)

    print("Published version:", published_version)
    print("Current version:  ", our_version)

    if our_version == published_version:
        raise Exception("You are attempting to republish version " + our_version)

    # sanity: check ChangeLog starts with our version
    changelog = open("CHANGELOG.rst", "r")
    found = False
    for line in changelog.readlines():
        if line.strip() == our_version:
            print("ChangeLog has an entry")
            found = True
            break
    changelog.close()
    if not found:
        raise Exception("The ChangeLog does not appear to include comments on this release")

    # Sanity check: is there a release tag
    tags = subprocess.check_output("hg tags".split())
    found = False
    looking_for = "Release " + our_version
    for line in tags.split("\n"):
        match = re.match(r"^(.*)\s+[0-9]+:[0-9a-f]+$", line)
        if match:
            tag = match.group(1).strip()
            if tag == looking_for:
                print("Found tag", tag)
                found = True
                break

    if not found:
        raise Exception("Mercurial does not have the release tag: " + looking_for)

    status = subprocess.check_output(["hg", "status"])
    for line in status.split("\n"):
        if len(line) > 0:
            raise Exception("Uncommitted changes present")

    try:
        v = os.environ["RELEASE"]
        if v != "formic":
            raise KeyError()
    except KeyError:
        print("$RELEASE environment variable is not set")
        raise

    subprocess.check_call("python setup.py bdist_egg upload".split())
    subprocess.check_call("python setup.py sdist upload".split())

################################################################################
# Bootstrap for running the script directly
if __name__ == "__main__":
    import sys
    run(sys.argv[1:])
