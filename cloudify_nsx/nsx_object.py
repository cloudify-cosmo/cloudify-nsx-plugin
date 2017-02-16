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
import cloudify_nsx.library.nsx_common as common
import pynsxv.library.nsx_logical_switch as nsx_logical_switch
import pynsxv.library.nsx_dlr as nsx_router
import cloudify_nsx.library.nsx_security_group as nsx_security_group
import cloudify_nsx.library.nsx_security_policy as nsx_security_policy
import cloudify_nsx.library.nsx_security_tag as nsx_security_tag


@operation
def create(**kwargs):
    validation_rules = {
        "name": {
            "required": True
        },
        "type": {
            "required": True,
            "values": [
                'group',
                'policy',
                'tag',
                'lswitch',
                'router'
            ]
        },
        "scopeId": {
            "default": "globalroot-0",
            "required": True
        }
    }

    _, nsx_object = common.get_properties_and_validate(
        'nsx_object', kwargs, validation_rules
    )

    # credentials
    client_session = common.nsx_login(kwargs)

    if nsx_object['type'] == 'group':
        resource_id, _ = nsx_security_group.get_group(
            client_session,
            nsx_object['scopeId'],
            nsx_object['name']
        )
    elif nsx_object['type'] == 'policy':
        resource_id, _ = nsx_security_policy.get_policy(
            client_session,
            nsx_object['name']
        )
    elif nsx_object['type'] == 'tag':
        resource_id, _ = nsx_security_tag.get_tag(
            client_session,
            nsx_object['name']
        )
    elif nsx_object['type'] == 'lswitch':
        resource_id, switch_params = nsx_logical_switch.logical_switch_read(
            client_session, nsx_object['name']
        )
    elif nsx_object['type'] == 'router':
        resource_id, _ = nsx_router.dlr_read(
            client_session, nsx_object['name']
        )

    runtime_properties = ctx.instance.runtime_properties
    runtime_properties['resource_id'] = resource_id
    runtime_properties['use_external_resource'] = resource_id is not None


@operation
def delete(**kwargs):
    common.remove_properties('nsx_object')
