# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import subprocess
from contextlib import contextmanager

from click import style

from ..core.envs import Envs
from . import IEnvBuilder

class TypeScriptBuilder(IEnvBuilder):
    env = Envs.TYPE_SCRIPT

    @contextmanager
    def _open_tsc(self, args: list):
        args = ['tsc'] + args
        self.echo('run proc ' + style(str(args), fg='magenta'))
        yield subprocess.Popen(args,
            cwd=str(self.get_cwd_path()), shell=True, encoding='utf-8',
            stdout=subprocess.PIPE
        )
        self.echo('end proc ' + style(str(args), fg='magenta'))

    def init(self):
        with self._open_tsc(['--init']) as proc:
            for line in proc.stdout:
                self.echo('    ' + line)
            proc.wait()

