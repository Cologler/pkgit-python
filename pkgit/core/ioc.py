# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from anyioc import ServiceProvider

pkgit_ioc = ServiceProvider()

def lazy(factory):
    key = object()
    pkgit_ioc.register_singleton(key, factory)
    return lambda: pkgit_ioc[key]
