from schematics import Model
from schematics.types import ModelType, ListType, StringType, DateTimeType, IntType


class Tags(Model):
    key = StringType()
    value = StringType()


class AffectedResource(Model):
    entity_arn = StringType(deserialize_from='entityArn')
    event_arn = StringType(deserialize_from='eventArn')
    entity_value = StringType()
    entity_type = StringType(choices=('account', 'resource'))
    entity_url = StringType(deserialize_from='entityUrl', serialize_when_none=False)
    aws_account_id = StringType(deserialize_from='awsAccountId')
    last_update_time = DateTimeType(deserialize_from='lastUpdatedTime')
    status_code = StringType(deserialize_from='statusCode', choices=('IMPAIRED', 'UNIMPAIRED', 'UNKNOWN'))
    tags = ListType(ModelType(Tags), default=[])


class Event(Model):
    arn = StringType()
    service = StringType(serialize_when_none=False)
    status_code = StringType(deserialize_from='statusCode', choices=('open', 'closed', 'upcoming'))
    event_scope_code = StringType(deserialize_from='eventScopeCode', choices=('PUBLIC', 'ACCOUNT_SPECIFIC', 'NONE'))
    event_type_code = StringType(deserialize_from="eventTypeCode")
    event_title = StringType(default='')
    event_type_category = StringType(deserialize_from="eventTypeCategory",
                                     choices=('issue', 'accountNotification', 'scheduledChange', 'investigation'))
    availability_zone = StringType(deserialize_from='availabilityZone', serialize_when_none=False)
    start_time = DateTimeType(deserialize_from="startTime")
    last_update_time = DateTimeType(deserialize_from="lastUpdatedTime")
    end_time = DateTimeType(deserialize_from="endTime")
    affected_resources = ListType(ModelType(AffectedResource), default=[])
    affected_resource_display = StringType(default='-')
    description = StringType(default='')
    region = StringType()
    account_id = StringType(default="")

    def reference(self):
        return {
            "resource_id": self.arn,
            "external_link": f"https://phd.aws.amazon.com/phd/home#/event-log?eventID={self.arn}&eventTab=details"
        }
