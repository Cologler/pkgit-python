# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import List

from click import Context, get_current_context
import fsoopify
import execode
from anyioc.g import get_namespace_provider

from ..core.conf import PkgitConf

ioc = get_namespace_provider()

_builder_classes = {}

class IEnvBuilder:
    def __init__(self, ctx, conf):
        self._ctx: Context = ctx
        self._conf: PkgitConf = conf

    def __init_subclass__(cls):
        if cls.__init__ is not IEnvBuilder.__init__:
            raise TypeError

        _builder_classes.setdefault(cls.env, []).append(cls)

    @staticmethod
    def get_builders_for_env(env, ctx, conf):
        classes = _builder_classes.get(env, ())
        return [cls(ctx, conf) for cls in classes]

    @staticmethod
    def get_builders(ctx, conf) -> List['IEnvBuilder']:
        local_conf = conf.get_local_conf()
        builders = []
        for env in local_conf.get('envs', ()):
            builders.extend(IEnvBuilder.get_builders_for_env(env, ctx, conf))
        return builders

    # exec core

    def invoke(self, command: str):
        pass

    def _fallback_invoke(self, command: str):
        '''
        if subclass does not override the method, fallback to call `invoke()`
        '''
        if getattr(type(self), command) is getattr(IEnvBuilder, command):
            return self.invoke(command)

    def init(self):
        return self._fallback_invoke('init')

    def update(self):
        return self._fallback_invoke('update')

    # helpers

    def get_envs(self) -> list:
        '''get envs list from conf'''
        local_conf = self._conf.get_local_conf()
        return local_conf.get('envs', ())

    def get_cwd_path(self) -> fsoopify.Path:
        '''get cwd path for the proj'''
        return ioc['cwd']

    def get_cwd(self) -> fsoopify.DirectoryInfo:
        '''get cwd for the proj'''
        return fsoopify.DirectoryInfo(self.get_cwd_path())


class BuilderCollection:
    def __init__(self, builders: List[IEnvBuilder]):
        self._builders = builders

    def __iter__(self):
        return iter(self._builders)

    def init(self):
        for builder in self._builders:
            builder.init()

    def update(self):
        for builder in self._builders:
            builder.update()

    @staticmethod
    def from_env(env, ctx=None, conf=None):
        ''' get builders from env '''
        if ctx is None:
            ctx = get_current_context()
        if conf is None:
            conf = ioc[PkgitConf]

        classes = _builder_classes.get(env, ())
        return BuilderCollection([cls(ctx, conf) for cls in classes])

    @staticmethod
    def from_conf(ctx=None, conf=None):
        ''' get builders from all envs in conf '''
        if ctx is None:
            ctx = get_current_context()
        if conf is None:
            conf = ioc[PkgitConf]

        local_conf = conf.get_local_conf()
        builders = []
        for env in local_conf.get('envs', ()):
            builders.extend(BuilderCollection.from_env(env, ctx, conf))
        return BuilderCollection(builders)


env_builders_dir = fsoopify.Path.from_caller_file().dirname

for f in fsoopify.DirectoryInfo(env_builders_dir).list_items():
    if f.node_type == fsoopify.NodeType.file:
        if f.path.name != '__init__.py':
            execode.exec_pkg_py(f.path)
