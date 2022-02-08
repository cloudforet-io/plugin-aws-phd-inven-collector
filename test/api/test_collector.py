import os
import unittest
import pprint

from google.protobuf.json_format import MessageToDict
from spaceone.core import utils, pygrpc
from spaceone.core.unittest.runner import RichTestRunner

ENDPOINT = 'grpc://localhost:50051'


class TestCollector(unittest.TestCase):

    pp = pprint.PrettyPrinter(indent=4)
    identity_v1 = None
    domain = None
    domain_owner = None
    owner_id = None
    owner_pw = None
    owner_token = None

    @classmethod
    def setUpClass(cls):
        super(TestCollector, cls).setUpClass()
        e = utils.parse_grpc_endpoint(ENDPOINT)
        cls.client = pygrpc.client(endpoint=e['endpoint'], ssl_enabled=e['ssl_enabled'])
        cls.secret_data = {
            'aws_access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        }

    @classmethod
    def tearDownClass(cls):
        super(TestCollector, cls).tearDownClass()

    def _print_data(self, message, description=None):
        print()
        if description:
            print(f'[ {description} ]')

        self.pp.pprint(MessageToDict(message, preserving_proto_field_name=True))

    def test_init(self):
        message = self.client.Collector.init({'options': {}})
        self._print_data(message, 'test_init')

    def test_verify(self):
        options = {
            'domain': 'mz.co.kr'
        }
        message = self.client.Collector.verify({'options': options, 'secret_data': self.secret_data})
        self._print_data(message, 'test_verify')

    def test_collect(self):
        options = {}
        filter = {}

        res_iterator = self.client.Collector.collect(
            {'options': options, 'secret_data': self.secret_data, 'filter': filter}
        )

        for message in res_iterator:
            response = MessageToDict(message, preserving_proto_field_name=True)
            try:
                if response['resource']['data']['resources_summary']['resources_flagged'] > 0:
                    print(response)
            except:
                pass
            # self.assertEqual('CLOUD_SERVICE', res.resource_type)

if __name__ == '__main__':
    unittest.main(testRunner=RichTestRunner)