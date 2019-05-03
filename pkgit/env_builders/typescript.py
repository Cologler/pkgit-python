# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import subprocess

from ..core.envs import Envs
from . import IEnvBuilder

class TypeScriptBuilder(IEnvBuilder):
    env = Envs.TYPE_SCRIPT

    def _tsc_run(self, args: list):
        args = ['tsc'] + args
        return subprocess.run(args,
            cwd=str(self.get_cwd_path()), shell=True
        )

    def init(self):
        cp = self._tsc_run(['--init'])
        if cp.returncode != 0:
            return

