from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, SearchField
from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse, \
    CloudServiceTypeMeta


cst_phd = CloudServiceTypeResource()
cst_phd.name = 'Event'
cst_phd.provider = 'aws'
cst_phd.group = 'PersonalHealthDashboard'
cst_phd.labels = ['Management']
cst_phd.is_primary = True
cst_phd.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/aws/AWS-Personal-Health-Dashboard.svg',
}

cst_phd._metadata = CloudServiceTypeMeta.set_meta(
    fields=[
        TextDyField.data_source('Event', 'data.event_type_code'),
        TextDyField.data_source('Status', 'data.status_code'),
        TextDyField.data_source('Event Category', 'data.event_type_category'),
        TextDyField.data_source('Region', 'region_code'),
        TextDyField.data_source('Start Time', 'data.start_time'),
        TextDyField.data_source('Last Update Time', 'data.last_update_time'),
        TextDyField.data_source('Affected Resources', 'data.affected_resource_display'),
    ],
    search=[
        SearchField.set(name='ARN', key='data.arn'),
        SearchField.set(name='Event', key='data.event_type_code'),
        SearchField.set(name='Event Category', key='data.event_type_category'),
        SearchField.set(name='Event Scope Code', key='data.event_scope_code'),
        SearchField.set(name='Status Code', key='data.status_code'),
        SearchField.set(name='Service', key='data.service'),
        SearchField.set(name='Start Time', key='data.start_time', data_type='datetime'),
        SearchField.set(name='Last Update Time', key='data.last_update_time', data_type='datetime'),
        SearchField.set(name='End Time', key='data.end_type', data_type='datetime'),
        SearchField.set(name='Affected Resource', key='data.affected_resources.entity_value')
    ]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_phd}),
]
