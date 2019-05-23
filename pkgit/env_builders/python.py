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
        with self._printer.scoped(self.env):
            self._printer.echo('ignore install {} because this is global env. you should install it manual.'.format(
                style(package_name, fg='green')
            ))

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
        proj_kind: str = self._ioc['proj-kind']
        if proj_kind == 'package':
            self._init_package()

    def _init_package(self):
        use_setupmeta_builder = self._printer.prompt_yn('did you want to use {}?'.format(
            style('setupmeta-builder', fg='green')
        ))
        if use_setupmeta_builder:
            self.echo('invoke install setupmeta-builder:')
            self._ioc['install-python-package']('setupmeta-builder', dev=True)

        setup = self.get_cwd().get_fileinfo('setup.py')
        if not setup.is_file():
            if use_setupmeta_builder:
                self.echo(f'create {setup.path.name}')
                setup_cont = '\n'.join([
                    'from setupmeta_builder import setup_it', '', 'setup_it()'
                ])
                setup.write_text(setup_cont)

        # make dir for package
        package_name = str(self.get_cwd_path().name)
        if package_name.endswith('-python'):
            package_name = package_name[:-7]
        package_dir = self.get_cwd().get_dirinfo(package_name)
        if not package_dir.is_directory():
            self.echo('create dir {} for package'.format(
                package_name
            ))
            package_dir.create()
            self.echo('create file {}/{} for package'.format(
                package_name, '__init__.py'
            ))
            package_dir.get_fileinfo('__init__.py').write_text('')
