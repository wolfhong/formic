''' Just provides a method to replace `os.walk`, if it was needed.
TreeWalk.walk_from_list(files) return a function just working similarly to `os.walk()`.
This file is not necessary when you're using Formic.
'''
import os
from collections import defaultdict

FILE_MARKER = object()


class TreeWalk(object):

    @classmethod
    def list_to_tree(cls, files):
        """Converts a list of filenames into a directory tree structure."""

        def attach(branch, trunk):
            """Insert a branch of directories on its trunk."""
            parts = branch.split('/', 1)
            if len(parts) == 1:  # branch is a file
                trunk[FILE_MARKER].append(parts[0])
            else:
                node, others = parts
                if node not in trunk:
                    trunk[node] = defaultdict(dict, ((FILE_MARKER, []), ))
                attach(others, trunk[node])

        tree = defaultdict(dict, ((FILE_MARKER, []), ))
        for line in files:
            attach(line, tree)
        return tree

    @classmethod
    def tree_walk(cls, directory, tree):
        """Walks a tree returned by `cls.list_to_tree` returning a list of
        3-tuples as if from os.walk()."""
        results = []
        dirs = [d for d in tree if d != FILE_MARKER]
        files = tree[FILE_MARKER]
        results.append((directory, dirs, files))
        for d in dirs:
            subdir = os.path.join(directory, d)
            subtree = tree[d]
            results.extend(cls.tree_walk(subdir, subtree))
        return results

    @classmethod
    def walk_from_list(cls, files):
        """A function that mimics :func:`os.walk()` by simulating a directory with
        the list of files passed as an argument.

        :param files: A list of file paths
        :return: A function that mimics :func:`os.walk()` walking a directory
                 containing only the files listed in the argument
        """
        tree = cls.list_to_tree(files)

        def walk(directory, **kwargs):
            return cls.tree_walk(directory, tree)

        return walk
