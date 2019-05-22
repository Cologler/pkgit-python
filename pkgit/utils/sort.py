# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
# a simple sort system
# ----------

_empty_set = frozenset()

class SortRule:
    def __init__(self):
        self._data = {}

    def _get_node(self, key, create=False):
        try:
            return self._data[key]
        except KeyError:
            pass

        if create:
            return self._data.setdefault(key, _SortNode(key, self))
        else:
            return _empty

    def has_order(self, first, second):
        self._get_node(second, True).has_before(first)

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

    def get_key(self, item):
        node = self._get_node(item)
        if node is None:
            code = (1, node)
        else:
            code = (0, node.get_order_code())
        return code

    def sort(self, iterable):
        return sorted(iterable, key=self.get_key)


class _EmptyNode:
    def __repr__(self):
        return '_EmptyNode()'

    def get_before_chain(self):
        return _empty_set

    def get_order_code(self):
        return 1

_empty = _EmptyNode()

class _SortNode:
    def __init__(self, me, manager):
        self._me = me # value of this node
        self._manager: SortManager = manager
        self._before_me = set()

    def __repr__(self):
        return f'_SortNode({self._before_me})'

    def has_before(self, value):
        if self._me == value:
            raise TypeError
        if self._me in self._manager._get_node(value).get_before_chain():
            raise TypeError
        self._before_me.add(value)

    def get_before_chain(self):
        ret = set()
        ret.update(self._before_me)
        for item in self._before_me:
            ret.update(self._manager._get_node(item).get_before_chain())
        return ret

    def get_order_code(self):
        return sum(self._manager._get_node(x).get_order_code() for x in self._before_me) + 1
