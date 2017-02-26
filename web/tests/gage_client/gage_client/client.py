from itsdangerous import JSONWebSignatureSerializer
import requests
import logging


class SendError(Exception):
    """
    Error during sending
    """
    # http://stackoverflow.com/a/12370499/3658919 for storing details
    sucessful = []
    fail = []


class AuthenticationError(SendError):
    """
    Failed to authenticate with server
    """
    pass


class Client(object):
    """
    Generic API Client
    """
    def __new__(cls, url, id, password):
        """
        Builds the right client class for the API based on the url given
        """
        if '/0.1' in url:
            logging.debug('Creating Client_0_1 for API version 0.1')
            return Client_0_1.__new__(Client_0_1, url, id, password)
        logging.error('Did not create Client based on url')

    def __init__(self, url, id, password):
        """
        Initialize a new client

        Parameters:
            url (str): URL for aPI endpoint
            id (int): Client ID number
            password (str): Password string to submit samples
        """
        logging.error('__init__ not implemented on generic Client class')
        raise NotImplementedError

    def reading(self, sensor, dt, value):
        """
        Add a new reading to the ones the Client will send to the server
        """
        logging.error('reading method not implemented on generic Client class')
        raise NotImplementedError

    def readings(self):
        """
        Return current readings
        """
        logging.error('readings method not implemented on generic Client class')
        raise NotImplementedError

    def send_all(self):
        logging.error('send_all method not implemented on generic Client class')  # pragma: no cover
        raise NotImplementedError


class Client_0_1(Client):
    def __new__(cls, url, id, password):
        instance = object.__new__(Client_0_1)
        return instance

    def __init__(self, url, id, password):
        """
        Initialize a new client

        Parameters:
            url (str): Url for API endpoint
            id (int): Client ID number
            password (str): Shared password string for signature
        """
        self.url = url
        self.id = id
        self.serializer = JSONWebSignatureSerializer(password)
        self.samples = []
        logging.debug('Client_0_1 initialized for {url} and gage id {id}'.format(url=url, id=id))

    def reading(self, sensor, dt, value, id=None):
        """
        Add a new reading to send at next connection

        Parameters:
            sensor (str): Type of sensor (level, current, voltage)
            dt (datetime string): Datetime string of sensor reading
            value (float): Float value of sensor reading
            id (int): Integer identifying sample, if not given, just use length of sample list
        """
        if id is None:
            self.samples.append({'type': sensor,
                                 'datetime': dt,
                                 'value': value,
                                 'sender_id': len(self.samples)})
        else:
            self.samples.append({'type': sensor,
                                 'datetime': dt,
                                 'value': value,
                                 'sender_id': id})
        return True

    def readings(self):
        """
        Return current readings
        """
        return self.samples

    def send_all(self):
        """
        Send all samples to server
        """

        payload = {'samples': self.samples,
                   'gage': {'id': self.id}}

        data = self.serializer.dumps(payload)
        sucessful_ids = []

        r = requests.post(self.url, data=data)

        try:
            r.json()
        except ValueError:
            exc = SendError('Failed to send')
            exc.fail = self.samples
            exc.sucessful = sucessful_ids
            raise exc

        # Check status codes to see if there was an authentication error
        if r.status_code == 401:
            exc = AuthenticationError('Failure to Authenticate')
            exc.fail = self.samples
            exc.sucessful = sucessful_ids
            raise exc

        # Else we did something
        elif r.status_code == 200 and r.json()['result'] == 'created':
            for sample in r.json()['samples']:
                sucessful_ids.append(sample['sender_id'])
            self.samples = [x for x in self.samples if not x['sender_id'] in sucessful_ids]

            # If not everything was popped from self.samples, then there was
            # a failure in sending
            if len(self.samples) > 0:
                exc = SendError('Partial send')
                exc.fail = self.samples
                exc.sucessful = sucessful_ids
                raise exc
            return (True, sucessful_ids)

        # Fail and give status code if known
        if r.status_code:
            exc = SendError('Unknown Send Error, HTTP Code:', r.status_code)
        # Otherwise more generic message
        else:
            exc = SendError('Unknown Send Error')
        exc.fail = self.samples
        exc.sucessful = sucessful_ids
        raise exc
