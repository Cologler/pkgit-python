# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import contextlib

import click

class Printer:
    def __init__(self, prefix='', indent='   ', indent_level=0):
        self._prefix = prefix
        self._indent = indent
        self._indent_level = indent_level
        self.header = None
        self._is_header_printed = False

    @contextlib.contextmanager
    def scoped(self, header=None):
        old_state: dict = {
            'header': self.header,
            '_is_header_printed': self._is_header_printed
        }

        self.header = header
        self._indent_level += 1
        self._is_header_printed = False
        yield self
        self._indent_level -= 1
        vars(self).update(old_state)

    def _get_total_prefix(self, level):
        return self._prefix + (self._indent * (self._indent_level + level))

    def _ensure_echo_header(self):
        if not self._is_header_printed:
            if self.header:
                prefix = self._get_total_prefix(0)
                header = click.style(self.header, fg='bright_cyan', dim=True) + ':'
                click.echo(prefix + header)
            self._is_header_printed = True

    def echo(self, message: str, *args, **kwargs):
        self._ensure_echo_header()
        prefix = self._get_total_prefix(1)
        lines = [m for m in message.splitlines()]
        lines = [prefix + l for l in lines]
        click.echo('\n'.join(lines), *args, **kwargs)
