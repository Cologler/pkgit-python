# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from enum import IntEnum, auto
from itertools import chain
from collections import defaultdict

_declared_items = []
_declared_items_aliases = {}
_declared_items_grouped = defaultdict(set)

class Groups(IntEnum):
    LANGUAGE = auto()
    DEV_TOOL = auto()
    FRAMEWORK = auto()


def declare(fullname, *alias, group=None):
    if group is not None:
        _declared_items_grouped[group].add(fullname)

    _declared_items.append(fullname)

    for name in chain([fullname], alias):
        assert name not in _declared_items_aliases
        _declared_items_aliases[name] = fullname

    return fullname

def get_env(key, d=None):
    '''
    try get env from key
    '''
    return _declared_items_aliases.get(key, d)

def get_all_envs():
    '''
    get a list of declared envs
    '''
    return _declared_items.copy()

class Envs:
    # version control system
    GIT = declare('git')
    SVN = declare('svn')

    # runtime
    NODE = declare('node')

    # language
    PYTHON = declare('python', 'py', group=Groups.LANGUAGE)
    TYPE_SCRIPT = declare('typescript', 'ts', group=Groups.LANGUAGE)
    JAVA_SCRIPT = declare('javascript', 'js', group=Groups.LANGUAGE)

    # editor or IDE
    VSCODE = declare('vscode', 'vsc')

    # dev-tool
    PIPENV = declare('pipenv', group=Groups.DEV_TOOL)

    # framework
    PYTEST = declare('pytest', group=Groups.FRAMEWORK)

    # ci
    TRAVIS_CI = declare('travis-ci')
    AZURE_PIPELINES = declare('azure-pipelines')


class Environments(Envs):

    @staticmethod
    def filter_by_group(envs: list, group):
        ge = _declared_items_grouped[group]
        return [e for e in envs if e in ge]
