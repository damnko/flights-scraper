# -*- coding: utf-8 -*-

import datetime
import json
import scrapy
from scrapy.conf import settings

from flights.helpers import dates
from flights.items import FlightData

class RyanairSpider(scrapy.Spider):
    name = "ryanair"
    allowed_domains = ["ryanair.com"]

    def start_requests(self):
        self.orig = {
            'treviso': 'TSF',
            'venice': 'VCE'
        }
        self.dest = {
            'paris': 'BVA',
            'edinburgh': 'EDI',
            'stockholm': 'NYO',
            'london': 'STN',
            'barcelona': 'BCN'
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
                        'https://desktopapps.ryanair.com/v2/it-it/availability?ADT=1&CHD=0&FlexDaysIn=0&FlexDaysOut=0&INF=0&RoundTrip=true&TEEN=0&exists=false',
                        '&DateIn={}'.format(date_range[1]),
                        '&DateOut={}'.format(date_range[0]),
                        '&Destination={}'.format(destination),
                        '&Origin={}'.format(origin)
                    )
                    request = scrapy.Request(''.join(link), self.parse)
                    yield request

    def parse(self, response):
        # response is a json object
        jsonresponse = json.loads(response.body_as_unicode())
        self.logger.info(jsonresponse)
        trips = jsonresponse['trips']

        flights = []

        for trip in trips:
            for date_details in trip['dates']:
                for flight_details in date_details['flights']:
                    # initialize scrapy item
                    fd = FlightData()
                    fd['capture_time'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                    fd['origin'] = trip['origin']
                    fd['destination'] = trip['destination']
                    fd['flight_code'] = flight_details['flightNumber']
                    fd['departure_time'] = flight_details['time'][0]
                    fd['departure_time_utc'] = flight_details['timeUTC'][0]
                    fd['fares_left'] = flight_details["faresLeft"]
                    # TODO: there could be more fares to get prices from
                    fd['price'] = flight_details['regularFare']['fares'][0]['amount']
                    flights.append(fd)
        return flights