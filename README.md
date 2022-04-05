<h1 align="center">AWS PHD(Personal Health Dashboard) Collector</h1>  

<br/>  
<div align="center" style="display:flex;">  
  <img width="245" src="https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-cloudservice.svg">
  <p> 
    <br>
    <img alt="Version"  src="https://img.shields.io/badge/version-1.4.3-blue.svg?cacheSeconds=2592000"  />    
    <a href="https://www.apache.org/licenses/LICENSE-2.0"  target="_blank"><img alt="License: Apache 2.0"  src="https://img.shields.io/badge/License-Apache 2.0-yellow.svg" /></a> 
  </p> 
</div>    

### Plugin to collect AWS Personal Health Dashboard

> SpaceONE's [plugin-aws-phd-inven-collector](https://github.com/spaceone-dev/plugin-aws-phd-inven-collector) is a convenient tool to get PHD(Personal Heath Dashboard) from AWS.


Find us also at [Dockerhub](https://hub.docker.com/repository/docker/spaceone/aws-cloud-services)
> Latest stable version : 1.4.3

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

### Ver 1.4.3
Bugfix
* [modify cloud service type](https://github.com/spaceone-dev/plugin-aws-phd-inven-collector/commit/a93be4c7be6e2311b19bee825243fed802020630)

### Ver 1.4.2
Bugfix
* Error resource (#20)

### Ver 1.4.1
Enhancement
* Apply Error resource (#19)

### Ver 1.4
* Add name field for standardization.(#15)
* Remove to_date filter in query to collect future data all
