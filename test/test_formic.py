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
"""Tests on formic"""
# pylint: disable-all

import sys
import os
import pytest

add_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, add_path)


from formic.formic import get_version, MatchType, Matcher, ConstantMatcher, \
    FNMatcher, FormicError, Section, Pattern, PatternSet, FileSetState, \
    FileSet, get_path_components, reconstitute_path
from formic.treewalk import TreeWalk


def create_starstar(glob):
    ps = Pattern.create(glob)
    for pattern in ps.patterns:
        if pattern.file_pattern == "*":
            pattern_dir = pattern
        else:
            pattern_file = pattern
    return (pattern_dir, pattern_file)


def match(matcher, original, expected):
    matched = set()
    unmatched = set(original)
    matcher.match_files(matched, unmatched)
    assert set(expected) == matched
    assert unmatched == set(original) - matched


NOT_PRESENT = -1
MATCHED_INHERIT = 0
MATCHED_AND_SUBDIR = 1
MATCHED_NO_SUBDIR = 2
UNMATCHED = 3


def file_set_state_location(file_set_state, pattern, location):
    """A helper function that validates that the correct FileSetState
    contains the Pattern 'pattern'."""
    msg = [
        "MATCHED_INHERIT", "MATCHED_AND_SUBDIR", "MATCHED_NO_SUBDIR",
        "UNMATCHED"
    ]
    locations = [
        file_set_state.matched_inherit.patterns,
        file_set_state.matched_and_subdir.patterns,
        file_set_state.matched_no_subdir.patterns,
        file_set_state.unmatched.patterns
    ]
    found = [pattern in patterns for patterns in locations]
    count = len([b for b in found if b])
    if count == 0:
        if location == NOT_PRESENT:
            pass
        else:
            assert False, "{0} was not found anywhere in {1}".format(
                pattern, file_set_state)
    elif count > 1:
        assert False, "{0} was found in {1} locations in {2}".format(
            pattern, count, file_set_state)
    else:
        for i in range(0, 4):
            if found[i]:
                break
        if location == NOT_PRESENT:
            assert False, "{0} was in {1} but should have been NOT PRESENT for path {2}".\
                            format(pattern, msg[i], file_set_state.path_elements)

        else:
            if i != location:
                assert False, "{0} was in {1} but should have been in {2} for path {3}".\
                                format(pattern, msg[i], msg[location], file_set_state.path_elements)


def find_count(directory, pattern):
    """Platform-detecting way to count files matching a pattern"""
    if os.name == "posix":
        return find_count_posix(directory, pattern)
    elif os.name == "nt":
        return find_count_dos(directory, pattern)
    else:
        raise Exception("System is neither Posix not Windows")


def find_count_posix(directory, pattern):
    """Runs Unix find command on a directory counting how many files match
    the specified pattern"""
    if pattern is None:
        pattern = "*"
    import subprocess
    process = subprocess.Popen(
        ["find", str(directory), "-type", "f", "-name",
         str(pattern)],
        stdout=subprocess.PIPE)
    lines = 0
    while True:
        line = process.stdout.readline()
        if line:
            lines += 1
        else:
            break
    print("find", directory, "-type f -name", pattern, ": found", lines,
          "files")
    return lines


def find_count_dos(directory, pattern):
    """Runs DOS dir /s command on a directory counting how many files match
    the specified pattern"""
    if pattern is None:
        pattern = "*.*"
    import subprocess
    process = subprocess.Popen(
        ["dir",
         str(os.path.join(directory, pattern)), "/s", "/a-d", "/b"],
        stdout=subprocess.PIPE,
        shell=True)
    lines = 0
    while True:
        line = process.stdout.readline()
        if line:
            lines += 1
        else:
            break
    print("dir", str(os.path.join(directory, pattern)), "/s : found", lines,
          "files")
    return lines


def get_test_directory():
    """Return a platform-suitable directory for bulk-testing"""
    if os.name == "posix":
        return "/usr/sbin"
    elif os.name == "nt":
        return "C:\\WINDOWS\\Boot"
    else:
        raise Exception("System is neither Posix not Windows")


def formic_count(directory, pattern):
    if pattern is None:
        pattern = "*"
    fs = FileSet(
        directory=directory,
        include="/**/" + pattern,
        default_excludes=False,
        symlinks=False)
    lines = sum(1 for f in fs.files())
    print("FileSet found", lines, "files")
    return lines


def compare_find_and_formic(directory, pattern=None):
    """Runs find and formic on the same directory with the same file pattern;
    both approaches should return the same number of files."""
    assert find_count(directory, pattern) == formic_count(directory, pattern)


def test_path_components():
    d = os.getcwd() + os.path.sep
    drive, folders = get_path_components(d)
    if os.name == "nt":
        assert drive is not None
        assert d.startswith(drive)
        reconst = reconstitute_path(drive, folders)
        assert d.startswith(reconst)
        assert reconst.endswith(os.path.sep) is False

        drive2, folders2 = get_path_components(drive + os.path.sep)
        assert drive2 == drive
        assert folders2 == []
        reconst = reconstitute_path(drive2, folders2)
        assert reconst.endswith(os.path.sep)

    else:
        assert drive == ""
        reconst = os.path.join(os.path.sep, *folders)
        print(d, reconst)
        assert d.startswith(reconst)
        assert reconst.endswith(os.path.sep) is False

        drive2, folders2 = get_path_components(os.path.sep)
        assert drive2 == ""
        assert folders2 == []
        reconst = reconstitute_path(drive2, folders2)
        assert reconst.endswith(os.path.sep)


