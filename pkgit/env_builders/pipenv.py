# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from . import IEnvBuilder, declare_env_requires
from ..core.envs import Envs

declare_env_requires(Envs.PIPENV, Envs.PYTHON)
