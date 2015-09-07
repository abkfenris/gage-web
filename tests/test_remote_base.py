import pytest

from .test_basics import BasicTestCase

from app.remote import base


class TestRemoteBase(BasicTestCase):
    remote_gage = base.RemoteGage()

    def test_get_sample(self):
        with pytest.raises(NotImplementedError):
            self.remote_gage.get_sample(1)
