# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import subprocess
from contextlib import contextmanager
from typing import List, Tuple

from click import Context, get_current_context, echo, style
import fsoopify
import execode
from anyioc import ServiceProvider
from anyioc.g import get_namespace_provider

from ..core.conf import PkgitConf
from ..core.deps import get_requires, declare_requires, sort_envs, declare_order
from ..utils.echo import Printer

ioc = get_namespace_provider()

_builders = {}
_builders_fix_env = []

class IEnvBuilder:
    env: str = None # require overwrite on subclass
    requires_envs: Tuple[str, ...] = ()

    def __init__(self, ctx, conf, ioc, printer):
        self._ctx: Context = ctx
        self._conf: PkgitConf = conf
        self._ioc: ServiceProvider = ioc
        self._printer: Printer = printer

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
        try to use the `IEnvBuilder` to fill the missing envs.
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

    def conf_ioc(self):
        '''
        run before any command like `init`, `update` to config `self._ioc`.
        '''
        return self._fallback_invoke('conf_ioc')

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

    @contextmanager
    def open_proc(self, args: List[str], *, stdout=False, stderr=False, encoding=None):
        '''
        if `stdout` or `stderr` set to `True`, mean caller will handle the output.
        '''

        self.echo('run proc ' + style(str(args), fg='bright_magenta'))

        proc = subprocess.Popen(args,
            cwd=str(self.get_cwd_path()), shell=True, encoding=encoding,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        yield proc

        def echo_stream(stream):
            for line in stream:
                if not encoding:
                    try:
                        line = line.decode('utf-8', 'ignore')
                    except UnicodeDecodeError:
                        pass # keep print bytes
                self._printer.echo(f'    {line}')
        if not stdout:
            echo_stream(proc.stdout)
        if not stderr:
            echo_stream(proc.stderr)

        code = proc.wait()
        self.echo(f'end proc with code {code}')

    def echo(self, message: str, **kwargs):
        return self._printer.echo(message, **kwargs)


class BuilderCollection:
    def __init__(self, *, env, ctx, conf):
        self._env = env
        self._ctx: Context = ctx
        self._conf: PkgitConf = conf
        self._ioc = ioc.scope()
        self._printer = Printer()

    def _make_builder(self, builder_class: type) -> IEnvBuilder:
        return builder_class(
            self._ctx,
            self._conf,
            self._ioc,
            self._printer
        )

    def fix_env(self):
        echo('prepare ...')

        conf = self._conf

        for builder in [self._make_builder(cls) for cls in _builders_fix_env]:
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
        envs = sort_envs(self._get_envs())
        self._print_envs(envs, command)

        builders = self._get_builders(envs)

        for builder in builders:
            with self._printer.scoped(f'{builder.env} (conf step)'):
                builder.conf_ioc()

        for builder in builders:
            with self._printer.scoped(f'{builder.env} ({command} step)'):
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

    def _get_builders(self, envs: list) -> List[IEnvBuilder]:
        builders = []
        for env in envs:
            clses = _builders.get(env, ())
            builders.extend([self._make_builder(cls) for cls in clses])
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
