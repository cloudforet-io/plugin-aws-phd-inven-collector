import logging
from botocore.exceptions import ClientError

from spaceone.inventory.libs.connector import AWSConnector
from spaceone.inventory.error.custom import *

__all__ = ['PersonalHealthDashboardConnector']
_LOGGER = logging.getLogger(__name__)


class PersonalHealthDashboardConnector(AWSConnector):
    service = 'health'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def describe_events(self, **query):
        query = self.generate_query(is_paginate=True, **query)

        try:
            paginator = self.client.get_paginator('describe_events')
            response_iterator = paginator.paginate(**query)

            events = []
            for response in response_iterator:
                events.extend(response['events'])

            return events

        except ClientError as e:
            if e.response['Error']['Code'] == 'SubscriptionRequiredException':
                raise ERROR_SUBSCRIPTION_REQUIRED()
            else:
                _LOGGER.error(e)
                raise ERROR_AWS_BOTO_REQUEST(message=e)

        except Exception as e:
            _LOGGER.error(f'Fail to describe events: {e}')
            raise ERROR_AWS_BOTO_REQUEST(message=e)

    def describe_event_details(self, event_arns):
        try:
            response = self.client.describe_event_details(eventArns=event_arns)
            return response.get('successfulSet', [])

        except Exception as e:
            _LOGGER.error(f'Fail to describe event details: {e}')
            raise ERROR_AWS_BOTO_REQUEST(message=e)

    def describe_affected_entities(self, **query):
        query = self.generate_query(is_paginate=True, **query)

        try:
            paginator = self.client.get_paginator('describe_affected_entities')
            response_iterator = paginator.paginate(**query)

            entities = []
            for response in response_iterator:
                entities.extend(response['entities'])

            return entities

        except Exception as e:
            _LOGGER.error(f'Fail to describe affected entities: {e}')
            raise ERROR_AWS_BOTO_REQUEST(message=e)

    def describe_entity_aggregates(self, event_arn, **query):
        query = self.generate_query(is_paginate=True, **query)

        try:
            response = self.client.describe_entity_aggregates(eventArns=event_arn, **query)
            return response.get('events', [])

        except ClientError as e:
            if e.response['Error']['Code'] == 'SubscriptionRequiredException':
                raise ERROR_SUBSCRIPTION_REQUIRED()
            else:
                _LOGGER.error(e)
                raise ERROR_AWS_BOTO_REQUEST(message=e)

        except Exception as e:
            _LOGGER.error(f'Fail to describe entity aggregates: {e}')
            raise ERROR_AWS_BOTO_REQUEST(message=e)
