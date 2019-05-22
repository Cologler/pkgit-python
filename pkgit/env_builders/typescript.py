# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from click import style

from ..core.envs import Envs
from . import IEnvBuilder

class TypeScriptBuilder(IEnvBuilder):
    env = Envs.TYPE_SCRIPT

    def init(self):
        with self.open_proc(['tsc', '--init']):
            pass

