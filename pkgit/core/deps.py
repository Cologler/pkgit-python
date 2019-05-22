# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

_all = {}
_empty_set = frozenset()

class _Chain:
    def __init__(self):
        self._l = []
        self._s = set()

    def ensure(self, v):
        if v in self._s:
            raise TypeError(self._l)

        self._l.append(v)
        self._s.add(v)


class Requiresable:
    def get_requires(self):
        return _empty_set

    def get_requires_chain(self):
        return _empty_set


class RequiresNode:
    def __init__(self, env):
        self._env = env
        self._requires = set()

    def require(self, *deps):
        self._internal_require(_Chain(), deps)

    def _internal_require(self, chain: _Chain, deps: tuple):
        chain.ensure(self._env)
        self._requires.update(deps)

    def get_requires(self):
        return frozenset(self._requires)

    def get_requires_chain(self):
        items = []
        for dep in self._requires:
            items.append(dep)
            node: RequiresNode = _all.get(dep)
            if node:
                items.extend(node.get_requires_chain())
        return frozenset(items)

_Empty = Requiresable()

def declare_requires(env, *deps):
    try:
        rn: RequiresNode = _all[env]
    except KeyError:
        rn: RequiresNode = _all.setdefault(env, RequiresNode(env))
    rn.require(*deps)

def get_requires(env) -> Requiresable:
    try:
        return _all[env]
    except KeyError:
        return _Empty
