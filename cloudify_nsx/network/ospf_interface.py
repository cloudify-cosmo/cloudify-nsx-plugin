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
from cloudify import exceptions as cfy_exc
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
        # must be vnic with uplink
        "vnic": {
            "required": True
        },
        "helloInterval": {
            "default": 10,
            "type": "string"
        },
        "deadInterval": {
            "default": 40,
            "type": "string",
        },
        "priority": {
            "default": 128,
            "type": "string"
        },
        "cost": {
            "set_none": True
        }
    }

    use_existing, interface = common.get_properties_and_validate(
        'interface', kwargs, validation_rules
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        if not use_existing:
            return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = cfy_dlr.add_esg_ospf_interface(
        client_session,
        interface['dlr_id'],
        interface['areaId'],
        interface['vnic'],
        use_existing,
        interface['helloInterval'],
        interface['deadInterval'],
        interface['priority'],
        interface['cost']
    )

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s" % resource_id)


@operation
def delete(**kwargs):
    use_existing, interface = common.get_properties('interface', kwargs)

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    try:
        cfy_dlr.del_esg_ospf_interface(
            client_session,
            ctx.instance.runtime_properties['resource_id']
        )
    except Exception as ex:
        ctx.logger.error("We have issue with remove: %s", str(ex))
        raise cfy_exc.RecoverableError(
            message="Retry to delete little later", retry_after=30
        )

    ctx.logger.info("deleted %s" % resource_id)

    common.remove_properties('interface')
