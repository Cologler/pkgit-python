# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from typing import List, Tuple

from click import Context, get_current_context, echo, style
import fsoopify
import execode
from anyioc.g import get_namespace_provider

from ..core.conf import PkgitConf

ioc = get_namespace_provider()

_requires_envs = {}

def declare_env_requires(env, *require_envs):
    s: set = _requires_envs.setdefault(env, set())
    assert isinstance(require_envs, tuple)
    s.update(require_envs)

def get_env_requires(env) -> List[str]:
    return frozenset(_requires_envs.get(env, ()))

_builders = {}
_builders_fix_env = []

class IEnvBuilder:
    env: str = None # require overwrite on subclass
    requires_envs: Tuple[str, ...] = ()

    def __init__(self, ctx, conf):
        self._ctx: Context = ctx
        self._conf: PkgitConf = conf

    def __init_subclass__(cls):
        if cls.__init__ is not IEnvBuilder.__init__:
            raise TypeError(f'{cls} should not override __init__()')

        # for env
        env = cls.env
        if env is None:
            raise TypeError(f'{cls} should overwrite class var env')
        _builders.setdefault(env, []).append(cls)

        # for fix_env
        if cls.fix_env is not IEnvBuilder.fix_env:
            _builders_fix_env.append(cls)

    # exec core

    def fix_env(self):
        '''
        fix env.
        '''
        pass

    def invoke(self, command: str):
        pass

    def _fallback_invoke(self, command: str):
        '''
        if subclass does not override the method, fallback to call `invoke()`
        '''
        if getattr(type(self), command) is getattr(IEnvBuilder, command):
            return self.invoke(command)

    def init(self):
        'init env'
        return self._fallback_invoke('init')

    def update(self):
        'update env'
        return self._fallback_invoke('update')

    # helpers

    def get_envs(self) -> list:
        '''get envs list from conf'''
        local_conf = self._conf.get_local_conf()
        return local_conf.get('envs', ())

    def add_envs(self, *envs):
        '''add envs to conf'''
        local_conf = self._conf.get_local_conf()
        local_conf.setdefault('envs', []).extend(envs)

    def get_cwd_path(self) -> fsoopify.Path:
        '''get cwd path for the proj'''
        return ioc['cwd']

    def get_cwd(self) -> fsoopify.DirectoryInfo:
        '''get cwd for the proj'''
        return fsoopify.DirectoryInfo(self.get_cwd_path())


class BuilderCollection:
    def __init__(self, *, env, ctx, conf):
        self._env = env
        self._ctx: Context = ctx
        self._conf: PkgitConf = conf

    def __iter__(self):
        return iter(self._get_builders())

    def fix_env(self):
        ctx = self._ctx
        conf = self._conf

        for builder in [cls(ctx, conf) for cls in _builders_fix_env]:
            builder.fix_env()

        local_conf = conf.get_local_conf()
        envs_src = local_conf.get('envs', ())
        envs_set = set(envs_src)
        for env in envs_src:
            requires = get_env_requires(env)
            for new in (requires - envs_set):
                echo(
                    'added env {} because env {} require it'.format(
                        style(new, fg='green'),
                        style(env, fg='green')
                    )
                )
            envs_set.update(get_env_requires(env))
        if len(envs_set) > len(envs_src):
            local_conf['envs'] = list(envs_set)

    def init(self):
        for builder in self._get_builders():
            builder.init()

    def update(self):
        for builder in self._get_builders():
            builder.update()

    def _get_builders(self, from_env=True):
        ctx = self._ctx
        conf = self._conf

        if self._env is None:
            envs = conf.get_local_conf().get('envs', ())
        else:
            envs = [self._env]

        builders = []
        for env in envs:
            clses = _builders.get(env, ())
            builders.extend([cls(ctx, conf) for cls in clses])
        return builders

    @staticmethod
    def from_env(env, ctx=None, conf=None):
        ''' get builders from env '''
        if ctx is None:
            ctx = get_current_context()
        if conf is None:
            conf = ioc[PkgitConf]

        return BuilderCollection(env=env, ctx=ctx, conf=conf)

    @staticmethod
    def from_conf(ctx=None, conf=None):
        ''' get builders from all envs in conf '''
        if ctx is None:
            ctx = get_current_context()
        if conf is None:
            conf = ioc[PkgitConf]

        return BuilderCollection(env=None, ctx=ctx, conf=conf)


env_builders_dir = fsoopify.Path.from_caller_file().dirname

for f in fsoopify.DirectoryInfo(env_builders_dir).list_items():
    if f.node_type == fsoopify.NodeType.file:
        if f.path.name != '__init__.py':
            execode.exec_pkg_py(f.path)
