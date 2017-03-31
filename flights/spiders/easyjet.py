# -*- coding: utf-8 -*-

import re
import datetime
import scrapy
from scrapy.conf import settings

from flights.helpers import dates
from flights.items import FlightData

class RyanairSpider(scrapy.Spider):
    name = "easyjet"
    allowed_domains = ["easyjet.com"]

    def start_requests(self):
        self.orig = {
            'venice': 'VCE'
        }
        self.dest = {
            'paris': 'CDG',
            # 'paris1': 'ORY',
            # 'copenhagen': 'CPH'
            # 'edinburgh': 'EDI',
            # 'stockholm': 'NYO',
            # 'london': 'STN',
            # 'barcelona': 'BCN'
        }
        # find upcoming Friday(going) and Sunday(coming back)
        next_friday = dates.find_next_friday()
        next_sunday = next_friday + datetime.timedelta(days=2)
        # create the date array where to search for flights
        self.dates = dates.create_dates(1, next_friday, next_sunday, '%Y-%m-%d')
        # get the urls
        for origin in self.orig.values():
            for destination in self.dest.values():
                for date_range in self.dates:
                    link = (
                        'http://www.easyjet.com/links.mvc?lang=IT&apax=1&cpax=0&ipax=0&SearchFrom=SearchPod2_/it&isOneWay=off&pid=www.easyjet.com',
                        '&dd={}'.format(date_range[0]),
                        '&rd={}'.format(date_range[1]),
                        '&dep={}'.format(origin),
                        '&dest={}'.format(destination)
                    )
                    request = scrapy.Request(''.join(link), self.parse)
                    request.meta['origin'] = origin
                    request.meta['destination'] = destination
                    yield request

    def parse(self, response):
        origin = response.meta['origin']
        destination = response.meta['destination']

        flights = []

        # ids of the divs where the flight data is stored
        outbound_flight_id = 'OutboundFlightDetails'
        inbound_flight_id = 'ReturnFlightDetails'
        for id in (outbound_flight_id, inbound_flight_id):
            container = response.xpath('//div[@id="{}"]'.format(id)).css('.day')[2].css('ul.middleRow li.selectable')
            # for each container there may be more than one flight/dates/prices, so these are lists
            dept_time_raw = container.css('input.flightDate').xpath('@value').extract()
            arr_time_raw = container.css('input.flightArrivalDate').xpath('@value').extract()
            price_raw = container.xpath('a/@charge-credit-full').extract()
            # converting values to correct formats
            dept_time = [self.convert_flight_time(time_raw) for time_raw in dept_time_raw]
            arr_time = [self.convert_flight_time(time_raw) for time_raw in arr_time_raw]
            price = [float(price) for price in price_raw]
            # save flight data
            group = zip(dept_time, arr_time, price)
            for el in group:
                fd = FlightData()
                fd['capture_time'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                fd['origin'] = origin if id == outbound_flight_id else destination
                fd['destination'] = destination if id == outbound_flight_id else origin
                fd['departure_time'] = el[0]
                fd['arrival_time'] = el[1]
                fd['price'] = el[2]
                flights.append(fd)

        return flights

    def convert_flight_time(self, raw_time):
        print('############################', raw_time)
        raw_time = re.sub(r'new Date\((\d+)\)', r'\1', raw_time)
        return datetime.datetime.fromtimestamp(int(raw_time)/1000).strftime('%Y/%m/%d %H:%M:%S')