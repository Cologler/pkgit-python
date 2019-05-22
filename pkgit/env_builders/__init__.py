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
from ..core.deps import get_requires, declare_requires

ioc = get_namespace_provider()

_builders = {}
_builders_fix_env = []

class IEnvBuilder:
    env: str = None # require overwrite on subclass
    requires_envs: Tuple[str, ...] = ()

    def __init__(self, ctx, conf):
        self._ctx: Context = ctx
        self._conf: PkgitConf = conf
        self._echoed = False

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

    def echo(self, message: str, *args, **kwargs):
        if not self._echoed:
            echo('   {}:'.format(style(self.env, fg='bright_cyan', dim=True)))
            self._echoed = True
        lines = [m for m in message.splitlines()]
        lines = [f'      {l}' for l in lines]
        echo('\n'.join(lines), *args, **kwargs)


class BuilderCollection:
    def __init__(self, *, env, ctx, conf):
        self._env = env
        self._ctx: Context = ctx
        self._conf: PkgitConf = conf

    def __iter__(self):
        return iter(self._get_builders())

    def fix_env(self):
        echo(
            'prepare ...'
        )

        ctx = self._ctx
        conf = self._conf

        for builder in [cls(ctx, conf) for cls in _builders_fix_env]:
            builder.fix_env()

        local_conf = conf.get_local_conf()
        envs = set(local_conf.get('envs', ()))
        deps = {}
        for env in envs:
            requires = get_requires(env).get_requires_chain()
            for new in (requires - envs):
                deps.setdefault(new, []).append(env)
        if deps:
            echo('   {}:'.format(style('deps', fg='bright_cyan', dim=True)))
            for dep, dep_src in deps.items():
                echo(
                    '      added env {} because of env {} require it'.format(
                        style(new, fg='green'),
                        ', '.join([style(x, fg='green') for x in dep_src])
                    )
                )
            envs.update(deps)
            local_conf['envs'] = list(envs)

    def init(self):
        self._invoke_command('init')

    def update(self):
        self._invoke_command('update')

    def _invoke_command(self, command):
        envs = self._get_envs()
        self._print_envs(envs, command)
        for builder in self._get_builders():
            getattr(builder, command)()

    def _print_envs(self, envs, command):
        echo(
            f'{command} for envs: ' +\
            ', '.join([style(x, fg='green') for x in envs])
        )

    def _get_envs(self):
        if self._env is None:
            return self._conf.get_local_conf().get('envs', ())
        else:
            return [self._env]

    def _get_builders(self, envs: list=None):
        ctx = self._ctx
        conf = self._conf
        if envs is None:
            envs = self._get_envs()

        deps = {}
        for env in envs:
            deps[env] = get_requires(env).get_requires()
        def order(item):
            return len(deps[item])
        envs = sorted(envs, key=order) # ensure deps order

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
