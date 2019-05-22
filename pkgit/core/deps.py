# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from ..utils.sort import SortRule

_all = {}
_order = {}
_empty_set = frozenset()

_sort_rule = SortRule()

class Node:
    def get_requires(self):
        return _empty_set

    def get_requires_chain(self):
        return _empty_set

    def _internal_get_requires_chain(self, items: list):
        pass

class RequiresNode(Node):
    _registers = {}

    @classmethod
    def get_node(cls, env, create=False):
        try:
            return cls._registers[env]
        except KeyError:
            pass

        if create:
            return cls._registers.setdefault(env, cls(env))
        else:
            return _Empty

    def __init__(self, env):
        self._env = env
        self._requires = set()

    def __repr__(self):
        return f'deps({self._env}, {self._requires})'

    def _raise_recursion_require(self, dep):
        raise TypeError((self._env, dep))

    def require(self, *deps):
        for dep in deps:
            if dep == self._env:
                raise TypeError
            if self._env in self.get_node(dep).get_requires_chain():
                self._raise_recursion_require(dep)
        self._requires.update(deps)

    def get_requires(self):
        '''get direct deps (without self).'''
        return frozenset(self._requires)

    def get_requires_chain(self):
        '''get deps chain (without self).'''
        items = []
        self._internal_get_requires_chain(items)
        return frozenset(items)

    def _internal_get_requires_chain(self, items: list):
        for dep in self._requires:
            items.append(dep)
            get_requires(dep)._internal_get_requires_chain(items)


_Empty = Node()

def get_requires(env, create=False) -> Node:
    return RequiresNode.get_node(env)

def declare_requires(env, *deps):
    rn = RequiresNode.get_node(env, True)
    rn.require(*deps)
    for dep in deps:
        _sort_rule.has_order(dep, env)

def declare_order(env, then_env):
    _sort_rule.has_order(env, then_env)

def sort_envs(envs: list):
    '''sort envs by deps, return a new list.'''
    return _sort_rule.sort(envs)
