import time
import datetime
from spaceone.inventory.libs.manager import AWSManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.personal_health_dashboard import PersonalHealthDashboardConnector
from spaceone.inventory.model.personal_health_dashboard.data import Event, AffectedResource
from spaceone.inventory.model.personal_health_dashboard.cloud_service import EventResource, EventResponse
from spaceone.inventory.model.personal_health_dashboard.cloud_service_type import CLOUD_SERVICE_TYPES

DEFAULT_DAY_TO_RANGE = 30
DEFAULT_DAY_FROM_RANGE = 30


class PersonalHealthDashboardManager(AWSManager):
    connector_name = 'PersonalHealthDashboardConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_services(self, params):
        print("** Personal Health Dashboard Start **")
        start_time = time.time()
        phd_conn: PersonalHealthDashboardConnector = self.locator.get_connector(self.connector_name, **params)
        phd_conn.set_client()

        event_resources = []

        options = params.get('options', {})
        all_events = options.get('all_events', False)

        event_query = self.generate_query(params)
        events = phd_conn.describe_events(**event_query)
        event_arns = [event['arn'] for event in events]

        # event_arns Must have length less than or equal to 10. Divide event_arns under 10.
        divide_event_arns_list = list(self._divide_by_event(event_arns))

        filter_queries = []
        for divide_event_arns in divide_event_arns_list:
            filter_queries.append({'filter': {'eventArns': divide_event_arns}})

        affected_resources = []
        for affected_resource_query in filter_queries:
            affected_resources.extend(phd_conn.describe_affected_entities(**affected_resource_query))

        # Filtering 'UNKNOWN' affected entities
        affected_resources = self._filter_affected_entities(affected_resources)

        event_details = []
        for divide_event_arns in divide_event_arns_list:
            event_details.extend(phd_conn.describe_event_details(divide_event_arns))

        for event in events:
            event_affected_resources = self._find_affected_resources(affected_resources, event['arn'])

            affected_resources_data = []
            for affected_resource in event_affected_resources:
                entity_type, entity_value = self._get_entity_type_value(affected_resource)
                affected_resource.update({
                    'entity_type': entity_type,
                    'entity_value': entity_value,
                    'tags': self._convert_tag_format(affected_resource.get('tags', {}))
                })
                affected_resources_data.append(AffectedResource(affected_resource, strict=False))

            event.update({
                'event_title': self._convert_event_tile_from_code(event['eventTypeCode']),
                'account_id': params['account_id'],
                'description': self._find_event_description(event_details, event['arn']),
                'affected_resources': affected_resources_data
            })

            if affected_resources_data:
                event.update({
                    'affected_resource_display': f'{len(affected_resources_data)} entity',
                    'has_affected_resources': True,
                    'affected_resources_count': len(affected_resources_data)
                })

            event_data = Event(event, strict=False)
            event_resource = EventResource({
                'data': event_data,
                'region_code': event['region'],
                'reference': ReferenceModel(event_data.reference())
            })

            event_resources.append(EventResponse({'resource': event_resource}))

        print(f' Personal Health Dashboard Finished {time.time() - start_time} Seconds')
        return event_resources

    @staticmethod
    def _merge_flagged_resources(check_id_data, checkResult):
        """
        Return: list
        """
        headers = ['status', 'region']
        headers.extend(check_id_data.metadata)

        res_list = []
        if 'flaggedResources' in checkResult:
            flagged_resources = checkResult['flaggedResources']
            for res in flagged_resources:
                result = [res['status']]
                if 'region' in res:
                    result.append(res['region'])
                else:
                    result.append("")
                result.extend(res.get('metadata', []))
                res_list.append(result)
        else:
            pass

        resources = []
        for res in res_list:
            data = {}
            for idx in range(len(headers)):
                data[headers[idx]] = res[idx]
            resources.append(data)
        return resources

    @staticmethod
    def generate_query(params):
        options = params.get('options', {})

        now = datetime.datetime.now()
        to_date = now + datetime.timedelta(days=DEFAULT_DAY_TO_RANGE)
        from_date = now - datetime.timedelta(days=DEFAULT_DAY_FROM_RANGE)

        filter_query = {'startTimes': [{'from': from_date, 'to': to_date}]}

        if 'eventStatusCodes' in options:
            filter_query.update({'eventStatusCodes': options['eventStatusCodes']})

        return {'filter': filter_query}

    @staticmethod
    def _find_affected_resources(affected_resources, event_arn):
        return [af for af in affected_resources if af['eventArn'] == event_arn]

    @staticmethod
    def _find_event_description(event_details, event_arn):
        description = [ed.get('eventDescription', {}).get('latestDescription', '') for ed in event_details
                       if ed.get('event', {}).get('arn') == event_arn]

        if description:
            return description[0]
        else:
            return ''

    @staticmethod
    def _get_entity_type_value(affected_resource):
        if affected_resource.get('entityValue') == 'AWS_ACCOUNT':
            return 'account', affected_resource.get('awsAccountId')
        else:
            return 'resource', affected_resource.get('entityValue')

    @staticmethod
    def _convert_tag_format(tags):
        return_tags = []
        for k, v in tags.items():
            return_tags.append({'key': k, 'value': v})

        return return_tags

    @staticmethod
    def _filter_affected_entities(affected_resources):
        return [af for af in affected_resources if af.get('entityValue') != 'UNKNOWN']

    @staticmethod
    def _divide_by_event(event_arns, divide_num=10):
        for i in range(0, len(event_arns), divide_num):
            yield event_arns[i:i + divide_num]

    @staticmethod
    def _convert_event_tile_from_code(event_code):
        try:
            event_title = event_code.replace('AWS_', '').replace('_', ' ').title()
        except Exception as e:
            event_title = event_code

        return event_title

