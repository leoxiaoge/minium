#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by xiazeng on 2018/3/14
import threading
import logging
import time


logger = logging.getLogger()


class ThreadHelper(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(ThreadHelper, self).__init__(*args, **kwargs)
        self.thread_main = None
        self.args = None
        self.kwargs = None
        self.thread_result = None
        self.run_exception = None

    @property
    def result(self):
        self.join()
        if self.run_exception is not None:
            raise self.run_exception
        return self.thread_result

    def run(self):
        try:
            s = time.time()
            self.thread_result = self.thread_main(*self.args, **self.kwargs)
            logger.info("costs %.2fms", time.time()-s)
        except Exception as e:
            logger.exception("failed")
            self.run_exception = e


def run(f, *args, **kwargs):
    thread_helper = ThreadHelper()
    thread_helper.args = args
    thread_helper.kwargs = kwargs
    thread_helper.thread_main = f
    thread_helper.setDaemon(True)
    thread_helper.start()
    return thread_helper


def post_run(delay, f, *args, **kwargs):
    time.sleep(delay)
    run(f, *args, **kwargs)


def test(a):
    import time
    time.sleep(1)
    return a

if __name__ == '__main__':
    a = run(test, 1)
    b = run(test, 'ad')

    print(b.result)
    print(a.result)
