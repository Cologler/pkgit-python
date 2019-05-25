# -*- coding: utf-8 -*-
#
# Copyright (c) 2019~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from threading import Thread, Lock, Condition
from subprocess import Popen
from queue import Queue

def _read_from_stream(stream, queue: Queue, tag):
    def run():
        for line in stream:
            line: bytes
            for x in line.splitlines():
                queue.put((tag, x))
        queue.put(None)

    thread = Thread(target=run)
    thread.start()

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

    queue = Queue()
    err_reader = _read_from_stream(proc.stderr, queue, 'stderr')
    out_reader = _read_from_stream(proc.stdout, queue, 'stdout')

    end_count = 0
    while end_count < 2:
        item = queue.get()
        if item is None:
            end_count += 1
        else:
            yield item
