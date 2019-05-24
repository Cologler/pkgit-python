# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from threading import Thread, Lock, Condition
from subprocess import Popen


class StreamReader:
    def __init__(self, stream, cond: Condition):
        self._stream = stream
        self._thread: Thread = None
        self._buffer = []
        self._end = False
        self._lock = Lock()
        self._cond = cond

    def begin_read(self):
        self._thread = Thread(target=self._run)
        self._thread.start()

    def _run(self):
        for line in self._stream:
            line: bytes
            lines = line.splitlines()
            with self._lock:
                self._buffer.extend(lines)
            with self._cond:
                self._cond.notify(1)

        with self._lock:
            self._end = True
        with self._cond:
            self._cond.notify(1)

    def end(self):
        ''' check whether stream is end '''
        with self._lock:
            return self._end and not self._buffer

    def get_buffer(self) -> list:
        with self._lock:
            try:
                return self._buffer
            finally:
                self._buffer = []


def yield_from_proc(proc: Popen):
    '''
    yield each `bytes` line from `stdout` and `stderr`.

    ``` py
    for src, line in yield_from_proc(proc):
        if src == 'stdout':
            ... # line is read from stdout
        if src == 'stderr':
            ... # line is read from stderr
    ```
    '''

    assert proc.stdout is not None
    assert proc.stderr is not None

    cond = Condition()
    err_reader = StreamReader(proc.stderr, cond)
    out_reader = StreamReader(proc.stdout, cond)
    out_reader.begin_read()
    err_reader.begin_read()
    while True:
        with cond:
            cond.wait(100)
        if err_reader.end() and out_reader.end():
            break
        if not out_reader.end():
            yield from [('stdout', l) for l in out_reader.get_buffer()]
        if not err_reader.end():
            yield from [('stderr', l) for l in err_reader.get_buffer()]
