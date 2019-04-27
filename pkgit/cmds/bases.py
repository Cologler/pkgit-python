# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import click

from ..core import pkgit_ioc, PkgitConf

class InitedCommand:
    def __init__(self, ctx: click.Context):
        self._ctx = ctx
        self._conf: PkgitConf = pkgit_ioc[PkgitConf]
        self._local_conf = self._conf.get_local_conf()
        if self._conf.is_local_new:
            ctx.fail('You need to init the project before do this')
