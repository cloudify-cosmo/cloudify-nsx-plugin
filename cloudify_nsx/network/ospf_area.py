########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
from cloudify import ctx
from cloudify.decorators import operation
import cloudify_nsx.library.nsx_esg_dlr as cfy_dlr
import cloudify_nsx.library.nsx_common as common


@operation
def create(**kwargs):
    validation_rules = {
        "dlr_id": {
            "required": True
        },
        "areaId": {
            "required": True
        },
        "type": {
            "required": True,
            "values": [
                "normal",
                "nssa"
            ]
        },
        "authentication": {
            "set_none": True,
            "sub": {
                "type": {
                    "required": True,
                    "values": [
                        "none",
                        "password",
                        "md5"
                    ]
                },
                "value": {
                    "set_none": True,
                    "required": False
                }
            }
        }
    }

    use_existing, area = common.get_properties_and_validate(
        'area', kwargs, validation_rules
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        if not use_existing:
            return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = cfy_dlr.add_esg_ospf_area(
        client_session,
        area['dlr_id'],
        area['areaId'],
        use_existing,
        area['type'],
        area['authentication']
    )

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s" % resource_id)


@operation
def delete(**kwargs):
    use_existing, area = common.get_properties('area', kwargs)

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    cfy_dlr.del_esg_ospf_area(
        client_session,
        resource_id
    )

    ctx.logger.info("deleted %s" % resource_id)

    common.remove_properties('area')
