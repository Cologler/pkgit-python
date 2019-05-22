# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
# a simple sort system
# ----------

from abc import ABC, abstractmethod


class _INode(ABC):
    def has_before(self, store, value):
        pass

    @abstractmethod
    def get_before_chain(self, store):
        raise NotImplementedError

    @abstractmethod
    def get_order_code(self, store):
        raise NotImplementedError


class _EmptyNode(_INode):
    _empty_set = frozenset()

    def __repr__(self):
        return 'Empty()'

    def get_before_chain(self, _):
        return self._empty_set

    def get_order_code(self, _):
        return 1

_empty = _EmptyNode()


class _RulesStore:
    def __init__(self):
        self._data = {}

    def get_rule(self, key, create=False) -> _INode:
        try:
            return self._data[key]
        except KeyError:
            pass

        if create:
            return self._data.setdefault(key, _SortNode(key))
        else:
            return _empty

    def get_key(self, item):
        node = self.get_rule(item)
        if node is None:
            code = (1, node)
        else:
            code = (0, node.get_order_code(self))
        return code

    def build(self):
        ''' build a cachable store '''
        store = _RulesStore()
        store._data.update(dict((k, _CachedNode(v)) for (k, v) in self._data.items()))
        return store

class SortRule:
    def __init__(self):
        self._data = {}
        self._store = _RulesStore()

    def has_order(self, first, second):
        self._store.get_rule(second, True).has_before(self._store, first)

    def has_orders(self, iterable):
        '''
        equals:

        ``` py
        has_order(item_1, item_2)
        has_order(item_2, item_3)
        ...
        ```
        '''
        items = list(iterable)
        if len(items) < 2:
            raise ValueError

        for pair in zip(items, items[1:]):
            self.has_order(*pair)

    def sort(self, iterable):
        store = self._store.build()
        return sorted(iterable, key=store.get_key)


class _CachedNode(_INode):
    def __init__(self, node):
        self._node = node

    def get_before_chain(self, store):
        raise NotImplementedError

    def get_order_code(self, store):
        try:
            return self._value
        except AttributeError:
            pass

        self._value = self._node.get_order_code(store)
        return self._value


class _SortNode(_INode):
    def __init__(self, me):
        self._me = me # value of this node
        self._before_me = set()

    def __repr__(self):
        return f'SortNode({self._before_me})'

    def has_before(self, store: _RulesStore, value):
        if self._me == value:
            raise TypeError
        if self._me in store.get_rule(value).get_before_chain(store):
            raise TypeError
        self._before_me.add(value)

    def get_before_chain(self, store: _RulesStore):
        ret = set()
        ret.update(self._before_me)
        for item in self._before_me:
            ret.update(store.get_rule(item).get_before_chain(store))
        return ret

    def get_order_code(self, store: _RulesStore):
        return sum(store.get_rule(x).get_order_code(store) for x in self._before_me) + 1
