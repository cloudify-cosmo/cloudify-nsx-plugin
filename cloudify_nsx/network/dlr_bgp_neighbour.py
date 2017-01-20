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


def _create(kwargs, validation_rules):
    use_existing, neighbour = common.get_properties_and_validate(
        'neighbour', kwargs, validation_rules
    )

    print use_existing, neighbour

    if use_existing:
        ctx.logger.info("Used existed, no changes made")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = cfy_dlr.add_bgp_neighbour(
        client_session,
        neighbour['dlr_id'],
        use_existing,
        neighbour['ipAddress'],
        neighbour['remoteAS'],
        neighbour['weight'],
        neighbour['holdDownTimer'],
        neighbour['keepAliveTimer'],
        neighbour['password'],
        neighbour.get('protocolAddress'),
        neighbour.get('forwardingAddress')
    )

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s" % resource_id)


@operation
def create_dlr(**kwargs):
    validation_rules = {
        'holdDownTimer': {
            'default': 180,
            'type': 'string'
        },
        'weight': {
            'default': 60,
            'type': 'string'
        },
        'remoteAS': {
            'required': True
        },
        'protocolAddress': {
            'required': True
        },
        'dlr_id': {
            'required': True
        },
        'forwardingAddress': {
            'required': True
        },
        'password': {
            'set_none': True
        },
        'ipAddress': {
            'required': True
        },
        'keepAliveTimer': {
            'default': 60,
            'type': 'string'
        }
    }
    _create(kwargs, validation_rules)


@operation
def create_esg(**kwargs):
    validation_rules = {
        "dlr_id": {
            "required": True
        },
        "ipAddress": {
            "required": True
        },
        "remoteAS": {
            "required": True
        },
        "weight": {
            "type": "string",
            "default": 60
        },
        "holdDownTimer": {
            "type": "string",
            "default": 180
        },
        "keepAliveTimer": {
            "type": "string",
            "default": 60
        },
        "password": {
            "set_none": True
        }
    }
    _create(kwargs, validation_rules)


@operation
def delete(**kwargs):
    use_existing, neighbour = common.get_properties('neighbour', kwargs)

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    cfy_dlr.del_bgp_neighbour(
        client_session,
        resource_id
    )

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None
