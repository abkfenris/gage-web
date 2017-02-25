import unittest
import json
import responses
import requests
from itsdangerous import JSONWebSignatureSerializer, BadSignature
from datetime import datetime as dt

from gage_client import Client
from gage_client.client import Client_0_1, AuthenticationError, SendError

password = 'password'
url_stub = 'http://riverflo.ws/api/0.1/'
gage_id = 5
s = JSONWebSignatureSerializer(password)
url = url_stub + 'gages/' + str(gage_id) + '/sample'
bad_url = 'http://riverflo.ws'
bad_password = 'badpassword'


def client_0_1_response_callback(request):
    try:
        payload = s.loads(request.body)
    except BadSignature:
        print('Bad Signature')
        output = {'error': 'unauthorized',
                  'message': 'bad signature'}
        return (401, {}, json.dumps(output))
    samples = payload['samples']
    output_samples = []
    count = 0
    for sample in samples:
        result_json = {
            'datetime': sample['datetime'],
            'id ': count,
            'sender_id': sample['sender_id'],
            'url': 'http://example.com/api/0.1/samples/(count)'.format(count=count),
            'value': sample['value']
        }
        output_samples.append(result_json)

    resp_body = {'gage': {'id': payload['gage']['id']},
                 'result': 'created',
                 'samples': output_samples}
    return (200, {}, json.dumps(resp_body))


def client_0_1_partial_callback(request):
    try:
        payload = s.loads(request.body)
    except BadSignature:
        print('Bad Signature')
        output = {'error': 'unauthorized',
                  'message': 'bad signature'}
        return (401, {}, json.dumps(output))
    samples = payload['samples'][::2]
    output_samples = []
    count = 0
    for sample in samples:
        result_json = {
            'datetime': sample['datetime'],
            'id ': count,
            'sender_id': sample['sender_id'],
            'url': 'http://example.com/api/0.1/samples/(count)'.format(count=count),
            'value': sample['value']
        }
        output_samples.append(result_json)

    resp_body = {'gage': {'id': payload['gage']['id']},
                 'result': 'created',
                 'samples': output_samples}
    return (200, {}, json.dumps(resp_body))


class Test_Client_0_1(unittest.TestCase):
    """
    Basic tests of Client_0_1
    """

    def setUp(self):
        responses.reset()
        self.client = Client(url, gage_id, password)

    def testVersion(self):
        self.assertEqual(type(self.client), Client_0_1)

    def testReading(self):
        datetime = str(dt.now())
        sensor = 'level'
        value = 4.2
        self.client.reading(sensor, datetime, value)
        self.assertEquals(len(self.client.samples), 1)
        print(self.client.samples[0])
        self.assertEquals(self.client.samples[0]['type'], sensor)
        self.assertEquals(self.client.samples[0]['value'], value)
        self.assertEquals(self.client.samples[0]['datetime'], datetime)
        self.assertEquals(len(self.client.readings()), 1)

    @responses.activate
    def testSend_All(self):
        responses.add_callback(
            responses.POST, url,
            callback=client_0_1_response_callback,
            content_type='application/json'
        )
        self.client.reading('level', str(dt.now()), 4.2)
        self.client.reading('ampherage', str(dt.now()), 375.3)
        self.client.send_all()


class Test_Client_0_1_Partial(Test_Client_0_1):
    """
    Test when a server can only process a few of the responses sent
    """
    @responses.activate
    def testSend_All(self):
        responses.add_callback(
            responses.POST, url,
            callback=client_0_1_partial_callback,
            content_type='application/json'
        )
        self.client.reading('level', str(dt.now()), 4.2)
        self.client.reading('ampherage', str(dt.now()), 375.3)
        self.assertRaises(SendError, self.client.send_all)


class Test_Client_0_1_Ids(Test_Client_0_1):
    """
    Checks that the client can make readings with non sequential id numbers
    """

    def testReading(self):
        datetime = str(dt.now())
        sensor = 'level'
        value = 4.2
        self.client.reading(sensor, datetime, value, id=1)
        self.assertEquals(len(self.client.samples), 1)
        print(self.client.samples[0])
        self.assertEquals(self.client.samples[0]['type'], sensor)
        self.assertEquals(self.client.samples[0]['value'], value)
        self.assertEquals(self.client.samples[0]['datetime'], datetime)


class Test_Client_0_1_BadPassword(Test_Client_0_1):
    """
    Checks that the server sends a 401 response and that the client raises an
    Authentication error
    """

    def setUp(self):
        responses.reset()
        self.client = Client(url, gage_id, bad_password)

    @responses.activate
    def testSend_All(self):
        responses.add_callback(
            responses.POST, url,
            callback=client_0_1_response_callback,
            content_type='application/json'
        )
        self.client.reading('level', str(dt.now()), 4.2)
        self.client.reading('ampherage', str(dt.now()), 375.3)
        self.assertRaises(AuthenticationError, self.client.send_all)

class Test_Client_0_1_BadEndpoint(Test_Client_0_1):
    """
    Test when the client is given a bad endpoint
    """
    def setUp(self):
        responses.reset()
        self.client = Client(bad_url, gage_id, password)

    def testVersion(self):
        self.assertNotEqual(self.client, Client_0_1)

    testReading = None
    testSend_All = None


class Test_Client_0_1_MalformedResponse(Test_Client_0_1):
    """
    Test when the server returns something completely random and useless
    """
    @responses.activate
    def testSend_All(self):
        responses.add(
            responses.POST, url,
            body='Error message', status=404,
            content_type='application/json'
        )
        self.client.reading('level', str(dt.now()), 4.2)
        self.client.reading('ampherage', str(dt.now()), 375.3)
        self.assertRaises(SendError, self.client.send_all)


class Test_Client_0_1_404Response(Test_Client_0_1):
    """
    Test when the server returns a 404
    """
    @responses.activate
    def testSend_All(self):
        responses.add(
            responses.POST, url,
            body='{"error": "not found"}', status=404,
            content_type='application/json'
        )
        self.client.reading('level', str(dt.now()), 4.2)
        self.client.reading('ampherage', str(dt.now()), 375.3)
        self.assertRaises(SendError, self.client.send_all)


if __name__ == '__main__':
    unittest.main()