class TestMatchers(object):
    def test_basic(self):
        assert Matcher("test") == Matcher("test")
        assert Matcher("a") != Matcher("b")

        # Test Constant matcher
        assert isinstance(Matcher.create("a"), ConstantMatcher)
        assert Matcher.create("a").match("a")
        assert not Matcher.create("a").match("b")
        assert Matcher.create("a") == Matcher.create("a")
        assert Matcher.create("test") == Matcher.create("test")

        # Test FNMatcher
        assert isinstance(Matcher.create("a*"), FNMatcher)
        assert Matcher.create("a*").match("abc")
        assert Matcher.create("a*").match("ape")
        assert not Matcher.create("a*").match("bbc")
        assert Matcher.create("a?").match("ab")
        assert not Matcher.create("a?").match("ba")


class TestSections(object):
    def test_basic(self):
        s = Section(['test'])
        assert s.str == "test"
        assert s.elements[0] == ConstantMatcher("test")

        s = Section(["test", "bin"])
        assert s.str == "test/bin"
        assert s.elements[0] == ConstantMatcher("test")
        assert s.elements[1] == ConstantMatcher("bin")

        s = Section(["????", "test", "bin"])
        assert s.str == "????/test/bin"
        assert s.elements[0] == FNMatcher("????")
        assert s.elements[1] == ConstantMatcher("test")
        assert s.elements[2] == ConstantMatcher("bin")

    def test_match_single_no_bindings(self):
        s = Section(['test'])
        path = []
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [1] == matches

        path = "not".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test/util/bin/test/last/test".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [1, 4, 6] == matches

        path = "not/util/bin/test/last/not".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [4] == matches

    def test_match_single_bound_start(self):
        s = Section(['test'])
        s.bound_start = True
        path = []
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [1] == matches

        path = "not".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test/util/bin/test/last/test".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [1] == matches

        path = "not/util/bin/test/last/not".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

    def test_match_single_bound_end(self):
        s = Section(['test'])
        s.bound_end = True
        path = []
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [1] == matches

        path = "not".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test/util/bin/test/last/test".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [6] == matches

        path = "not/util/bin/test/last/not".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

    def test_match_twin_elements_no_bindings(self):
        s = Section(['test', "a*"])
        path = []
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test/bin".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test/andrew".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [2] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [2, 5, 7] == matches

        path = "not/util/bin/test/ast/not".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [5] == matches

    def test_match_twin_elements_bound_start(self):
        s = Section(['test', "a*"])
        s.bound_start = True
        path = []
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test/bin".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test/andrew".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [2] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [2] == matches

        path = "not/util/bin/test/ast/not".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

    def test_match_twin_elements_bound_end(self):
        s = Section(['test', "a*"])
        s.bound_end = True
        path = []
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test/bin".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test/andrew".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [2] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [7] == matches

        path = "not/util/bin/test/ast/not".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

    def test_single_match_not_beginning(self):
        s = Section(['test'])
        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [index for index in s.match_iter(path, 2)]
        assert [4, 6] == matches
        matches = [index for index in s.match_iter(path, 3)]
        assert [4, 6] == matches
        matches = [index for index in s.match_iter(path, 4)]
        assert [6] == matches
        matches = [index for index in s.match_iter(path, 5)]
        assert [6] == matches
        matches = [index for index in s.match_iter(path, 6)]
        assert [] == matches
        matches = [index for index in s.match_iter(path, 7)]
        assert [] == matches
        matches = [index for index in s.match_iter(path, 8)]
        assert [] == matches

    def test_multi_match_not_beginning(self):
        s = Section(['test', 'a*'])
        path = "test".split("/")
        matches = [index for index in s.match_iter(path, 1)]
        assert [] == matches

        path = "test/andrew".split("/")
        matches = [index for index in s.match_iter(path, 1)]
        assert [] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [index for index in s.match_iter(path, 2)]
        assert [5, 7] == matches
        matches = [index for index in s.match_iter(path, 3)]
        assert [5, 7] == matches
        matches = [index for index in s.match_iter(path, 4)]
        assert [7] == matches
        matches = [index for index in s.match_iter(path, 5)]
        assert [7] == matches
        matches = [index for index in s.match_iter(path, 6)]
        assert [] == matches
        matches = [index for index in s.match_iter(path, 7)]
        assert [] == matches
        matches = [index for index in s.match_iter(path, 8)]
        assert [] == matches

    def test_match_bound_start(self):
        s = Section(['test', "a*"])
        s.bound_start = True
        path = "test".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [index for index in s.match_iter(path, 0)]
        assert [2] == matches

        path = "test/andrew/bin/test/ast/test/another".split("/")
        matches = [index for index in s.match_iter(path, 1)]
        assert [] == matches


