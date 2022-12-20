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

        paginator = self.client.get_paginator('describe_events')
        response_iterator = paginator.paginate(**query)

        events = []
        for response in response_iterator:
            events.extend(response['events'])

        return events

    def describe_event_details(self, event_arns):
        response = self.client.describe_event_details(eventArns=event_arns)
        return response.get('successfulSet', [])

    def describe_affected_entities(self, **query):
        query = self.generate_query(is_paginate=True, **query)

        paginator = self.client.get_paginator('describe_affected_entities')
        response_iterator = paginator.paginate(**query)

        entities = []
        for response in response_iterator:
            entities.extend(response['entities'])

        return entities

    def describe_entity_aggregates(self, event_arn, **query):
        query = self.generate_query(is_paginate=True, **query)

        response = self.client.describe_entity_aggregates(eventArns=event_arn, **query)
        return response.get('events', [])
