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
from nsx_common import nsx_login
import pynsxv.library.nsx_logical_switch as nsx_logical_switch
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))
    client_session = nsx_login(nsx_auth)

    switch_dict = properties.get('switch', {})
    switch_dict.update(kwargs.get('switch', {}))
    switch_mode = switch_dict.get("mode", "UNICAST_MODE")
    use_existed = switch_dict.get('use_external_resource', False)

    ctx.logger.info("checking %s" % str(switch_dict["name"]))

    resource_id, switch_params = nsx_logical_switch.logical_switch_read(client_session, str(switch_dict["name"]))
    if use_existed:
        ctx.instance.runtime_properties['resource_id'] = resource_id
        ctx.logger.info("Used existed %s" % str(resource_id))

    elif resource_id:
        raise cfy_exc.NonRecoverableError(
            "We already have such switch"
        )

    if not use_existed:
        # nsx does not understand unicode strings
        ctx.logger.info("creating %s" % str(switch_dict["name"]))
        resource_id, location = nsx_logical_switch.logical_switch_create(
            client_session, switch_dict["transport_zone"],
            str(switch_dict["name"]), switch_mode
        )
        ctx.instance.runtime_properties['location'] = location
        ctx.logger.info("created %s | %s" % (str(resource_id), str(location)))
        switch_params = None

    if not switch_params:
        resource_id, switch_params = nsx_logical_switch.logical_switch_read(client_session, str(switch_dict["name"]))

    resource_dvportgroup_id = switch_params.get('vdsContextWithBacking', {}).get('backingValue')

    ctx.instance.runtime_properties['resource_dvportgroup_id'] = resource_dvportgroup_id
    ctx.instance.runtime_properties['resource_id'] = resource_id


@operation
def delete(**kwargs):
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))

    switch_dict = properties.get('switch', {})
    switch_dict.update(kwargs.get('switch', {}))
    use_existed = switch_dict.get('use_external_resource', False)

    if use_existed:
        ctx.logger.info("Used pre existed!")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("We dont have resource_id")
        return

    client_session = nsx_login(nsx_auth)

    ctx.logger.info("deleting %s" % str(resource_id))

    client_session.delete('logicalSwitch', uri_parameters={'virtualWireID': str(resource_id)})

    ctx.logger.info("deleted %s" % str(resource_id))

    ctx.instance.runtime_properties['resource_id'] = None
