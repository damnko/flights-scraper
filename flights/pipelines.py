# -*- coding: utf-8 -*-

class FlightDataValidation(object):
    def process_item(self, item, spider):
        # TODO: validate each field
        # example validation
        if type(item['price']) not in (float, int) or item['price'] <= 0:
            spider.logger.info('Problem with flight price, either not number or <= 0')
        return item
