# -*- coding: utf-8 -*-
import scrapy
from scrapy.conf import settings
import random
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

from flights.helpers import dates

class MomondoSpider(scrapy.Spider):
    name = "momondo"
    allowed_domains = ["momondo.it"]

    def __init__(self, *args, **kwargs):
        super(MomondoSpider, self).__init__(*args, **kwargs)
        self.orig = {
            'venice': 'VCE'
        }
        self.dest = {
            'paris': 'PAR',
            'edinburgh': 'EDI',
            'oslo': 'OSL',
            'st petersburg': 'LED',
            'moscow': 'MOW',
            'london': 'LON',
            'helsinki': 'HEL',
            'reykjavik': 'REK'
        }
        # find upcoming Friday(going) and Sunday(coming back)
        next_friday = dates.find_next_friday()
        next_sunday = next_friday + datetime.timedelta(days=2)
        # create the date array where to search for flights
        self.dates = dates.create_dates(3, next_friday, next_sunday, '%d-%m-%Y')
        # set the user-agent for the current search session
        opts = Options()
        opts.add_argument(random.choice(settings['USER_AGENTS']))
        # set Chrome as driver
        self.driver = webdriver.Chrome(chrome_options=opts)
        self.logger.info('User-agent is now: %s', self.driver.execute_script("return navigator.userAgent"))

    def start_requests(self):
        for origin in self.orig.values():
            for destination in self.dest.values():
                for date_range in self.dates:
                    link = (
                        'http://www.momondo.it/flightsearch/?Search=true&TripType=2&SegNo=2',
                        '&SO0={}'.format(origin),
                        '&SD0={}'.format(destination),
                        '&SDP0={}'.format(date_range[0]),
                        '&SO1={}'.format(destination),
                        '&SD1={}'.format(origin),
                        '&SDP1={}'.format(date_range[1]),
                        '&AD=1&TK=ECO&DO=false&NA=false'
                    )
                    request = scrapy.Request(''.join(link), self.parse)
                    request.meta['dept'] = origin
                    request.meta['arr'] = destination
                    request.meta['dep_date'] = date_range[0]
                    request.meta['arr_date'] = date_range[1]
                    yield request

    def parse(self, response):
        dept = response.meta['dept']
        arr = response.meta['arr']
        dep_date = response.meta['dep_date']
        arr_date = response.meta['arr_date']

        self.driver.get(''.join(response.request.url))
        search_completed = "//div[@id='searchProgressText' and text()='Ricerca completata']"
        # wait for 30secs max for the search to complete
        try:
            element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, search_completed)))
        except Exception as e:
            self.logger.info('The search was not fully completed, gettint the results anyway. Error: %s', str(e))
        sel = scrapy.Selector(text=self.driver.page_source)
        # get the prices
        prices = sel.xpath('//span[@class="price "]/span[@class="value"]/text()').extract()
        prices = [int(price) for price in prices]
        prices.sort()
        # keep only the lowest price
        lowest_price = prices[0]
        yield {
            'dept': dept,
            'arr': arr,
            'dep_date': dep_date,
            'arr_date': arr_date,
            'lowest_price': lowest_price
        }