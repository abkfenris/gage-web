import pytest

from .test_basics import BasicTestCase

from app.remote import base


class TestRemoteBase(BasicTestCase):
    RemoteGage = base.RemoteGage()

    def test_get_sample(self):
        with pytest.raises(NotImplementedError):
            self.RemoteGage.get_sample(1)
