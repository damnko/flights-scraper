# -*- coding: utf-8 -*-

from scrapy import Item, Field

class FlightData(Item):
    capture_time = Field()
    departure_time = Field()
    departure_time_utc = Field()
    arrival_time = Field()
    duration = Field()
    return_time = Field()
    origin = Field()
    destination = Field()
    price = Field()
    fares_left = Field()
    flight_code = Field()
