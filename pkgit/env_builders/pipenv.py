# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from click import style

from . import IEnvBuilder, declare_requires
from ..core.envs import Envs

declare_requires(Envs.PIPENV, Envs.PYTHON)

class PipenvEnvBuilder(IEnvBuilder):
    env = Envs.GIT

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
