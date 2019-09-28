# encoding=utf-8


class WsPools(object):
    """
    Websocket连接池，保存所有的websocket连接
    - 单例模式
    - tab的id和url都是有可能重复出现的, 最好不要用成主键来索引, 否则可能导致多个线程的竞态条件产生
    """
    _socket_map = {}

    @classmethod
    def add(cls, sock):
        "按主键存储"
        cls._socket_map[sock.identity] = sock

    @classmethod
    def remove(cls, sock):
        "按主键移除"
        del cls._socket_map[sock.identity]

    @classmethod
    def get(cls, identity):
        "根据主键返回"
        return cls._socket_map[identity]

    @classmethod
    def has(cls, identity):
        "判断是否存在"
        return identity in WsPools._socket_map

    # =======================================================================================
    # Business ID
    # =======================================================================================

    @classmethod
    def has_id(cls, tab_id):
        "判断指定业务ID页面是否存在"
        for sock in WsPools._socket_map.values():
            if sock.tab_id == tab_id:
                return True
        return False

    @classmethod
    def get_by_id(cls, tab_id):
        "根据其业务ID返回"
        for sock in WsPools._socket_map.values():
            if sock.tab_id == tab_id:
                return sock
