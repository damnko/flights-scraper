# -*- coding: utf-8 -*-

import base64
import random
from scrapy import signals
from flights.config.agents import AGENTS
from flights.config.proxies import PROXIES_FREE
# check if private proxies are available
try:
    from flights.config.pvt_proxies import PROXIES_PRIVATE, CREDENTIALS
    has_private_proxies = True
except ImportError:
    has_private_proxies = False

class RandomUserAgent(object):
    def process_request(self, request, spider):
        agent = random.choice(AGENTS)
        request.headers['User-Agent'] = agent

class RandomProxy(object):
    def process_request(self, request, spider):
        # if private proxies are not available use the free ones
        proxy_list = PROXIES_PRIVATE if has_private_proxies else PROXIES_FREE
        proxy = random.choice(proxy_list)
        request.meta['proxy'] = 'http://%s' % proxy
        # set proxy authentication if private proxies are available
        if has_private_proxies:
            user_pass = CREDENTIALS['user'] + ':' + CREDENTIALS['pwd']
            user_pass=base64.b64encode(user_pass.encode())
            request.headers['Proxy-Authorization'] = 'Basic ' + user_pass.decode()

class FlightsSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
