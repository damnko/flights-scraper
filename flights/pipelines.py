# -*- coding: utf-8 -*-

import pyrebase
from flights.config import pvt_credentials as credentials

class FlightDataValidation(object):
    def process_item(self, item, spider):
        # TODO: validate each field
        # example validation
        if type(item['price']) not in (float, int) or item['price'] <= 0:
            spider.logger.info('Problem with flight price, either not number or <= 0')
        return item

class SaveToFirebase(object):
    def __init__(self):
        self.config = credentials.firebase
    
    def open_spider(self, spider):
        firebase = pyrebase.initialize_app(self.config)
        self.db = firebase.database()

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        print('########################################################')
        print('########################################################')
        print('about to push to firebase', item)
        print('########################################################')
        print('########################################################')
        self.db.child('flights').push(dict(item))
        return item