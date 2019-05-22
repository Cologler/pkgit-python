# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import click

from ..core import pkgit_ioc, PkgitConf, Envs

from .bases import InitedCommand

def get_wellknow_envs(ctx, envs_list):
    keys = []
    for env in envs_list:
        k = Envs.map.get(env)
        if k is None:
            ctx.fail('Unable to parse env: ' + click.style(env, fg='green'))
        keys.append(k)
    return keys

class Env(InitedCommand):
    def list(self):
        '''list all envs from current project.'''

        envs = self._local_conf.get('envs', ())
        if envs:
            click.echo('envs in current project:')
            for env in envs:
                click.echo(f'  - {env}')
        else:
            click.echo('none envs in current project.')


    def add(self, envs: str):
        '''add envs to current project.'''

        if not envs:
            self._ctx.fail('env is empty')

        envs_list = envs.split('+')
        keys = get_wellknow_envs(self._ctx, envs_list)
        keys = [k for k in keys if k not in self._local_conf.get('envs', ())]

        if not keys:
            self._ctx.fail('all envs in your .pkgit already')

        self._local_conf['envs'] = self._local_conf.get('envs', []) + keys
        self._conf.mark_local_changed()

        from ..env_builders import BuilderCollection
        BuilderCollection.from_conf().init()

        self._conf.save()
