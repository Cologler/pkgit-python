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
        with self._printer.scoped(self.env):
            args = ['pipenv', 'install', package_name]
            if kwargs.get('dev', False):
                args.append('--dev')

            with self.open_proc(args, stdout=False, stderr=True) as proc:
                pass

    def conf_ioc(self):
        self._ioc.register_value('install-python-package', self._install_from_pipenv)
