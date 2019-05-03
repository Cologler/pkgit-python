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
    runtime = auto() # runtime
    lang = auto()
    editor = auto()
    tool = auto()
    framework = auto()

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

class VCS(BaseEnv):
    kind = EnvKind.vcs

    GIT = 'git'

class Runtimes(BaseEnv):
    kind = EnvKind.runtime

    NODE = 'node'

class Languages(BaseEnv):
    kind = EnvKind.lang

    PYTHON = 'python'
    TYPE_SCRIPT = 'typescript'
    JAVA_SCRIPT = 'javascript'

class Editors(BaseEnv):
    kind = EnvKind.editor

    VSCODE = 'vscode'

class Tools(BaseEnv):
    kind = EnvKind.tool

    PIPENV = 'pipenv'

class Frameworks(BaseEnv):
    kind = EnvKind.framework

    PYTEST = 'pytest'

class Envs(VCS, Runtimes, Languages, Editors, Tools, Frameworks):
    map: Dict[str, str] = None

Envs.map = dict((v, v) for v in Envs.values())
Envs.map['vsc'] = Editors.VSCODE
Envs.map['py'] = Languages.PYTHON
Envs.map['ts'] = Languages.TYPE_SCRIPT
Envs.map['js'] = Languages.JAVA_SCRIPT

EnvVal = namedtuple('EnvVal', ['kind', 'value'])

def to_envval(env: str):
    for envs in Envs.__bases__:
        if env in envs.values():
            kind = envs.kind
    return EnvVal(kind, env)
