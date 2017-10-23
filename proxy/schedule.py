import asyncio
import aiohttp
import time

from .getter import ProxyGetter
from .setting import *
from .db import RedisClient
from .error import ResourceDepletionError
from multiprocessing import Process

# 测试proxy 的异常
from asyncio import TimeoutError
from aiohttp import ClientError

class ValidityTester(object):

    test_url = TEST_URL

    def __init__(self):
        self._raw_proxies =None

    # 将proxy传入实例
    def set_raw_proxies(self, proxies):
        self._raw_proxies = proxies
        self._conn = RedisClient()

    # 异步测试, asyncio 异步函数， aiohttp 异步请求,网络io直接切出去
    async def proxy_test(self, proxy):
        async with aiohttp.ClientSession() as session:
            try:
                # 将bytes转str
                if isinstance(proxy, bytes):
                    proxy = proxy.decode("utf-8")
                real_proxy = "http://" + proxy
                print("Testing", proxy)
                # 测试,
                async with session.get(self.test_url, proxy=real_proxy, timeout = 20) as response:
                    print(response.status)
                    if response.status == 200:
                        self._conn.put(proxy)
                        print("Valid proxy", proxy)
            except (ClientError, TimeoutError, ValueError):
                print("Invalid proxy", proxy)

    # 测试所有proxy
    def test(self):
        print('ValidityTester is working')
        try:
            # 得到event loop
            loop  = asyncio.get_event_loop()
            # 封装task
            tasks = [self.proxy_test(proxy) for proxy in self._raw_proxies]
            # 执行coroutine
            loop.run_until_complete(asyncio.wait(tasks)) # asyncio.wait -> task 队列
        except ValueError:
            print('Async Error')

class PoolAdder(object):

    def __init__(self, threshold):
        self._crawler = ProxyGetter()
        self._conn = RedisClient()
        self._tester = ValidityTester()
        self._threshold = threshold

    # 保证线程池线程池
    def is_over_threshold(self):
        if self._conn.queue_len >= self._threshold:
            return True
        else:
            return False

    def add_to_queue(self):
        print("PoolAdder is working")
        proxy_count = 0
        for callback_label in range(self._crawler.__CrawlFuncCount__):
            callback = self._crawler.__CrawlFunc__[callback_label]
            raw_proxies = self._crawler.get_proxies(callback)
            # 测试
            self._tester.set_raw_proxies(raw_proxies)
            self._tester.test()
            # ip池数量
            proxy_count += len(raw_proxies)
            if self.is_over_threshold():
                print("IP is enough")
                break
        if proxy_count == 0:
            raise ResourceDepletionError

class Schedule(object):

    # 检查 => 得到redis左边的proxy，更新到右边
    @staticmethod
    def valid_proxy(cycle=VALID_CHECK_CYCLE):
        conn = RedisClient()
        tester = ValidityTester()
        while True:
            count = int(0.5*conn.queue_len)
            # 如果redis 中没有ip，睡眠，等待check_pool
            if count == 0:
                print("waiting for adding")
                time.sleep(cycle)
                continue
            # 检查
            raw_proxies = conn.get(count)
            tester.set_raw_proxies(raw_proxies)
            tester.test()
            time.sleep(cycle)

    # 添加 => 向redis 中添加ip
    @staticmethod
    def check_pool(lower_threshold=POOL_LOWER_THRESHOLD,
                   upper_threshold=POOL_UPPER_THRESHOLD,
                   cycle=POOL_CHECK_CYCLE):
        conn = RedisClient()
        adder = PoolAdder(upper_threshold)
        while True:
            if conn.queue_len < lower_threshold:
                adder.add_to_queue()
            time.sleep(cycle)

    def run(self):
        print("schedule staring")
        valid_process = Process(target=Schedule.valid_proxy)
        check_process = Process(target=Schedule.check_pool)
        valid_process.start()
        check_process.start()



