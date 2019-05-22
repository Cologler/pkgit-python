# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from pytest import raises

from pkgit.utils.sort import SortRule

def _assert_from_pairs(pairs, example):
    sr = SortRule()
    for pair in pairs:
        sr.has_order(*pair)
    ret = sr.sort(example)
    for f, s in pairs:
        assert ret.index(f) < ret.index(s)
    return ret

def test_sortsys_sort_with_default():
    sr = SortRule()
    assert sr.sort([1, 2, 3, 4]) == [1, 2, 3, 4]

def test_sortsys_sort_with_has_order():
    pairs = [
        (1, 4), (4, 2), (4, 3), (3, 5)
    ]
    _assert_from_pairs(pairs, [1, 2, 3, 4, 5, 6])

def test_sortsys_can_detect_recursion():
    sr = SortRule()
    sr.has_order(1, 2)
    sr.has_order(2, 3)
    sr.has_order(3, 4)
    with raises(TypeError):
        sr.has_order(4, 1)
