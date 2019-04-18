# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import fsoopify
import click
import datetime

from ..core import pkgit_ioc, PkgitConf

class Licenses:
    MIT = 'MIT License'

    Map = {
        'mit': MIT
    }

    @classmethod
    def try_parse(cls, value: str):
        ret = cls.Map.get(value.lower())
        return ret


def set_new_license(ctx: click.Context, conf: PkgitConf, new_lice):
    local_conf = conf.get_local_conf()
    lice = Licenses.try_parse(new_lice)
    if not lice:
        ctx.fail('Unable to parse license: ' + click.style(license, fg='green'))
    local_conf['license'] = lice
    conf.mark_local_changed()


def update_license(ctx: click.Context, conf: PkgitConf):
    local_conf = conf.get_local_conf()
    lice = local_conf.get('license')
    if not lice:
        return

    lice_path = fsoopify.Path(__file__).dirname.dirname / 'data' / 'licenses' / f'{lice}.txt'
    lice_temp = fsoopify.FileInfo(lice_path).read_text()
    author = conf.proxy_get('author')
    lice_cont = lice_temp.format_map({
        'year': str(datetime.datetime.now().year),
        'author': author,
    })
    fsoopify.FileInfo('LICENSE').write_text(lice_cont, append=False)


class License:
    '''sub commands for license'''

    def update(self, ctx: click.Context, license=None):
        '''
        update local LICENSE file.

        if argument license is set, will change the license.
        '''
        conf: PkgitConf = pkgit_ioc.get(PkgitConf)
        if license:
            set_new_license(ctx, conf, license)
        update_license(ctx, conf)
        conf.save()
