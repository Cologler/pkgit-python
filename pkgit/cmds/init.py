# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import click
import fsoopify

from ..core import pkgit_ioc, PkgitConf
from .git import update_gitignore

def init(self, ctx: click.Context, envs: str):
    ''' init project on current project. '''
    if not envs:
        ctx.fail(
            'You need to let pkgit known what kind of project you want to create, for example, ' +
            click.style('python+vscode', fg='blue')
        )
    envs_list = envs.split('+')
    from ..core.envs import ENVS_MAP
    keys = []
    for env in envs_list:
        k = ENVS_MAP.get(env)
        if k is None:
            ctx.fail('Unable to parse env: ' + click.style(env, fg='green'))
        keys.append(k)

    conf: PkgitConf = pkgit_ioc.get(PkgitConf)
    local_conf = conf.get_local_conf()
    if conf.is_local_new:
        local_conf['envs'] = keys
    else:
        ctx.fail('You cannot init a project again')
    conf.save()
    update_gitignore(ctx)
