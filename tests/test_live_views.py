import sys
import pytest
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

    @pytest.mark.skipif(sys.version_info > (3,0),
                        reason='python 3 issues')
    def test_gage_plot(self):
        """
        Test that a gage plot can be generated
        """
        r = requests.get('{server}/gage/1/usgs-height.png'.format(
                server=self.get_server_url()))
        assert 'image/png' == r.headers['content-type']
