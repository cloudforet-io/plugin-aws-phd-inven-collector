from schematics.types import ModelType, StringType, PolyModelType

from spaceone.inventory.model.personal_health_dashboard.data import Event
from spaceone.inventory.libs.schema.metadata.dynamic_field import TextDyField, DateTimeDyField, EnumDyField
from spaceone.inventory.libs.schema.metadata.dynamic_layout import ItemDynamicLayout, TableDynamicLayout
from spaceone.inventory.libs.schema.cloud_service import CloudServiceResource, CloudServiceResponse, CloudServiceMeta


event_meta = ItemDynamicLayout.set_fields('Event', fields=[
    TextDyField.data_source('Event', 'data.event_type_code'),
    TextDyField.data_source('ARN', 'data.arn'),
    EnumDyField.data_source('Status', 'data.status_code', default_state={
        'safe': ['closed'],
        'warning': ['upcoming'],
        'alert': ['open']
    }),
    TextDyField.data_source('Event Scope Code', 'data.event_scope_code'),
    TextDyField.data_source('Event Category', 'data.event_type_category'),
    TextDyField.data_source('Region', 'region_code'),
    TextDyField.data_source('Description', 'data.description'),
    DateTimeDyField.data_source('Start Time', 'data.start_time'),
    DateTimeDyField.data_source('Last Update Time', 'data.last_update_time'),
    DateTimeDyField.data_source('End Time', 'data.end_time'),
])

affected_resources_meta = TableDynamicLayout.set_fields('Affected Resources', 'data.affected_resources', fields=[
    TextDyField.data_source('Account ID', 'aws_account_id'),
    TextDyField.data_source('Entity Value', 'entity_value'),
])

metadata = CloudServiceMeta.set_layouts(layouts=[event_meta, affected_resources_meta])


class PersonalHealthDashboardResource(CloudServiceResource):
    cloud_service_group = StringType(default='PersonalHealthDashboard')


class EventResource(PersonalHealthDashboardResource):
    cloud_service_type = StringType(default='Event')
    data = ModelType(Event)
    _metadata = ModelType(CloudServiceMeta, default=metadata, serialized_name='metadata')


class EventResponse(CloudServiceResponse):
    resource = PolyModelType(EventResource)
