import time
import datetime
from spaceone.inventory.libs.manager import AWSManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.connector.personal_health_dashboard import PersonalHealthDashboardConnector
from spaceone.inventory.model.personal_health_dashboard.data import Event, AffectedResource
from spaceone.inventory.model.personal_health_dashboard.cloud_service import EventResource, EventResponse
from spaceone.inventory.model.personal_health_dashboard.cloud_service_type import CLOUD_SERVICE_TYPES


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

        if event_arns:
            filter_query = {'filter': {'eventArns': event_arns}}
        else:
            filter_query = {}

        affected_resources = phd_conn.describe_affected_entities(**filter_query)
        affected_resources = self._filter_affected_entities(affected_resources)

        event_details = phd_conn.describe_event_details(event_arns)

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
                'account_id': params['account_id'],
                'description': self._find_event_description(event_details, event['arn']),
                'affected_resources': affected_resources_data
            })

            if affected_resources_data:
                event.update({
                    'affected_resource_display': f'{len(affected_resources_data)} entity'
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

        to_date = datetime.datetime.now()
        from_date = to_date + datetime.timedelta(days=-14)      # 2 weeks ago

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
