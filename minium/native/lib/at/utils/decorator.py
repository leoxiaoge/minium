# -*- coding: utf-8 -*-
import threading
import sys

import time
import logging

__author__ = 'xiazeng'
logger = logging.getLogger()


class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill()
    method.
    Come from:
    Kill a thread in Python:
    http://mail.python.org/pipermail/python-list/2004-May/260937.html
    """
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run  # Force the Thread to install our trace.
        threading.Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the
        trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


class Timeout(Exception):
    """function run timeout"""
    pass


def timeout(seconds):
    """超时装饰器，指定超时时间
    若被装饰的方法在指定的时间内未返回，则抛出Timeout异常"""

    def timeout_decorator(func):
        """真正的装饰器"""

        def _new_func(old_func, result, old_func_args, old_func_kwargs):
            result.append(old_func(*old_func_args, **old_func_kwargs))

        def _(*args, **kwargs):
            result = []
            new_kwargs = {  # create new args for _new_func, because we want to get the func return val to result list
                'old_func': func,
                'result': result,
                'old_func_args': args,
                'old_func_kwargs': kwargs
            }
            thd = KThread(target=_new_func, args=(), kwargs=new_kwargs)
            thd.start()
            thd.join(seconds)
            alive = thd.isAlive()
            thd.kill()  # kill the child thread
            if alive:
                raise Timeout(u'function run too long, timeout %d seconds.' % seconds)
            else:
                return result[0] if len(result) > 0 else None

        _.__name__ = func.__name__
        _.__doc__ = func.__doc__
        return _
    return timeout_decorator


def retry_in(max_seconds, sleep_seconds=1):
    """
    重试装饰器，在指定的时间内不断重试
    被装饰的方法如果返回非真，那么认为需要重试。如果超时都未返回真，那么以最后一次测试的结果返回
    注意： 如果函数内部发生异常，将捕捉不到堆栈
    """

    def timeout_decorator(func):
        """真正的装饰器"""

        def _new_func(old_func, result, old_func_args, old_func_kwargs, ex):
            try:
                ret = old_func(*old_func_args, **old_func_kwargs)
                result.append(ret)
            except Exception as e:
                ex.append(e)

        def _(*args, **kwargs):
            ex = []
            result = []
            new_kwargs = {  # create new args for _new_func, because we want to get the func return val to result list
                'old_func': func,
                'result': result,
                'old_func_args': args,
                'old_func_kwargs': kwargs,
                'ex': ex
            }
            index = 0
            last_time = time.time() + max_seconds
            while time.time() < last_time:
                thd = KThread(target=_new_func, args=(), kwargs=new_kwargs)
                thd.start()
                thd.join(max_seconds)
                thd.kill()  # kill the child thread
                if len(ex) == 1:
                    raise ex[0]
                if index < len(result) and result[index]:
                    break
                index += 1
                time.sleep(sleep_seconds)
            else:
                return result[-1] if result else None
            return result[index]

        _.__name__ = func.__name__
        _.__doc__ = func.__doc__
        return _
    return timeout_decorator


def retry_exception(ExceptionToCheck=Exception, tries=3, delay=1, backoff=2):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = u"%s, Retrying in %d seconds..." % (e, mdelay)
                    logger.exception(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

method_costs = {}


def cost_log(func):
    def wrap(*arg, **kargs):
        start = time.time()
        r = func(*arg, **kargs)
        end = time.time()
        if func not in method_costs:
            method_costs[func] = {"total": 0, "num": 0}
        method_costs[func]["total"] += (end - start)*1000
        method_costs[func]["num"] += 1
        logger.info(" %s  cost %d ms" % (func.__name__, (end - start)*1000))
        return r
    return wrap


class cached_property(object):
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property.

        Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
        """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def get_key(i):
    if isinstance(i, str):
        return hash(i)
    if isinstance(i, int):
        return i
    if isinstance(i, object):
        return hash(i)
    raise RuntimeError("notice xia zeng")


def get_id_tuple(f, args, kwargs, mark=object()):
    l = [id(f)]
    for arg in args:
        l.append(get_key(arg))
    l.append(get_key(mark))
    for k, v in kwargs:
        l.append(k)
        l.append(get_key(v))
    return tuple(l)

_func_memoized = {}
def memoize(f):
    """
    缓存函数调用
    """
    def memoized(*args, **kwargs):
        key = get_id_tuple(f, args, kwargs)
        if key not in _func_memoized:
            _func_memoized[key] = f(*args, **kwargs)
        return _func_memoized[key]
    return memoized


class testCachedProperty(object):

    @cached_property
    def very_slow(self):
        """Represents a performance heavy property."""
        time.sleep(1)  # Wait a WHOLE second!
        return "I am slooooow"


@timeout(5)
def test_timeout(seconds, text):
    print('start', seconds, text)
    time.sleep(seconds)
    print('finish', seconds, text)
    return seconds


@retry_in(5, 1)
def test_retry_in(seconds, text):
    print('start', seconds, text)
    if seconds > 5:
        return True


def test():
    a = testCachedProperty()
    for sec in range(1, 10):

        try:
            print('*' * 20)
            # print test_timeout(sec, 'test waiting %d seconds' % sec)
            # print test_retry_in(sec, 'test waiting %d seconds' % sec)

            print(a.very_slow)
        except Timeout as e:
            print(e)


if __name__ == '__main__':
    test()
