import sys
import requests

from .test_live import LiveServerBase


class GageClient01(LiveServerBase):
    def test_index_page(self):
        """
        Test that the index page loads
        """
        r = requests.get(self.get_server_url())
        assert 'riverflo.ws' in r.text

    def test_gage_page(self):
        """
        Test that a gage page will load
        """
        r = requests.get('{server}/gage/1/'.format(
                server=self.get_server_url()))
        assert 'Wild River at Gilead' in r.text
        r = requests.get('{server}/gage/wild-river-gilead/'.format(
                server=self.get_server_url()))
        assert 'Wild River at Gilead' in r.text

