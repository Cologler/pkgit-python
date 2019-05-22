# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import click
import fsoopify

from ..core import pkgit_ioc, PkgitConf
from .license import set_new_license, update_license
from .env import get_wellknow_envs


def init(self, ctx: click.Context, envs: str, license=None):
    ''' init project on current project. '''
    if not envs:
        ctx.fail(
            'You need to let pkgit known what kind of project you want to create, for example, ' +
            click.style('python+vscode', fg='blue')
        )
    envs_list = envs.split('+')

    keys = get_wellknow_envs(ctx, envs_list)

    conf: PkgitConf = pkgit_ioc.get(PkgitConf)
    local_conf = conf.get_local_conf()
    if not conf.is_local_new:
        ctx.fail('You cannot init a project again')

    if license is not None:
        set_new_license(ctx, conf, license)
    local_conf['envs'] = keys

    from ..env_builders import BuilderCollection
    BuilderCollection.from_conf().init()

    update_license(ctx, conf)

    conf.save()
