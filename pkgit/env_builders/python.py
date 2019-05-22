# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from . import IEnvBuilder
from ..core.envs import Envs

class PythonEnvBuilder(IEnvBuilder):
    env = Envs.PYTHON

    def _install_from_pip(self, package_name: str, **kwargs):
        pass

    def init(self):
        self._ioc.register_value('install-python-package', self._install_from_pip)
