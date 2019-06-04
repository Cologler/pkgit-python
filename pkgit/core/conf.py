# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from fsoopify import Path, NodeInfo, FileInfo, DirectoryInfo
from fsoopify.utils import gettercache
from anyioc.utils import inject_by_name
from anyioc.g import get_namespace_provider

ioc = get_namespace_provider()

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
        if self._is_local_new is not None:
            return self._is_local_new
        return not self._local_file.is_file()

    @gettercache
    def get_local_conf(self) -> dict:
        if self._local_file.is_file():
            self._is_local_new = False
            return self._local_file.load()
        else:
            self._is_local_new = True
            return self.get_global_conf().copy()

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
            self._local_file.dump(
                self.get_local_conf(),
                kwargs=dict(
                    ensure_ascii=False,
                    indent=4
                )
            )

    def proxy_get(self, key):
        local_conf = self.get_local_conf()
        if key in local_conf:
            return local_conf[key]
        global_conf = self.get_global_conf()
        if key in global_conf:
            return global_conf[key]
        return None

ioc.register_singleton(PkgitConf, inject_by_name(PkgitConf))
