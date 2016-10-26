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
from cfy_nsx_common import nsx_login, get_properties
from cloudify import exceptions as cfy_exc
import pynsxv.library.nsx_dhcp as nsx_dhcp


@operation
def create(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))
    client_session = nsx_login(nsx_auth)

    use_existed, pool_dict = get_properties('pool', kwargs)

    if use_existed:
        ctx.logger.info("Used pre existed!")
        return

    resource_id = nsx_dhcp.add_dhcp_pool(client_session,
        str(pool_dict['esg_name']),
        str(pool_dict['ip_range']),
        str(pool_dict['default_gateway']),
        str(pool_dict['subnet_mask']),
        str(pool_dict['domain_name']),
        str(pool_dict['dns_server_1']),
        str(pool_dict['dns_server_2']),
        str(pool_dict['lease_time']),
        str(pool_dict['auto_dns'])
    )

    ctx.instance.runtime_properties['resource_id'] = resource_id

    ctx.logger.info("created %s | %s" % (str(resource_id), str(pool_dict['esg_name'])))


@operation
def delete(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))
    client_session = nsx_login(nsx_auth)

    use_existed, pool_dict = get_properties('pool', kwargs)

    if use_existed:
        ctx.logger.info("Used pre existed!")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("We dont have resource_id")
        return

    if not nsx_dhcp.delete_dhcp_pool(client_session,
        str(pool_dict['esg_name']), resource_id
    ):
        raise cfy_exc.NonRecoverableError(
            "Ca't drop dhcp pool"
        )

    ctx.instance.runtime_properties['resource_id'] = None
