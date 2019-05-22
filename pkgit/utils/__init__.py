# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import Callable, TypeVar

from anyioc import ServiceProvider

T = TypeVar('T')

_IOC_FOR_LAZY = ServiceProvider()

def lazy(factory: Callable[[], T]):
    key = object()
    _IOC_FOR_LAZY.register_singleton(key, factory)
    def wrapper() -> T:
        return _IOC_FOR_LAZY[key]
    return wrapper
