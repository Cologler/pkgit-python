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

    def _format_message(self, message):
        prefix = self._get_total_prefix(1)
        lines = [m for m in message.splitlines()]
        lines = [prefix + l for l in lines]
        return '\n'.join(lines)

    def echo(self, message: str, **kwargs):
        self._ensure_echo_header()
        click.echo(self._format_message(message), **kwargs)

    def prompt(self, message: str, default=None, type=str, **kwargs):
        self._ensure_echo_header()
        return click.prompt(self._format_message(message),
            default=default, type=type,
            **kwargs)

    def prompt_yn(self, message: str, default=None, **kwargs):
        'prompt yes or no'
        return self.prompt(
            message + ' [Y/N]', default=default, type=bool, **kwargs
        )

    # for subproc

    def echo_stream_for_subproc(self, stream, encoding=None):
        for line in stream:
            self.echo_line_for_subproc(stream, encoding)

    def echo_line_for_subproc(self, line, encoding=None):
        encoding = encoding or 'utf-8'
        try:
            line = line.decode('utf-8', 'ignore')
        except UnicodeDecodeError:
            pass # keep print bytes
        self.echo(f'    {line}')
