# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from click import style, prompt

from . import IEnvBuilder, declare_requires
from ..core.envs import Envs

from ..utils.proc_reader import yield_from_proc

declare_requires(Envs.PIPENV, Envs.PYTHON)

PIPFILE_NAME = 'Pipfile'

class PipenvEnvBuilder(IEnvBuilder):
    env = Envs.PIPENV

    def fix_env(self):
        if Envs.PIPENV not in self.get_envs():
            if self.get_cwd().get_fileinfo(PIPFILE_NAME).is_file():
                self.echo(
                    'added env {} because of found file {}'.format(
                        style(Envs.PIPENV, fg='green'),
                        style(PIPFILE_NAME, fg='green')
                    )
                )
                self.add_envs(Envs.PIPENV)

    def _list_installed(self, dev: bool) -> list:
        fileinfo = self.get_cwd().get_fileinfo(PIPFILE_NAME)
        if fileinfo.is_file():
            data: dict = fileinfo.load()
            part: dict = data.get('develop') if dev else data.get('default')
            if part:
                return list(part)
        return []

    def _install_from_pipenv(self, package_name: str, **kwargs):
        with self._printer.scoped(self.env):
            args = ['pipenv', 'install', package_name]
            dev = kwargs.get('dev', False)
            if package_name in self._list_installed(dev):
                return self.echo('Ignore install {} because of it was installed ready.'.format(
                    style(package_name, fg='green'),
                ))

            if dev:
                args.append('--dev')

            with self.open_proc(args, stdout=True, stderr=True) as proc:
                progress_msg = set()
                for src, line in yield_from_proc(proc):
                    line: bytes

                    if src == 'stderr':
                        if line[:1] == b'[' and line[5:6] == b']':
                            # ignore progress bar
                            line = line[7:].rstrip(b'\x08')
                            if line in progress_msg:
                                continue
                            progress_msg.add(line)
                        line = line.lstrip(b'\x08')

                    self._printer.echo_line_for_subproc(line)

    def conf_ioc(self):
        self._ioc.register_value('install-python-package', self._install_from_pipenv)