class TestPattern(object):
    def test_illegal_glob(self):
        with pytest.raises(FormicError):
            Pattern.create("/test/../**")

    def test_glob_with_pointless_curdir(self):
        simple = ['**', 'test', 'test']
        assert simple == Pattern._simplify(['**', '.', 'test', 'test'])
        assert simple == Pattern._simplify(['**', 'test', '.', 'test'])
        assert simple == Pattern._simplify(['**', 'test', 'test', '.'])

        assert simple == Pattern._simplify(['**', '**', 'test', 'test'])
        assert simple == Pattern._simplify(['**', '**', '**', 'test', 'test'])

        simple = ['**', 'test', '**', 'test']
        assert simple == Pattern._simplify(['**', 'test', '**', '**', 'test'])

    def test_compilation_and_str(self):
        # Syntax for the dictionary:
        # The key is the normative string, and the value is a list of patterns that generate the normative
        patterns = {
            "/*.py": ["/*.py"],
            "/test/*.py": ["/test/*.py"],
            "/test/dir/**/*": ["/test/dir/**/*"],
            "/start/**/test/*.py": ["/start/**/test/*.py"],
            "/start/**/test/**/*.py": ["/start/**/test/**/*.py"],
            "**/test/*.py": ["test/*.py", "**/test/*.py"],
            "**/test/*": ["test/*", "**/test/*"],
            "**/test/**/*": ["test/**/*", "**/test/**/*"],
            "**/test/**/*.py": ["test/**/*.py", "**/test/**/*.py"],
            "**/start/**/test/**/*.py":
            ["start/**/test/**/*.py", "**/start/**/test/**/*.py"],
        }
        for normative, options in patterns.items():
            for option in options:
                print("Testing that Pattern.create('{0}') == '{1}'".format(
                    option, normative))
                assert normative == str(Pattern.create(option))

    def test_compilation_and_str_starstar(self):
        for glob in [
                "test/", "/test/", "/test/**/", "/test/**", "/1/**/test/"
        ]:
            patternset = Pattern.create(glob)
            assert isinstance(patternset, PatternSet)
            assert len(patternset.patterns) == 2
            for pattern in patternset.patterns:
                assert pattern.file_pattern == "test" or pattern.sections[-1].elements[-1].pattern == "test"

    def test_compilation_bound_start(self):
        p = Pattern.create("/*.py")
        assert p.bound_start is True
        assert p.bound_end is True
        assert str(p.file_pattern) == "*.py"
        assert p.sections == []

        p = Pattern.create("/test/*.py")
        assert p.bound_start is True
        assert p.bound_end is True
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["test"])]

        p = Pattern.create("/test/dir/*")
        assert p.bound_start is True
        assert p.bound_end is True
        assert p.file_pattern == "*"
        assert p.sections == [Section(["test", "dir"])]

        p = Pattern.create("/start/**/test/*.py")
        assert p.bound_start is True
        assert p.bound_end is True
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["start"]), Section(["test"])]

        p = Pattern.create("/start/**/test/**/*.py")
        assert p.bound_start is True
        assert p.bound_end is False
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["start"]), Section(["test"])]

    def test_compilation_unbound_start(self):
        p = Pattern.create("*.py")
        assert p.bound_start is False
        assert p.bound_end is False
        assert str(p.file_pattern) == "*.py"
        assert p.sections == []

        p = Pattern.create("test/*.py")
        assert p.bound_start is False
        assert p.bound_end is True
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["test"])]

        p = Pattern.create("**/test/*.py")
        assert p.bound_start is False
        assert p.bound_end is True
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["test"])]

        p = Pattern.create("**/test/**/*")
        assert p.bound_start is False
        assert p.bound_end is False
        assert p.file_pattern == "*"

        assert p.sections == [Section(["test"])]

        p = Pattern.create("**/test/*")
        assert p.bound_start is False
        assert p.bound_end is True
        assert p.file_pattern == "*"

        assert p.sections == [Section(["test"])]

        p = Pattern.create("**/test/**/*.py")
        assert p.bound_start is False
        assert p.bound_end is False
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["test"])]

        p = Pattern.create("start/**/test/**/*.py")
        assert p.bound_start is False
        assert p.bound_end is False
        assert str(p.file_pattern) == "*.py"
        assert p.sections == [Section(["start"]), Section(["test"])]

    def test_complex_compilation(self):
        p1 = Pattern.create("dir/file.txt")
        p2 = Pattern.create("**/dir/file.txt")
        p3 = Pattern.create("/**/dir/file.txt")
        assert p1.sections == p2.sections
        assert p2.sections == p3.sections
        assert p1.bound_start is False
        assert p1.bound_start == p2.bound_start == p3.bound_start
        assert p1.bound_end is True
        assert p1.bound_end == p2.bound_end == p3.bound_end

    def test_match_pure_file_pattern(self):
        # No sections - all must match
        p = Pattern.create("test.py")
        assert p.match_directory([]) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory(
            "test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory(
            "some/where/".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES

    def test_match_bound_start_file_pattern(self):
        p = Pattern.create("/test.py")
        assert p.match_directory([]) == MatchType.MATCH_BUT_NO_SUBDIRECTORIES
        assert p.match_directory(
            "test".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory(
            "test/sub/".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory(
            "some/where/".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES

    def test_match_single_bound_start_no_sub(self):
        p = Pattern.create("/test/*.py")
        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory(
            "test".split("/")) == MatchType.MATCH_BUT_NO_SUBDIRECTORIES
        assert p.match_directory(
            "some/where/".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES

    def test_match_single_bound_start_any_sub(self):
        p = Pattern.create("/test/**/*")
        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory(
            "test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p.match_directory("some/where/test".split(
            "/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory(
            "some/where/".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES

    def test_match_single_unbound_directory(self):
        p_dir, p_file = create_starstar("test/")
        assert p_dir.match_directory([]) == MatchType.NO_MATCH
        assert p_dir.match_directory(
            "test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory(
            "some/where/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory("middle/test/middle".split(
            "/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory(
            "not/a/hope".split("/")) == MatchType.NO_MATCH

        unmatched = set(["1", "2", "3", "test"])
        matched = set()
        p_file.match_files(matched, unmatched)
        assert len(matched) == 1
        assert "test" in matched
        assert len(unmatched) == 3
        assert "test" not in unmatched
        p_dir.match_files(matched, unmatched)
        assert len(matched) == 4
        assert len(unmatched) == 0

        p_dir, p_file = create_starstar("**/test/**")
        assert p_dir.match_directory([]) == MatchType.NO_MATCH
        assert p_dir.match_directory(
            "test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory(
            "some/where/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory("middle/test/middle".split(
            "/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory(
            "not/a/hope".split("/")) == MatchType.NO_MATCH

        unmatched = set(["1", "2", "3", "test"])
        matched = set()
        p_file.match_files(matched, unmatched)
        assert len(matched) == 1
        assert "test" in matched
        assert len(unmatched) == 3
        assert "test" not in unmatched
        p_dir.match_files(matched, unmatched)
        assert len(matched) == 4
        assert len(unmatched) == 0

    def test_match_single_bound_end_directory(self):
        p = Pattern.create("test/*")
        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory("test".split("/")) == MatchType.MATCH
        assert p.match_directory(
            "some/where/test".split("/")) == MatchType.MATCH
        assert p.match_directory(
            "middle/test/middle".split("/")) == MatchType.NO_MATCH
        assert p.match_directory("not/a/hope".split("/")) == MatchType.NO_MATCH

    def test_match_twin_unbound_directories(self):
        p_dir, p_file = create_starstar("some/**/test/")
        assert p_dir.match_directory([]) == MatchType.NO_MATCH
        assert p_dir.match_directory(
            "test/test/test/test".split("/")) == MatchType.NO_MATCH
        assert p_dir.match_directory(
            "some/some/some".split("/")) == MatchType.NO_MATCH
        assert p_dir.match_directory(
            "some/where/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory("a/some/where/test/b".split(
            "/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory("some/where/else/test".split(
            "/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory("some/where/a/long/way/apart/test".split(
            "/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory(
            "not/a/hope".split("/")) == MatchType.NO_MATCH

        unmatched = set(["1", "2", "3", "test"])
        matched = set()
        p_file.match_files(matched, unmatched)
        assert len(matched) == 1
        assert "test" in matched
        assert len(unmatched) == 3
        assert "test" not in unmatched
        p_dir.match_files(matched, unmatched)
        assert len(matched) == 4
        assert len(unmatched) == 0

    def test_match_twin_directories(self):
        p_dir, p_file = create_starstar("/test/**/test/")
        assert p_dir.match_directory("test/test/test/test".split(
            "/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory(
            "test/where/test".split("/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory("test/a/very/long/way/apart/test".split(
            "/")) == MatchType.MATCH_ALL_SUBDIRECTORIES

        assert p_dir.match_directory([]) == MatchType.NO_MATCH
        assert p_dir.match_directory("test".split("/")) == MatchType.NO_MATCH
        assert p_dir.match_directory(
            "not/a/hope".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p_dir.match_directory("a/test/where/test/b".split(
            "/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p_dir.match_directory("some/some/some".split(
            "/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES

        p = Pattern.create("/test/**/test/*.py")
        assert p.match_directory(
            "test/test/test/test".split("/")) == MatchType.MATCH
        assert p.match_directory(
            "test/where/test".split("/")) == MatchType.MATCH
        assert p.match_directory(
            "test/a/very/long/way/apart/test".split("/")) == MatchType.MATCH

        assert p.match_directory([]) == MatchType.NO_MATCH
        assert p.match_directory("test".split("/")) == MatchType.NO_MATCH
        assert p.match_directory(
            "not/a/hope".split("/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory("a/test/where/test/b".split(
            "/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES
        assert p.match_directory("some/some/some".split(
            "/")) == MatchType.NO_MATCH_NO_SUBDIRECTORIES

    def test_match_multiple_unbound_directories(self):
        p_dir, p_file = create_starstar("a/**/b/**/c/**/d/")
        assert p_dir.match_directory(
            "test/a/test/test/b/c/test/test/d/test".split(
                "/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory(
            "test/a/test/a/test/b/c/test/c/test/d/test".split(
                "/")) == MatchType.MATCH_ALL_SUBDIRECTORIES
        assert p_dir.match_directory(
            "test/a/test/b/test/test/d/test/c/test".split(
                "/")) == MatchType.NO_MATCH

    def test_file_pattern(self):
        p = Pattern.create("*.py")
        match(p, [], [])
        match(p, ["a.no", "py"], [])
        match(p, ["x.px", "a.py", "a.pz", "b.py", "py"], ["a.py", "b.py"])
        p = Pattern.create("?bc.txt")
        match(p, ["a.no", "py"], [])
        match(p, ["abc.txt", "bbc.txt", "not.txt"], ["abc.txt", "bbc.txt"])

    def test_no_file_pattern(self):
        p = Pattern.create("")
        assert p.file_pattern == "*"

        match(p, [], [])
        s = ["a.py", "b.py"]
        match(p, s, s)
        s = ["x.px", "a.py", "a.pz", "b.py", "py"]
        match(p, s, s)

        p = Pattern.create("*")
        assert p.file_pattern == "*"
        match(p, [], [])
        s = ["a.py", "b.py"]
        match(p, s, s)
        s = ["x.px", "a.py", "a.pz", "b.py", "py"]
        match(p, s, s)


class TestPatternSet(object):
    def test_basic(self):
        py = Pattern.create("*.py")
        cvs = Pattern.create("**/CVS/**/*")
        pycache = Pattern.create("__pycache__/**/*")

        ps = PatternSet()
        assert ps.all_files() is False
        assert [pat for pat in ps.iter()] == []
        s = ["a.py", "b.py"]
        match(ps, s, [])

        ps.append(py)
        assert ps.all_files() is False
        assert [pat for pat in ps.iter()] == [py]
        s = ["a.py", "b.py"]
        match(ps, s, s)
        s = ["a.py", "b.py", "anything.goes"]
        match(ps, s, ["a.py", "b.py"])

        ps.append(cvs)
        assert ps.all_files() is True
        assert [pat for pat in ps.iter()] == [py, cvs]
        match(ps, s, s)

        ps.remove(cvs)
        ps.append(pycache)
        assert ps.all_files() is True
        assert [pat for pat in ps.iter()] == [py, pycache]
        match(ps, s, s)

        ps.remove(pycache)
        assert ps.all_files() is False
        assert [pat for pat in ps.iter()] == [py]
        match(ps, s, ["a.py", "b.py"])

    def test_extend(self):
        py = Pattern.create("*.py")
        cvs = Pattern.create("**/CVS/*")
        pycache = Pattern.create("__pycache__/**/*")

        ps1 = PatternSet()
        ps1.extend([py, cvs, pycache])
        assert [pat for pat in ps1.iter()] == [py, cvs, pycache]

        ps2 = PatternSet()
        ps2.extend(ps1)
        assert [pat for pat in ps2.iter()] == [py, cvs, pycache]

        ps1 = PatternSet()
        ps1.extend([py])
        assert [pat for pat in ps1.iter()] == [py]
        ps1.extend([cvs, pycache])
        assert [pat for pat in ps1.iter()] == [py, cvs, pycache]


class TestFileSetState(object):
    def test_parent(self):
        root = FileSetState("Label", "")
        a = FileSetState("Label", "a", root)
        assert a.parent == root
        b = FileSetState("Label", os.path.join("a", "b"), a)
        assert b.parent == a
        c = FileSetState("Label", os.path.join("a", "b", "c"), b)
        assert c.parent == b
        # Test the abrupt change from /a/b/c to /d
        d = FileSetState("Label", "d", c)
        assert d.parent == root

    def test_patterns_root(self):
        bound_start_top_all = Pattern.create("/test/*")
        bound_start_top_py = Pattern.create("/test/*.py")
        bound_start_sub_all = Pattern.create("/test/**/*")
        bound_start_sub_py = Pattern.create("/test/**/*.py")
        bound_end_all = Pattern.create("**/test/*")
        bound_end_py = Pattern.create("**/test/*.py")
        bound_start_end = Pattern.create("/test/**/test/*.py")
        unbound_all = Pattern.create("**/*")
        unbound_py = Pattern.create("**/*.py")

        _all = [
            bound_start_top_all, bound_start_top_py, bound_start_sub_all,
            bound_start_sub_py, bound_end_all, bound_end_py, bound_start_end,
            unbound_all, unbound_py
        ]

        # Test matches for the root directory
        fst = FileSetState("Label", "", None, _all)
        file_set_state_location(fst, bound_start_top_all, UNMATCHED)
        file_set_state_location(fst, bound_start_top_py, UNMATCHED)
        file_set_state_location(fst, bound_start_sub_all, UNMATCHED)
        file_set_state_location(fst, bound_start_sub_py, UNMATCHED)
        file_set_state_location(fst, bound_end_all, UNMATCHED)
        file_set_state_location(fst, bound_end_py, UNMATCHED)
        file_set_state_location(fst, bound_start_end, UNMATCHED)
        file_set_state_location(fst, unbound_all, MATCHED_INHERIT)
        file_set_state_location(fst, unbound_py, MATCHED_INHERIT)
        assert fst.no_possible_matches_in_subdirs() is False
        assert fst.matches_all_files_all_subdirs() is True

    def test_patterns_test_matching_dir(self):
        bound_start_top_all = Pattern.create("/test/*")
        bound_start_top_py = Pattern.create("/test/*.py")
        bound_start_sub_all = Pattern.create("/test/**/*")
        bound_start_sub_py = Pattern.create("/test/**/*.py")
        bound_end_all = Pattern.create("**/test/*")
        bound_end_py = Pattern.create("**/test/*.py")
        bound_start_end = Pattern.create("/test/**/test/*.py")
        unbound_all = Pattern.create("**/*")
        unbound_py = Pattern.create("**/*.py")

        _all = [
            bound_start_top_all, bound_start_top_py, bound_start_sub_all,
            bound_start_sub_py, bound_end_all, bound_end_py, bound_start_end,
            unbound_all, unbound_py
        ]

        # Test matches for the root directory
        fst = FileSetState("Label", "test", None, _all)
        file_set_state_location(fst, bound_start_top_all, MATCHED_NO_SUBDIR)
        file_set_state_location(fst, bound_start_top_py, MATCHED_NO_SUBDIR)
        file_set_state_location(fst, bound_start_sub_all, MATCHED_INHERIT)
        file_set_state_location(fst, bound_start_sub_py, MATCHED_INHERIT)
        file_set_state_location(fst, bound_end_all, MATCHED_AND_SUBDIR)
        file_set_state_location(fst, bound_end_py, MATCHED_AND_SUBDIR)
        file_set_state_location(fst, bound_start_end, UNMATCHED)
        file_set_state_location(fst, unbound_all, MATCHED_INHERIT)
        file_set_state_location(fst, unbound_py, MATCHED_INHERIT)
        assert fst.no_possible_matches_in_subdirs() is False
        assert fst.matches_all_files_all_subdirs() is True

    def test_patterns_test_no_match(self):
        bound_start_top_all = Pattern.create("/test/*")
        bound_start_top_py = Pattern.create("/test/*.py")
        bound_start_sub_all = Pattern.create("/test/**/*")
        bound_start_sub_py = Pattern.create("/test/**/*.py")
        bound_end_all = Pattern.create("**/test/*")
        bound_end_py = Pattern.create("**/test/*.py")
        bound_start_end = Pattern.create("/test/**/test/*.py")
        unbound_all = Pattern.create("**/*")
        unbound_py = Pattern.create("**/*.py")

        _all = [
            bound_start_top_all, bound_start_top_py, bound_start_sub_all,
            bound_start_sub_py, bound_end_all, bound_end_py, bound_start_end,
            unbound_all, unbound_py
        ]

        # Test matches for the root directory
        fst = FileSetState("Label", "nottest", None, _all)
        file_set_state_location(fst, bound_start_top_all, NOT_PRESENT)
        file_set_state_location(fst, bound_start_top_py, NOT_PRESENT)
        file_set_state_location(fst, bound_start_sub_all, NOT_PRESENT)
        file_set_state_location(fst, bound_start_sub_py, NOT_PRESENT)
        file_set_state_location(fst, bound_end_all, UNMATCHED)
        file_set_state_location(fst, bound_end_py, UNMATCHED)
        file_set_state_location(fst, bound_start_end, NOT_PRESENT)
        file_set_state_location(fst, unbound_all, MATCHED_INHERIT)
        file_set_state_location(fst, unbound_py, MATCHED_INHERIT)
        assert fst.no_possible_matches_in_subdirs() is False
        assert fst.matches_all_files_all_subdirs() is True

    def test_patterns_test_no_possible_match(self):
        bound_start_top_all = Pattern.create("/test/*")
        bound_start_top_py = Pattern.create("/test/*.py")
        bound_start_sub_all = Pattern.create("/test/**/*")
        bound_start_sub_py = Pattern.create("/test/**/*.py")
        bound_start_end = Pattern.create("/test/**/test/*.py")

        _all = [
            bound_start_top_all, bound_start_top_py, bound_start_sub_all,
            bound_start_sub_py, bound_start_end
        ]

        # Test matches for the root directory
        fst = FileSetState("Label", "nottest", None, _all)
        file_set_state_location(fst, bound_start_top_all, NOT_PRESENT)
        file_set_state_location(fst, bound_start_top_py, NOT_PRESENT)
        file_set_state_location(fst, bound_start_sub_all, NOT_PRESENT)
        file_set_state_location(fst, bound_start_sub_py, NOT_PRESENT)
        file_set_state_location(fst, bound_start_end, NOT_PRESENT)
        assert fst.no_possible_matches_in_subdirs() is True
        assert fst.matches_all_files_all_subdirs() is False

    def test_patterns_inherit_with_file(self):
        pattern1 = Pattern.create("/a/**/*.a")
        pattern2 = Pattern.create("**/b/**/*.b")
        pattern3 = Pattern.create("/a/b/c/*.c")
        all_files = ["not", "a.a", "b.b", "c.c"]
        a_files = ["a.a", "aa.a"]

        # Test matches for the root directory
        root = FileSetState("Label", "", None, [pattern1, pattern2, pattern3])
        file_set_state_location(root, pattern1, UNMATCHED)
        file_set_state_location(root, pattern2, UNMATCHED)
        file_set_state_location(root, pattern3, UNMATCHED)
        assert not root.match([])
        assert not root.match(all_files)
        assert not root.match(a_files)

        a = FileSetState("Label", "a", root)
        file_set_state_location(a, pattern1, MATCHED_INHERIT)
        file_set_state_location(a, pattern2, UNMATCHED)
        file_set_state_location(a, pattern3, UNMATCHED)
        assert not a.match([])
        assert set(["a.a"]) == a.match(all_files)
        assert set(["a.a", "aa.a"]) == a.match(a_files)

        b = FileSetState("Label", os.path.join("a", "b"), a)
        file_set_state_location(b, pattern1, NOT_PRESENT)  # In parent
        file_set_state_location(b, pattern2, MATCHED_INHERIT)
        file_set_state_location(b, pattern3, UNMATCHED)
        assert not b.match([])
        assert set(["a.a", "b.b"]) == b.match(all_files)
        assert set(["a.a", "aa.a"]) == b.match(a_files)

        c = FileSetState("Label", os.path.join("a", "b", "c"), b)
        file_set_state_location(c, pattern1, NOT_PRESENT)  # In grandparent
        file_set_state_location(c, pattern2, NOT_PRESENT)  # In parent
        file_set_state_location(c, pattern3, MATCHED_NO_SUBDIR)
        assert not c.match([])
        assert set(["a.a", "b.b", "c.c"]) == c.match(all_files)
        assert set(["a.a", "aa.a"]) == c.match(a_files)

        d = FileSetState("Label", os.path.join("a", "b", "c", "d"), b)
        file_set_state_location(d, pattern1,
                                NOT_PRESENT)  # In great-grandparent
        file_set_state_location(d, pattern2, NOT_PRESENT)  # In grandparent
        file_set_state_location(d, pattern3, NOT_PRESENT)  # Not applicable
        assert not d.match([])
        assert set(["a.a", "b.b"]) == d.match(all_files)
        assert set(["a.a", "aa.a"]) == b.match(a_files)

    def test_patterns_inherit_all_files(self):
        pattern1 = Pattern.create("/a/**/*")
        all_files = ["not", "a.a", "b.b", "c.c"]

        # Test matches for the root directory
        root = FileSetState("Label", "", None, [pattern1])
        file_set_state_location(root, pattern1, UNMATCHED)
        assert not root.match([])
        assert not root.match(all_files)

        a = FileSetState("Label", "a", root)
        file_set_state_location(a, pattern1, MATCHED_INHERIT)
        assert not a.match([])
        assert set(all_files) == a.match(all_files)

        b = FileSetState("Label", os.path.join("a", "b"), a)
        file_set_state_location(b, pattern1, NOT_PRESENT)  # In parent
        file_set_state_location(a, pattern1, MATCHED_INHERIT)
        assert not b.match([])
        assert b.parent == a
        assert set(all_files) == b.match(all_files)


class TestFileSet(object):
    def test_basic(self):
        root = os.path.dirname(os.path.dirname(__file__))
        pattern_all = os.path.sep + os.path.join("**", "*")
        pattern_py = os.path.sep + os.path.join("**", "*.py")
        pattern_pyc = os.path.sep + os.path.join("**", "*.pyc")
        pattern_txt = os.path.sep + os.path.join("**", "*.txt")
        print("Formic directory=", root, "include=", pattern_py)
        definitive_count = find_count(root, "*.py")

        fs = FileSet(directory=root, include=pattern_py, symlinks=False)
        files = [os.path.join(root, _dir, _file) for _dir, _file in fs.files()]
        assert definitive_count == len(files)
        assert [] == [f for f in files if not os.path.isfile(f)]
        assert files == [f for f in files if f.endswith(".py")]

        fs = FileSet(
            directory=root,
            include=pattern_all,
            exclude=[pattern_pyc, pattern_txt])
        files = [os.path.join(root, _dir, _file) for _dir, _file in fs.files()]
        assert definitive_count <= len(files)
        assert [] == [f for f in files if not os.path.isfile(f)]
        assert [] == [f for f in files if f.endswith(".pyc")]
        assert [] == [f for f in files if f.endswith(".txt")]

    def test_bound_root(self):
        """Unit test to pick up Issue #1"""
        original_dir = os.getcwd()
        curdir = os.path.dirname(os.path.dirname(__file__))
        os.chdir(curdir)
        try:
            import glob
            actual = glob.glob("*.py")

            fs = FileSet(include="/*.py", default_excludes=False)
            count = 0
            for _file in fs:
                count += 1
                print("File:", _file)
                head, tail = os.path.split(_file)
                assert curdir == head
                assert tail in actual
                assert tail.endswith(".py")
            assert len(actual) == count
        finally:
            os.chdir(original_dir)

    def test_cwd(self):
        fs = FileSet(include="*")
        assert fs.directory is None
        assert os.getcwd() == fs.get_directory()

        directory = os.path.dirname(__file__) \
            + os.path.sep + os.path.sep + os.path.sep
        fs = FileSet(directory=directory, include="*")
        assert fs.directory == os.path.dirname(__file__)
        assert fs.get_directory() == os.path.dirname(__file__)

    def test_vs_find(self):
        compare_find_and_formic(get_test_directory())
        compare_find_and_formic(get_test_directory(), "c*")

    def test_iterator(self):
        fs = FileSet(include="*.py")
        i = fs.__iter__()
        assert set([f for f in fs.qualified_files()]) == set([f for f in i])

    def test_alternate_walk(self):
        files = [
            "CVS/error.py", "silly/silly1.txt", "1/2/3.py", "silly/silly3.txt",
            "1/2/4.py", "silly/silly3.txt"
        ]

        fileset = FileSet(include="*.py", walk=TreeWalk.walk_from_list(files))
        found = [(_dir, _file) for _dir, _file in fileset.files()]

        assert len(found) == 2
        assert ("CVS", "error.py") not in found
        assert (os.path.join("1", "2"), "3.py") in found
        assert (os.path.join("1", "2"), "4.py") in found

    def test_glob_starstar(self):
        files = [
            "in/test/1.py", "in/a/b/test/2.py", "in/a/b/test", "out/a/3.py",
            "out/a/test.py"
        ]

        fileset = FileSet(include="in/**/test/", walk=TreeWalk.walk_from_list(files))
        found = [(_dir, _file) for _dir, _file in fileset.files()]
        assert len(found) == 3
        assert (os.path.join("in", "a", "b"), "test") in found
        assert (os.path.join("out", "a"), "test.py") not in found

        files = [
            "in/test/1test1.py", "in/a/b/test/2test2.py", "in/a/b/4test4",
            "out/a/3.py", "out/a/test.py"
        ]

        fileset = FileSet(include="in/**/*test*/", walk=TreeWalk.walk_from_list(files))
        found = [(_dir, _file) for _dir, _file in fileset.files()]
        assert len(found) == 3
        assert (os.path.join("in", "a", "b"), "4test4") in found
        assert (os.path.join("out", "a"), "test.py") not in found


class TestMiscellaneous(object):
    def test_version(self):
        assert "1.0.3" == get_version()

    def test_rooted(self):
        curdir = os.getcwd()
        full = os.path.dirname(os.path.dirname(__file__))
        drive, _dir = os.path.splitdrive(full)
        wild = "**" + os.path.sep + "*.rst"
        os.chdir(full)
        try:
            fileset = FileSet(include=wild, directory=full)
            for filename in fileset.qualified_files():
                print(filename)
            absolute = [
                filename for filename in FileSet(include=wild, directory=full)
            ]
            relative = [filename for filename in FileSet(include=wild)]
            rooted = [
                filename for filename in FileSet(
                    include=os.path.join(_dir, wild),
                    directory=drive + os.path.sep)
            ]
            assert len(relative) == len(absolute) == len(rooted)
            combined = list(zip(rooted, relative, absolute))
            for root, rel, abso in combined:
                print(root, "<->", rel, "<->", abso)
                assert root.endswith(rel)
                assert abso.endswith(rel)
        finally:
            os.chdir(curdir)

    def test_search_prune_efficiency(self):
        formic_root = os.path.dirname(os.path.dirname(__file__))

        print("Absolute, starting at ", formic_root)
        rooted = FileSet(
            include="/test/lower/lower.txt",
            directory=formic_root,
            default_excludes=False)
        files = [f for f in rooted]
        assert len(files) == 1

        floating = FileSet(
            include="/*/lower/lower.txt",
            directory=formic_root,
            default_excludes=False)
        files = [f for f in floating]
        assert len(files) == 1
        assert rooted._received < floating._received

    def test_filename_case(self):
        root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test")
        for test in ["lower/lower.txt", "lower/UPPER.txt", "UPPER/lower.txt",
                     "UPPER/UPPER.txt"]:
            print("Testing", test)
            found = [f for f in FileSet(include=test, directory=root)]
            assert len(found) == 1
            print("   ... found", test)

        root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test/lower")
        test_names = ["LOWER.TXT", "upper.txt"]
        if os.name == "posix":
            for test in test_names:
                print("POSIX testing case-sensitive-exclude of", test)
                found = [f for f in FileSet("*", exclude=test, directory=root)]
                assert len(found) == 2
            for test in test_names:
                print("POSIX testing case-insensitive-exclude of", test)
                found = [f for f in FileSet("*", exclude=test, directory=root, casesensitive=False)]
                assert len(found) == 1
        elif os.name == 'nt':
            for test in test_names:
                print("NT testing case-sensitive-exclude of", test)
                found = [f for f in FileSet("*", exclude=test, directory=root)]
                assert len(found) == 1
            for test in test_names:
                print("Nt testing case-insensitive-exclude of", test)
                found = [f for f in FileSet("*", exclude=test, directory=root, casesensitive=False)]
                assert len(found) == 1

        root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "formic")
        test_names = ["Formic.py", "version.txt", "LICENSE.TXT"]
        if os.name == "posix":
            for test in test_names:
                print("POSIX testing for case-sensitive-match of", test)
                found = [f for f in FileSet(include=test, directory=root)]
                assert len(found) == 0
            for test in test_names:
                print("POSIX testing for case-insensitive-match of", test)
                found = [f for f in FileSet(include=test, directory=root, casesensitive=False)]
                assert len(found) == 1
        elif os.name == "nt":
            for test in test_names:
                print("NT testing for case-sensitive-match of", test)
                found = [f for f in FileSet(include=test, directory=root)]
                assert len(found) == 1
            for test in test_names:
                print("NT testing for case-insensitive-match of", test)
                found = [f for f in FileSet(include=test, directory=root, casesensitive=False)]
                assert len(found) == 1

    def test_directory_case(self):
        root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test")
        sensitive_names = ["/lower/", "/UPP*/"]
        insensitive_names = ["/LOWER/", "/upp*/"]
        if os.name == "posix":
            # FileSet is sensitive
            for test in sensitive_names:
                found = [f for f in FileSet(include=test, directory=root)]
                assert len(found) == 2
            for test in insensitive_names:
                found = [f for f in FileSet(include=test, directory=root)]
                assert len(found) == 0
            # FileSet is insensitive
            for test in sensitive_names:
                found = [f for f in FileSet(include=test, directory=root, casesensitive=False)]
                assert len(found) == 2
            for test in insensitive_names:
                found = [f for f in FileSet(include=test, directory=root, casesensitive=False)]
                assert len(found) == 2
        elif os.name == "nt":
            # FileSet is sensitive
            for test in sensitive_names:
                found = [f for f in FileSet(include=test, directory=root)]
                assert len(found) == 2
            for test in insensitive_names:
                found = [f for f in FileSet(include=test, directory=root)]
                assert len(found) == 2
            # FileSet is insensitive
            for test in sensitive_names:
                found = [f for f in FileSet(include=test, directory=root, casesensitive=False)]
                assert len(found) == 2
            for test in insensitive_names:
                found = [f for f in FileSet(include=test, directory=root, casesensitive=False)]
                assert len(found) == 2

    def test_symlinks(self):
        if os.name == 'posix':
            root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test/symlinks")
            pattern = "*.txt"
            found = [f for f in FileSet(include=pattern, directory=root)]  # symlinks defaults to True
            assert len(found) == 3

            found = [f for f in FileSet(include=pattern, directory=root, symlinks=True)]
            assert len(found) == 3

            found = [f for f in FileSet(include=pattern, directory=root, symlinks=False)]
            assert len(found) == 1

    def test_get_path_components(self):
        drive, components = get_path_components(os.path.join("a", "b", "c"))
        print((drive, components))
        assert drive == ""
        assert components == ["a", "b", "c"]

        drive, components = get_path_components(os.path.sep)
        assert drive == ""
        assert components == []

        drive, components = get_path_components(
            os.path.sep + "a" + os.path.sep + "b")
        print((drive, components))
        assert drive == ""
        assert components == ["a", "b"]
