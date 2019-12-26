"""
Dependency/topological sort implementation.

"""

from logging import getLogger

from asyncsuds import *

log = getLogger(__name__)


def dependency_sort(dependency_tree):
    """
    Sorts items 'dependencies first' in a given dependency tree.

    A dependency tree is a dictionary mapping an object to a collection its
    dependency objects.

    Result is property sorted list of items, where each item is a 2-tuple
    containing an object and its dependency list, as given in the input
    dependency tree.

    If B is directly or indirectly dependent on A and they are not both a part
    of the same dependency cycle (i.e. then A is neither directly nor
    indirectly dependent on B) then A needs to come before B.

    If A and B are a part of the same dependency cycle, i.e. if they are both
    directly or indirectly dependent on each other, then it does not matter
    which comes first.

    Any entries found listed as dependencies, but that do not have their own
    dependencies listed as well, are logged & ignored.

    @return: The sorted items.
    @rtype: list

    """
    sorted = []
    processed = set()
    for key, deps in dependency_tree.items():
        _sort_r(sorted, processed, key, deps, dependency_tree)
    return sorted


def _sort_r(sorted, processed, key, deps, dependency_tree):
    """Recursive topological sort implementation."""
    if key in processed:
        return
    processed.add(key)
    for dep_key in deps:
        dep_deps = dependency_tree.get(dep_key)
        if dep_deps is None:
            log.debug('"%s" not found, skipped', Repr(dep_key))
            continue
        _sort_r(sorted, processed, dep_key, dep_deps, dependency_tree)
    sorted.append((key, deps))
