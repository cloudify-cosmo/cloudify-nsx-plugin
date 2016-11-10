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
import library.nsx_esg_dlr as cfy_dlr
import library.nsx_common as common


@operation
def create(**kwargs):
    use_existed, relay_dict = common.get_properties_and_validate(
        'relay', kwargs
    )

    if use_existed:
        ctx.logger.info("Used existed, no chnages made")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    cfy_dlr.update_dhcp_relay(
        client_session,
        relay_dict['dlr_id'],
        relay_dict['relayServer'],
        relay_dict['relayAgents']
    )

    resource_id = relay_dict['dlr_id']
    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s" % resource_id)


@operation
def delete(**kwargs):
    use_existed, relay_dict = common.get_properties(
        'relay', kwargs
    )

    if use_existed:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    ctx.logger.info("checking %s" % resource_id)

    client_session.delete('dhcpRelay', uri_parameters={'edgeId': resource_id})

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None
