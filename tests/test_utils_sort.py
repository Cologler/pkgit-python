# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from pytest import raises

from pkgit.utils.sort import SortRule

def test_sortsys_sort_with_default():
    sr = SortRule()
    assert sr.sort([1, 2, 3, 4]) == [1, 2, 3, 4]

def test_sortsys_sort_with_has_order():
    sr = SortRule()
    sr.has_order(1, 2)
    sr.has_order(3, 2)
    assert sr.sort([1, 2, 3, 4]) == [1, 3, 4, 2]

def test_sortsys_can_detect_recursion():
    sr = SortRule()
    sr.has_order(1, 2)
    sr.has_order(2, 3)
    sr.has_order(3, 4)
    with raises(TypeError):
        sr.has_order(4, 1)
