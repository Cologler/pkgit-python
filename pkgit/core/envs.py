# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from enum import IntEnum, auto
from typing import Set, Dict
from collections import namedtuple

class EnvKind(IntEnum):
    vcs =  auto() # version control system
    lang = auto()
    editor = auto()
    tool = auto()

class BaseEnv:
    @classmethod
    def values(cls) -> Set[str]:
        try:
            return getattr(cls, '_value')
        except AttributeError:
            s = set()
            for n in dir(cls):
                if n[:1] != '_' and n != 'values':
                    v = getattr(cls, n)
                    if isinstance(v, str):
                        s.add(v)
            setattr(cls, '_value', s)
            return s

class VersionControlSystem:
    kind = EnvKind.vcs

    GIT = 'git'

class Languages(BaseEnv):
    kind = EnvKind.lang

    PYTHON = 'python'

class Editors(BaseEnv):
    kind = EnvKind.editor

    VSCODE = 'vscode'

class Tools(BaseEnv):
    kind = EnvKind.tool

    PIPENV = 'pipenv'

class Envs(VersionControlSystem, Languages, Editors, Tools):
    map: Dict[str, str] = None

Envs.map = dict((v, v) for v in Envs.values())
Envs.map['vsc'] = Editors.VSCODE
Envs.map['py'] = Languages.PYTHON

EnvVal = namedtuple('EnvVal', ['kind', 'value'])

def to_envval(env: str):
    for envs in Envs.__bases__:
        if env in envs.values():
            kind = envs.kind
    return EnvVal(kind, env)
