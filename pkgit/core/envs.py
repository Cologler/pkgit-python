# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from itertools import chain

_declared_items = []
_declared_items_aliases = {}

def declare(fullname, *alias):
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
    PYTHON = declare('python', 'py')
    TYPE_SCRIPT = declare('typescript', 'ts')
    JAVA_SCRIPT = declare('javascript', 'js')

    # editor or IDE
    VSCODE = declare('vscode', 'vsc')

    # dev-tool
    PIPENV = declare('pipenv')

    # framework
    PYTEST = declare('pytest')

    # ci
    TRAVIS_CI = declare('travis-ci')
    AZURE_PIPELINES = declare('azure-pipelines')
