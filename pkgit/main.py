# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import os
import sys
import traceback

from click_anno import click_app

from .cmds.init import init
from .cmds.git import Git
from .cmds.license import License

@click_app
class App:
    init = init
    git = Git
    lice = License


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        from .core.ioc import pkgit_ioc
        from fsoopify import Path
        cwd = Path.from_cwd()
        pkgit_ioc.register_value('cwd', cwd)
        App()
    except Exception: # pylint: disable=W0703
        traceback.print_exc()

if __name__ == '__main__':
    main()
