# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from click import style, prompt

from . import IEnvBuilder, declare_requires
from ..core.envs import Envs

declare_requires(Envs.PIPENV, Envs.PYTHON)

class PipenvEnvBuilder(IEnvBuilder):
    env = Envs.PIPENV

    def fix_env(self):
        if Envs.PIPENV not in self.get_envs():
            name = 'Pipfile'
            if self.get_cwd().get_fileinfo(name).is_file():
                self.echo(
                    'added env {} because of found file {}'.format(
                        style(Envs.PIPENV, fg='green'),
                        style(name, fg='green')
                    )
                )
                self.add_envs(Envs.PIPENV)

    def _install_from_pipenv(self, package_name: str, **kwargs):
        self._printer.header = self.env

        args = ['pipenv', 'install', package_name]
        if kwargs.get('dev', False):
            args.append('--dev')

        with self.open_proc(args, stdout=True) as proc:
            # pipenv use stderr as stdout
            # just read and ignore
            buf = proc.stderr.read()

    def init(self):
        self._ioc.register_value('install-python-package', self._install_from_pipenv)
