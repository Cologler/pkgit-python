# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import click
import fsoopify

from ..core import pkgit_ioc, PkgitConf
from ..core.envs import Envs, EnvsValues

def make_env_gitignore_map():
    self_file = fsoopify.Path(__file__)
    data_path = self_file.dirname.dirname / 'data' / 'gitignore.json'
    d = fsoopify.NodeInfo.from_path(data_path).load()
    new_d = d.copy()
    for k, v in d.items():
        if k.lower() not in new_d:
            new_d[k.lower()] = v
    new_d[Envs.VSCODE] = new_d['VisualStudioCode']
    return new_d

GITIGNORE_MAP = make_env_gitignore_map()

def update_gitignore(ctx: click.Context):
    import requests

    conf: PkgitConf = pkgit_ioc.get(PkgitConf)
    local_conf = conf.get_local_conf()

    gitignores = []
    for env in local_conf.get('envs', ()):
        path = GITIGNORE_MAP.get(env)
        if path:
            gitignores.append([env, path])

    sb = []
    for gii in gitignores:
        env, path = gii
        url = f'https://github.com/github/gitignore/raw/master/{path}'
        sb.append('#' * 40)
        sb.append('#' * 5 + f'  gitignore for {env}')
        sb.append('#' * 5 + f'  url: {url}')
        sb.append('#' * 40)
        sb.append('')
        r = requests.get(url)
        if r.status_code != 200:
            sc = click.style(str(r.status_code), fg='red')
            ctx.fail('status code {sc} when gets ' +
                click.style(url, fg='green'))
        sb.append(r.text)
        sb.append('')
        sb.append('')

    doc = '\n'.join(sb)
    fsoopify.FileInfo('.gitignore').write_text(doc, append=False)

    gi_envs = ', '.join(click.style(z[0], fg='green') for z in gitignores)
    click.echo(f'updated gitignore for {gi_envs}')

class Git:
    '''sub commands for git module'''
    class Gitignore:
        def update(self, ctx: click.Context):
            '''update local gitignore'''
            update_gitignore(ctx)

