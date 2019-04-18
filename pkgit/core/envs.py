# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from enum import Enum

class Envs:
    VSCODE = 'vscode'
    PYTHON = 'python'
    PIPENV = 'pipenv'

def get_envs_values():
    d = dict(vars(Envs))
    for k in list(k for k in d.keys() if k[:1] == '_'):
        d.pop(k)
    return d

EnvsValues = get_envs_values()


ENVS_MAP = dict((v, v) for v in vars(Envs).values())
ENVS_MAP['vsc'] = Envs.VSCODE
ENVS_MAP['py'] = Envs.PYTHON
