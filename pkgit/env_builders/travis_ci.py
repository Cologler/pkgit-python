# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from . import IEnvBuilder
from ..core.envs import Envs, Environments, Groups

class TravisCIBuilder(IEnvBuilder):
    env = Environments.TRAVIS_CI

    def init(self):
        envs = self.get_envs()
        envs_as_set = set(envs)
        langs = Environments.filter_by_group(envs, Groups.LANGUAGE)

        if len(langs) > 1:
            return self._ctx.fail(f'too many language: {", ".join(langs)}')

        if len(langs) == 1:
            travis_yml = self.get_cwd().get_fileinfo('.travis.yml')

            conf = {}
            lang = langs[0]
            if lang == Environments.PYTHON:
                proj_kind: str = self._ioc.get('proj-kind')

                conf.update(
                    dict(
                        language='python',
                        dist='xenial',
                        sudo=True,
                        python=['3.7']
                    )
                )

                # install
                install = []
                if Environments.PIPENV in envs_as_set:
                    install.append('pipenv install --dev')
                if install:
                    conf['install'] = install

                # script
                script = []
                if Environments.PYTEST in envs_as_set:
                    script.append('python -m pytest')
                if not script:
                    script.append('python setup.py test')
                if script:
                    conf['script'] = script

                # deploy
                if proj_kind == 'package':
                    deploy = dict(
                        provider='pypi',
                        user='$PYPI_USER',
                        password='$PYPI_PASSWORD',
                        distributions='sdist bdist_wheel',
                        skip_existing=True,
                        on=dict(
                            tags=True
                        )
                    )
                    conf['deploy'] = deploy

                travis_yml.dump(conf, kwargs=dict(
                    indent=2,
                    default_flow_style=False
                ))
