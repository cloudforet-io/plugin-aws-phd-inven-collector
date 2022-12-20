import time
import logging
import concurrent.futures

from spaceone.core.service import *
from spaceone.inventory.libs.connector import *
from spaceone.inventory.conf.cloud_service_conf import *

_LOGGER = logging.getLogger(__name__)


class CollectorService(BaseService):
    def __init__(self, metadata):
        super().__init__(metadata)

    @transaction
    @check_required(['options'])
    def init(self, params):
        """ init plugin by options
        """
        capability = {
            'filter_format': FILTER_FORMAT,
            'supported_resource_type': SUPPORTED_RESOURCE_TYPE,
            'supported_features': SUPPORTED_FEATURES,
            'supported_schedules': SUPPORTED_SCHEDULES
        }
        return {'metadata': capability}

    @transaction
    @check_required(['options', 'secret_data'])
    def verify(self, params):
        """
        Args:
              params:
                - options
                - secret_data
        """
        options = params['options']
        secret_data = params.get('secret_data', {})

        if not secret_data:
            self.get_account_id(secret_data)

        return {}

    @transaction
    @check_required(['options', 'secret_data', 'filter'])
    def collect(self, params):
        """
        Args:
            params:
                - options
                - secret_data
                - filter
        """

        secret_data = params['secret_data']
        params.update({'account_id': self.get_account_id(secret_data)})

        start_time = time.time()

        _manager = self.locator.get_manager(EXECUTE_MANAGER)

        for resource in _manager.collect_resources(params):
            yield resource.to_primitive()

        _LOGGER.debug(f'[collect] TOTAL FINISHED TIME : {time.time() - start_time} Seconds')

    @staticmethod
    def get_account_id(secret_data, region=DEFAULT_REGION):
        aws_connector = AWSConnector(secret_data=secret_data)
        aws_connector.service = 'sts'
        aws_connector.set_client(region)
        return aws_connector.client.get_caller_identity()['Account']
