# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import os
import sys
import traceback

import click
from click_anno import click_app
from fsoopify import Path, DirectoryInfo

from .cmds.init import init
from .cmds.git import Git
from .cmds.license import License

@click_app
class App:
    def __init__(self, ctx: click.Context, root=None):
        if root is None:
            cwd = Path.from_cwd()
        else:
            dirinfo =DirectoryInfo(root)
            if not dirinfo.is_directory():
                ctx.fail(f'{root} is not a dir')
            cwd = dirinfo.path

        from .core.ioc import pkgit_ioc
        pkgit_ioc.register_value('cwd', cwd)

    init = init
    git = Git
    lice = License


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        App()
    except Exception: # pylint: disable=W0703
        traceback.print_exc()

if __name__ == '__main__':
    main()
