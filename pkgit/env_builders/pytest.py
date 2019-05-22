# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from . import IEnvBuilder, declare_requires
from ..core.envs import Envs

declare_requires(Envs.PYTEST, Envs.PYTHON)

class PyTestEnvBuilder(IEnvBuilder):
    env = Envs.PYTEST

    def update_for_vscode(self):
        cwd = self.get_cwd()
        vscode = cwd.get_dirinfo('.vscode')
        launch = vscode.get_fileinfo('launch.json')
        if launch.is_file():
            launch_c = launch.load()
        else:
            launch_c = {}
        launch_c.setdefault('version', '0.2.0')
        configurations = launch_c.setdefault('configurations', [])
        for c in configurations:
            if (c.get('type'), c.get('request'), c.get('module')) == ('python', 'launch', 'pytest'):
                return
        configurations.append({
            "name": "pypit: pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest"
        })

        vscode.ensure_created()
        launch.dump(launch_c)

        self.echo('create pytest launcher for vscode')

    def init(self):
        envs = self.get_envs()
        if Envs.VSCODE in envs:
            self.update_for_vscode()


