# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
# builder for gitignore.json
# ----------

import os
import sys
import traceback
import json

def build_from_local_path(root, parent=None, d=None):
    if d is None:
        d = {}
    if parent:
        parent_fullpath = os.path.join(root, parent)
    else:
        parent_fullpath = root
    dirs = []
    for name in os.listdir(parent_fullpath):
        if name in ['.github', '.git']:
            continue
        sub_node = os.path.join(parent_fullpath, name)
        if os.path.isfile(sub_node):
            if name.endswith('.gitignore'):
                k = name[:-len('.gitignore')]
                if parent:
                    v = '/'.join([parent, name])
                else:
                    v = name
                d[k] = v.replace('\\', '/')
        elif os.path.isdir(sub_node):
            dirs.append(name)
    for name in dirs:
        if parent:
            subp = os.path.join(parent, name)
        else:
            subp = name
        build_from_local_path(root, subp, d)
    return d

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        if len(argv) != 2:
            raise RuntimeError('Need path argument for local gitignore repo')
        d = build_from_local_path(argv[1])
        with open('gitignore.json', encoding='utf-8', mode='w') as fp:
            json.dump(d, fp)
    except Exception: # pylint: disable=W0703
        traceback.print_exc()

if __name__ == '__main__':
    main()
