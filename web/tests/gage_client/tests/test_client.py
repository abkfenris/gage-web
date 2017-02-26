import unittest
import json
import requests
from datetime import datetime as dt

from gage_client import Client

password = 'password'
url_stub = 'http://riverflo.ws/api/'
gage_id = 5

class ClientTestCase(unittest.TestCase):

    def setUp(self):
        self.client = Client(url_stub + 'gages/' + str(gage_id) + '/sample', gage_id, password)

    def testVersion(self):
        print(self.client)
        print(type(self.client))
        self.assertNotEqual(type(self.client), Client)

    # def testReading(self):

if __name__ == '__main__':
    unittest.main()
