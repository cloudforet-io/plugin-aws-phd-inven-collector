# plugin-aws-personal-health-dashboard
**Plugin to collect AWS Personal Health Dashboard

> SpaceONE's [plugin-aws-personal-health-dashboard](https://github.com/spaceone-dev/plugin-aws-personal-health-dashboard) is a convenient tool to get PHD(Personal Heath Dashboard) from AWS.


Find us also at [Dockerhub](https://hub.docker.com/repository/docker/spaceone/aws-cloud-services)
> Latest stable version : 1.4

Please contact us if you need any further information. (<support@spaceone.dev>)

---

## Collecting Contents

* Table of Contents
    * Event


---

## Authentication Overview

Registered service account on SpaceONE must have certain permissions to collect cloud service data Please, set
authentication privilege for followings:

<pre>
<code>
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "health:Describe*"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
</code>
</pre>


---

## Release Note

### Ver 1.4

* Add name field for standardization.
* Remove to_date filter in query to collect future data all
