# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import fsoopify
import click

from ..core.ioc import pkgit_ioc, lazy
from ..core.conf import PkgitConf
from ..core.envs import Envs
from . import IEnvBuilder

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

gitignore_map_factory = lazy(make_env_gitignore_map)

class GitEnvBuilder(IEnvBuilder):
    env = Envs.GIT

    def init(self):
        pass

    def update(self):
        pass


class GitIgnoreEnvBuilder(IEnvBuilder):
    env = Envs.GIT

    def _get_gitignore_file(self):
        return fsoopify.FileInfo(pkgit_ioc['cwd'] / '.gitignore')

    def init(self):
        if self._get_gitignore_file().is_file():
            click.echo(f'ignore init gitignore since it is exists')
            return
        self.update()

    def update(self):
        import requests

        local_conf = self._conf.get_local_conf()
        gitignore_map = gitignore_map_factory()

        gitignores = []
        for env in local_conf.get('envs', ()):
            path = gitignore_map.get(env)
            if path:
                gitignores.append([env, path])

        if not gitignores:
            return

        gi_envs = ', '.join(click.style(z[0], fg='green') for z in gitignores)
        click.echo(f'begin update gitignore for envs: {gi_envs}')

        sb = []
        for gii in gitignores:
            env, path = gii
            url = f'https://github.com/github/gitignore/raw/master/{path}'
            sb.append('#' * 100)
            sb.append('#' * 5 + f'  gitignore for {env}')
            sb.append('#' * 5 + f'  url: {url}')
            sb.append('#' * 100)
            sb.append('')
            url_s = click.style(url, fg='green')
            click.echo(f'   http get {url_s} ...')
            r = requests.get(url)
            if r.status_code != 200:
                sc = click.style(str(r.status_code), fg='red')
                self._ctx.fail('status code {sc} when gets ' +
                    click.style(url, fg='green'))
            sb.append(r.text)
            sb.append('')
            sb.append('')

        doc = '\n'.join(sb)
        self._get_gitignore_file().write_text(doc, append=False)

        click.echo(f'updated gitignore for envs: {gi_envs}')
