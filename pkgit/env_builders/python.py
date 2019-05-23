# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from click import style

from . import IEnvBuilder
from ..core.envs import Envs

_PROJ_KINDS = {
    'P': 'package',
    'A': 'app',
    'N': None
}

class PythonEnvBuilder(IEnvBuilder):
    env = Envs.PYTHON

    def _install_from_pip(self, package_name: str, **kwargs):
        pass

    def conf_ioc(self):
        self._ioc.register_value('install-python-package', self._install_from_pip)

        while True:
            proj_kind = self._printer.prompt('did you writing a package or a app? [{}]'.format(
                '/'.join(_PROJ_KINDS)
            ))
            proj_kind = proj_kind.upper()
            if proj_kind in _PROJ_KINDS:
                break
        self._ioc.register_value('proj-kind', _PROJ_KINDS[proj_kind])

    def init(self):
        proj_kind: stt = self._ioc['proj-kind']

        if proj_kind == 'package':
            use_setupmeta_builder = self._printer.prompt_yn('did you want to use {}?'.format(
                style('setupmeta-builder', fg='green')
            ))
            if use_setupmeta_builder:
                self.echo('invoke install setupmeta-builder:')
                self._ioc['install-python-package']('setupmeta-builder', dev=True)
            setup = self.get_cwd().get_fileinfo('setup.py')
            if not setup.is_file():
                self.echo(f'create {setup.path.name}')
                setup_cont = '\n'.join([
                    'from setupmeta_builder import setup_it', '', 'setup_it()'
                ])
                setup.write_text(setup_cont)
