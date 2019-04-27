# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import click
import fsoopify

from ..core import pkgit_ioc, PkgitConf
from ..core.envs import Envs


class GitBase:
    def __init__(self, ctx: click.Context):
        conf: PkgitConf = pkgit_ioc[PkgitConf]
        local_conf = conf.get_local_conf()
        if Envs.GIT not in local_conf.get('envs', ()):
            name = click.style(Envs.GIT, fg='green')
            ctx.fail(f'env {name} is not in your .pkgit file')


class Git(GitBase):
    '''sub commands for git system'''

    class ignore(GitBase):

        def update(self, ctx: click.Context):
            '''update local gitignore'''

            conf: PkgitConf = pkgit_ioc[PkgitConf]

            from ..env_builders import IEnvBuilder
            for builder in IEnvBuilder.get_builders_for_env(Envs.GIT, ctx, conf):
                builder.init()

