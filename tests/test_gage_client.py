from test_basics import BasicTestCase
from .gage_client.gage_client import Client
from flask import current_app
import requests

class GageClient_0_1_Case(BasicTestCase):

    def test_gage_client(self):
        self.gc = Client('http://127.0.0.1/api/0.1/gages/1/sample', 1, 'password')
        # r = requests.get('http://127.0.0.1:5000/')
