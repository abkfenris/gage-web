import sys
from flask import request
from .test_basics import BasicTestCase

from app.main import plot



class TestPlot(BasicTestCase):

    def test_plot_init(self):
        """
        Test that a SensorPlot object can be initialized
        """
        self.plot = plot.SensorPlot(gid=1, stype='usgs-height')
        assert self.plot.gid == 1
        assert self.plot.stype == 'usgs-height'
        from app.models import Sensor
        assert type(self.plot.sensor) == Sensor

    def test_plot_data(self):
        """
        Test that SensorPlot.data() will return some data
        """
        rv = self.client.get('/gage/1/usgs-height.png')
        assert rv.status_code == 200
        assert rv.content_type == 'image/png'
        with self.app.test_request_context('/gage/1/usgs-height.png'):
            assert request.path == '/gage/1/usgs-height.png'
            self.plot = plot.SensorPlot(gid=1, stype='usgs-height')
            self.plot.data()

    def test_plot_data_args(self):
        """
        Test that SensorPlot.data() will return a different response with
        start and end arguments
        """
        with self.app.test_request_context('/gage/1/usgs-height.png'):
            self.plot = plot.SensorPlot(gid=1, stype='usgs-height')
            self.normaldata = self.plot.data()
        with self.app.test_request_context('/gage/1/usgs-height.png?start=20150712&end=20150720'):
            assert request.args.get('start') == '20150712'
            assert request.args.get('end') == '20150720'
            self.plot = plot.SensorPlot(gid=1, stype='usgs-height')
            self.argsdata = self.plot.data()
            assert str(self.argsdata) != str(self.normaldata)

    def test_plot_matplot(self):
        """
        Test that SensorPlot.matplot() will return a figure
        """
        with self.app.test_request_context('/gage/1/usgs-height.png'):
            self.plot = plot.SensorPlot(gid=1, stype='usgs-height')
            matplot = self.plot.matplot()
            from matplotlib.figure import Figure
            assert type(matplot) == Figure

    def test_plot_png(self):
        """
        Test that SensorPlot.png() will return a PNG
        """
        with self.app.test_request_context('/gage/1/usgs-height.png'):
            self.plot = plot.SensorPlot(gid=1, stype='usgs-height')
            self.png = self.plot.png()
            if sys.version_info < (3,0):
                assert 'PNG' in self.png
            else:
                assert 'PNG' in str(self.png)

    def test_plot_jpg(self):
        """
        Test that SensorPlot.png() will return a JPEG
        """
        with self.app.test_request_context('/gage/1/usgs-height.jpg'):
            self.plot = plot.SensorPlot(gid=1, stype='usgs-height')
            self.jpg = self.plot.jpg()
            assert 'JFIF' in str(self.jpg)
