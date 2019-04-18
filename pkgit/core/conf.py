# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from fsoopify import Path, NodeInfo, FileInfo, DirectoryInfo
from fsoopify.utils import gettercache
from anyioc.utils import inject_by_name

from .ioc import pkgit_ioc

CONF_NAMES = ('.pkgit.json', '.pkgit.yaml')


class PkgitConf:
    def __init__(self, cwd):
        self._local_file = self._get_exists_or_first(
            NodeInfo.from_path(cwd), CONF_NAMES
        )
        self._global_file = self._get_exists_or_first(
            NodeInfo.from_path(Path.from_home()), CONF_NAMES
        )
        self._local_conf: dict = None
        self._global_conf: dict = None
        self._is_local_new: bool = None
        self._local_changed = False

    def _get_exists_or_first(self, root: DirectoryInfo, names: tuple):
        for name in names:
            fi = root.get_fileinfo(name)
            if fi.is_file():
                return fi
        return root.get_fileinfo(names[0])

    @property
    def is_local_new(self):
        return self._is_local_new

    def create_local(self) -> bool:
        if self._local_conf.is_file():
            return False
        self._is_local_new = True
        self._local_conf.dump({})
        return True

    def _load_dict(self, file: FileInfo):
        if file.is_file():
            return file.load()
        else:
            return {}

    @gettercache
    def get_local_conf(self) -> dict:
        if self._local_file.is_file():
            self._is_local_new = False
            return self._local_file.load()
        else:
            self._is_local_new = True
            return {}

    @gettercache
    def get_global_conf(self) -> dict:
        if self._global_file.is_file():
            return self._global_file.load()
        else:
            return {}

    def mark_local_changed(self):
        self._local_changed = True

    def save(self):
        if self._is_local_new or self._local_changed:
            self._local_file.dump(self.get_local_conf())


pkgit_ioc.register_singleton(PkgitConf, inject_by_name(PkgitConf))
