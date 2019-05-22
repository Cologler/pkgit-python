# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from itertools import chain
from enum import IntEnum, auto
from typing import Set, Dict
from collections import namedtuple

from ..utils.caching import cache_on_dict

_declared_items = {}

def declare(fullname, *alias):
    for name in chain([fullname], alias):
        assert name not in _declared_items
        _declared_items[name] = fullname
    return fullname

def get_env(key, d=None):
    return _declared_items.get(key, d)

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

    GIT = declare('git')
    SVN = declare('svn')

class Runtimes(BaseEnv):
    kind = EnvKind.runtime

    NODE = declare('node')

class Languages(BaseEnv):
    kind = EnvKind.lang

    PYTHON = declare('python', 'py')
    TYPE_SCRIPT = declare('typescript', 'ts')
    JAVA_SCRIPT = declare('javascript', 'js')

class Editors(BaseEnv):
    kind = EnvKind.editor

    VSCODE = declare('vscode', 'vsc')

class Tools(BaseEnv):
    kind = EnvKind.tool

    PIPENV = declare('pipenv')

class Frameworks(BaseEnv):
    kind = EnvKind.framework

    PYTEST = declare('pytest')

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
