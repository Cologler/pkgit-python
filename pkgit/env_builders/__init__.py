# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import List

from click import Context
import fsoopify
import execode

from ..core.ioc import pkgit_ioc
from ..core.conf import PkgitConf

class IEnvBuilder:
    _builders = {}

    def __init__(self, ctx, conf):
        self._ctx: Context = ctx
        self._conf: PkgitConf = conf

    def __init_subclass__(cls):
        IEnvBuilder._builders.setdefault(cls.env, []).append(cls)

    @staticmethod
    def get_builders_for_env(env, ctx, conf):
        clses = IEnvBuilder._builders.get(env, ())
        return [c(ctx, conf) for c in clses]

    @staticmethod
    def get_builders(ctx, conf) -> List['IEnvBuilder']:
        local_conf = conf.get_local_conf()
        builders = []
        for env in local_conf.get('envs', ()):
            builders.extend(IEnvBuilder.get_builders_for_env(env, ctx, conf))
        return builders

    def update(self):
        pass

    def init(self):
        pass

    # helpers

    def get_envs(self) -> list:
        '''get envs list from conf'''
        local_conf = self._conf.get_local_conf()
        return local_conf.get('envs', ())

    def get_cwd_path(self) -> fsoopify.Path:
        '''get cwd path for the proj'''
        return pkgit_ioc['cwd']

    def get_cwd(self) -> fsoopify.DirectoryInfo:
        '''get cwd for the proj'''
        return fsoopify.DirectoryInfo(self.get_cwd_path())


env_builders_dir = fsoopify.Path.from_caller_file().dirname

for f in fsoopify.DirectoryInfo(env_builders_dir).list_items():
    if f.node_type == fsoopify.NodeType.file:
        if f.path.name != '__init__.py':
            execode.exec_pkg_py(f.path)
