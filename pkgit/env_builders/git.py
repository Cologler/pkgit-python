# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import fsoopify
from click import style

from . import IEnvBuilder
from ..utils import lazy
from ..core.ioc import pkgit_ioc
from ..core.envs import Envs

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

    def fix_env(self):
        if Envs.GIT not in self.get_envs():
            git_dir_name = '.git'
            if self.get_cwd().get_dirinfo(git_dir_name).is_directory():
                self.echo(
                    'added env {} because of found dir {}'.format(
                        style(Envs.GIT, fg='green'),
                        style(git_dir_name, fg='green')
                    )
                )
                self.add_envs(Envs.GIT)


class GitIgnoreEnvBuilder(IEnvBuilder):
    env = Envs.GIT

    def _get_gitignore_file(self):
        return fsoopify.FileInfo(pkgit_ioc['cwd'] / '.gitignore')

    def init(self):
        if self._get_gitignore_file().is_file():
            self.echo(f'ignore update gitignore since it is exists')
            return
        self.update()

    def update(self):
        import requests

        local_conf = self._conf.get_local_conf()
        gitignore_map: dict = gitignore_map_factory()

        gitignores = []
        for env in local_conf.get('envs', ()):
            path = gitignore_map.get(env)
            if path:
                gitignores.append([env, path])

        if not gitignores:
            return

        gi_envs = ', '.join(style(z[0], fg='green') for z in gitignores)
        self.echo(f'begin update gitignore for envs: {gi_envs}')

        sb = []
        for gii in gitignores:
            env, path = gii
            url = f'https://github.com/github/gitignore/raw/master/{path}'
            sb.append('#' * 100)
            sb.append('#' * 5 + f'  gitignore for {env}')
            sb.append('#' * 5 + f'  url: {url}')
            sb.append('#' * 100)
            sb.append('')
            url_s = style(url, fg='green')
            self.echo(f'   http get {url_s} ...')
            r = requests.get(url)
            if r.status_code != 200:
                sc = style(str(r.status_code), fg='red')
                self._ctx.fail('status code {sc} when gets ' +
                    style(url, fg='green'))
            sb.append(r.text)
            sb.append('')
            sb.append('')

        doc = '\n'.join(sb)
        self._get_gitignore_file().write_text(doc, append=False)

        self.echo(f'updated gitignore for envs: {gi_envs}')
