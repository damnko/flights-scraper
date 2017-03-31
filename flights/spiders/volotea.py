# -*- coding: utf-8 -*-

import datetime
import json
import scrapy
from scrapy.conf import settings

from flights.helpers import dates
from flights.items import FlightData

class VoloteaSpider(scrapy.Spider):
    name = "volotea"
    allowed_domains = ["volotea.com"]

    def start_requests(self):
        self.orig = {
            'venice': 'VCE'
        }
        self.dest = {
            'alicante': 'ALC',
            'asturie': 'OVD',
            'atene': 'ATH',
            'cefalonia': 'EFL',
            'corfu': 'CFU',
            'praga': 'PRG'
        }

        # volotea returns a json with all the scheduled flights for a specific route
        # so no need to ask for specific dates

        # create the outbound flight urls
        for origin in self.orig.values():
            for destination in self.dest.values():
                route = sorted((origin, destination))
                request = self.generate_link(route[0], route[1])
                yield request

    def parse(self, response):
        origin = response.meta['origin']
        destination = response.meta['destination']

        # response is a json object
        jsonresponse = json.loads(response.body_as_unicode())

        flights = []

        for route in jsonresponse.keys():
            arrival_departure = self.get_origin_destination(route)
            for flight in jsonresponse[route]:
                fd = FlightData()
                fd['capture_time'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                fd['origin'] = arrival_departure['origin']
                fd['destination'] = arrival_departure['destination']
                fd['departure_time'] = self.change_time_format(flight['Departure'])
                fd['arrival_time'] = self.change_time_format(flight['Arrival'])
                fd['flight_code'] = flight['FlightNumber']
                # get the regular price without fees (payment by debit card)
                price = filter(lambda price: price['FareType'] == 'R', flight['Prices'])
                fd['price'] = next(price)['Price']
                flights.append(fd)

        return flights

    def get_origin_destination(self, route_string):
        route_list = route_string.split('-')
        return {
            'origin': route_list[0],
            'destination': route_list[1]
        }

    def generate_link(self, origin, destination):
        link = 'https://json.volotea.com/dist/schedule/{origin}-{destination}_schedule.json'.format(origin=origin, destination=destination)
        request = scrapy.Request(link, self.parse)
        request.meta['origin'] = origin
        request.meta['destination'] = destination
        return request

    def change_time_format(self, time):
        return datetime.datetime.strptime(time, '%Y%m%d%H%M').strftime('%Y/%m/%d %H:%M:%S')
