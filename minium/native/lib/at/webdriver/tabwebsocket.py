# encoding=utf-8
import json
import time
import traceback
import logging
import threading
import websocket
from .wspools import WsPools
from .error import *


logger = logging.getLogger()

MAX_WAIT_TIMEOUT = 50 #原先33
OPEN_TIMEOUT     = 4
CLOSE_TIMEOUT    = 4


class TabWebSocket(object):
    "与chrome内核的一个tab标签的Websocket连接"
    _ID_COUNTER = 0

    def __init__(self, url, desc=None, tab_id=None, title=None):
        self._identity = TabWebSocket._ID_COUNTER
        TabWebSocket._ID_COUNTER += 1
        self._url = url
        self._desc = desc
        self._tab_id = tab_id
        self._title = title
        self._open_lock = threading.Condition()
        self._close_lock = threading.Condition()
        self._msg_lock = threading.Condition()
        self._thread = None
        self._init()
        self.ensure_opened()

    def _init(self):
        self._width = -1
        self._height = -1

        self._req_id_counter = 0  # message id
        self._ws_event_queue = dict()
        self._is_running = False  # 标记连接是否建立
        self._status = "close"
        self._sync_wait_msg_id = None
        self._sync_wait_msg = None


    # ==============================================================================================
    # Property
    # ==============================================================================================
    @property
    def identity(self): return self._identity

    @property
    def url(self): return self._url

    @property
    def desc(self): return self._desc

    @property
    def tab_id(self): return self._tab_id

    @property
    def title(self): return self._title

    # ==============================================================================================
    # WebSocket Event Private Handler
    # ==============================================================================================
    def _on_open(self, ws):
        """
        :type ws: websocket.WebSocketApp
        """
        logger.debug('%s, %s, opened', self.url, self._thread.ident)
        self._status = "open"
        self.set_running(True)
        self._open_lock.acquire()
        self._open_lock.notify()
        self._open_lock.release()

    def _on_message(self, ws, message):
        """
        :type ws: websocket.WebSocketApp
        """
        logger.debug("%s, %s: %.1024s", self.url, self._thread.ident, message)
        msg = json.loads(message)
        if msg is not None and "id" in msg:     # response
            req_id = msg["id"]
            if req_id == self._sync_wait_msg_id:
                self._sync_wait_msg_id = None
                self._sync_wait_msg = msg
                self._msg_lock.acquire()
                self._msg_lock.notify()
                self._msg_lock.release()
            else:
                logger.warning('abandon msg: %s', req_id)
        else: # event from X5
            if "method" in msg and "params" in msg:
                self._push_event(msg["method"], msg["params"])

    def _on_error(self, ws, error):
        logger.error("%s, %s, error %s", self.url, self._thread.ident, error)

    def _on_close(self, ws):
        self.set_running(False)
        self._status = "close"
        logger.debug('%s, %s, closed in on_close', self.url, self._thread.ident)

        self._close_lock.acquire()
        self._close_lock.notify()
        self._close_lock.release()

    # ==============================================================================================
    # Open & Close
    # ==============================================================================================
    def _ws_run_forever(self):
        "在其他线程中执行"
        url = self.url
        logger.debug("%s, %s, ready to run", url, self._thread.ident)

        try:
            self._client.run_forever()
            self._init()
        except:
            self.set_running(False) # TODO 重构
            traceback.print_exc()
            logger.exception('websocket run error')
            return

        logger.debug("%s, %s, run forerver shutdown", url, self._thread.ident)

    def ensure_opened(self, timeout=OPEN_TIMEOUT):
        if self._status != "close":
            return
        WsPools.add(self)   # 成对出现
        self._client = websocket.WebSocketApp(self.url, on_open=self._on_open, on_message=self._on_message,
                                              on_error=self._on_error, on_close=self._on_close)
        self._open_lock.acquire()
        self._thread = threading.Thread(target=self._ws_run_forever, args=())
        self._status = "pending"
        self._thread.daemon = True
        self._thread.start()
        self._open_lock.wait(timeout) # 等待on_open唤醒
        self._open_lock.release()

        if self._is_running:
            logger.debug("%s, open in open API", self.url)
        else:
            logger.debug('url: %s', self.url)
            raise OpenWebSocketException('can not open websocket')

    def close(self, timeout=CLOSE_TIMEOUT):
        "关闭当前连接，幂等，允许多次调用"
        if not WsPools.has(self.identity): return
        WsPools.remove(self)    # 成对出现
        self._client.close()
        self._close_lock.acquire()
        self._close_lock.wait(timeout)   # 等待on_close唤醒
        self._close_lock.release()

        if self._is_running: # 有的机器close和on_close就不是成对出现的
            logger.warning('timeout, can not close websocket')
            #   raise CloseWebSocketException('timeout, can not close weboscket')
        else:
            logger.debug("%s, closed in close API", self.url)

    def __del__(self):
        self.close()

    def set_running(self, is_running):
        self._is_running = is_running

    # ==============================================================================================
    # Raw Event Protocol
    # ==============================================================================================
    def _push_event(self, method, params):
        if method in self._ws_event_queue:
            self._ws_event_queue[method].append(params)
        else:
            self._ws_event_queue[method] = [params, ]

    def pop_event(self, method):
        "弹出队列里先来的消息"
        if method in self._ws_event_queue:
            params = self._ws_event_queue[method][0]
            if len(self._ws_event_queue[method]) == 1:
                del self._ws_event_queue[method]
            else:
                del self._ws_event_queue[method][0]
            return params
        raise RuntimeError('no event: %s in queue' % method)

    def peek_event(self, method):
        "获取队列里先来的消息, 但不弹出"
        if self.has_event(method):
            return self._ws_event_queue[method][0]
        raise RuntimeError('no event: %s in queue' % method)

    def has_event(self, method):
        "判断事件消息是否存在"
        return method in self._ws_event_queue and len(self._ws_event_queue[method]) > 0

    def get_event(self, method):
        "获取事件队列"
        if method in self._ws_event_queue:
            return self._ws_event_queue[method]
        else:
            return None

    # TODO 使用锁来重构
    def wait_for_event(self, method, timeout=MAX_WAIT_TIMEOUT):
        "等待事件返回"
        start_time = time.time()
        while not self.has_event(method) and self._is_running:
            if time.time() - start_time > timeout:
                logger.warn("timeout " + method)
                break
            time.sleep(0.1)
        if self.has_event(method):
            return self.peek_event(method)
        return None

    # ==============================================================================================
    # Raw Communicate Protocol
    # ==============================================================================================
    def async_request(self, domain, command, params=None):
        "不阻塞异步执行, 不需要返回数据"
        req = { "method": "%s.%s" % (domain, command), "params": params }
        req_id = self._send_request(req)
        return req_id

    def sync_request(self, domain, command, params=None, timeout=MAX_WAIT_TIMEOUT):
        "阻塞直到获取返回数据, 或者超时报错"
        req = { "method": "%s.%s" % (domain, command), "params": params }
        self._sync_wait_msg_id = self._send_request(req)
        # logger.info(self._sync_wait_msg_id)
        return self._receive_request(timeout)

    def _send_request(self, params):
        if "id" in params:
            req_id = params["id"]
        else:
            params["id"] = req_id = self._get_req_id()
        serialize = json.dumps(params)
        # logger.debug('send: %s', serialize)
        self.ensure_opened()
        self._client.send(serialize)
        return req_id

    def _receive_request(self, timeout=MAX_WAIT_TIMEOUT):
        self._msg_lock.acquire()
        self._msg_lock.wait(timeout)
        self._msg_lock.release()

        if self._sync_wait_msg_id is None: # 获取到了数据
            return self._sync_wait_msg
        else:
            record_id = self._sync_wait_msg_id
            self._sync_wait_msg_id = None
            self._sync_wait_msg = None
            raise ResponseTimeout("receive from remote timeout, id: %s" % record_id)

    def _get_req_id(self):
        self._req_id_counter += 1
        return self._req_id_counter

    # ==============================================================================================
    # Runtime Protocol
    # ==============================================================================================
    def run_script(self, script, timeout=MAX_WAIT_TIMEOUT):
        # 小程序monkey的部分逻辑用到了includeCommandLineAPI
        # 协议版本: 1.1, 很可能不支持awaitPromise
        data = self.sync_request("Runtime", "evaluate", {"expression": script, "includeCommandLineAPI": True}, timeout)

        # TODO 如果webSocket提前中断, data可能是None
        if data is None: raise WebSocketLoseError("can not get script return, maybe webSocket crash happened")
        return data

    def run_script_with_output(self, script, timeout=MAX_WAIT_TIMEOUT):
        data = self.run_script(script, timeout)

        # 观察一下, 因为有前面的守护判断, 这里的data应该总是合法
        result = data["result"]["result"]
        result_type = result["type"]

        if result_type in ["boolean", "string", "number"]:
            return result["value"]
        else:
            logger.debug(u"未处理的类型: %s", result_type)
        return None

    def await_promise(self, promise_object_id, timeout = MAX_WAIT_TIMEOUT):
        "不用使用, 1.1不支持"
        data = self.sync_request('Runtime', 'awaitPromise', {"promiseObjectId": promise_object_id}, timeout)
        return data

    # ==============================================================================================
    # DOM Protocol
    # ==============================================================================================
    def get_document(self):
        data = self.sync_request('DOM', 'getDocument')
        return data['result']['root']

    def query_selector(self, node_id, selector):
        data = self.sync_request('DOM', 'querySelector', { 'nodeId': node_id, 'selector': selector })
        return data['result']

    def request_node(self, object_id):
        data = self.sync_request('DOM', 'requestNode', { 'objectId': object_id })
        return data

    def get_attributes(self, node_id):
        data = self.sync_request('DOM', 'getAttributes', { 'nodeId': node_id })
        return data

    # ==============================================================================================
    # Page Protocol
    # ==============================================================================================
    def get(self, url):
        self.sync_request("Page", "navigate", {"url": url})

    def reload(self, ignore_cache=True):
        self._ws_event_queue = dict()
        self.sync_request("Page", "reload", {"ignoreCache": ignore_cache})

    def page_enable(self):
        self.sync_request("Page", "enable", {})

    def network_enable(self):
        self.sync_request("Network", "enable", {})

    def network_clear_browser_cache(self):
        self.sync_request("Network", "clearBrowserCache", {})

    def network_set_cache_disabled(self):
        self.sync_request("Network", "setCacheDisabled", {"cacheDisabled": True})

    def console_enable(self, is_enable=True):
        if is_enable:
            method = "enable"
        else:
            method = "disable"
        self.sync_request("Console", method)


# self.errors = []
# def error(self, msg):
#     self.errors.append(msg)
