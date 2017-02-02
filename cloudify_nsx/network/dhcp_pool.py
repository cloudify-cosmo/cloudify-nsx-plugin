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
import cloudify_nsx.library.nsx_esg_dlr as nsx_dhcp


@operation
def create(**kwargs):
    validations_rules = {
        "esg_id": {
            "required": True
        },
        "ip_range": {
            "required": True
        },
        "default_gateway": {
            "set_none": True
        },
        "subnet_mask": {
            "set_none": True
        },
        "domain_name": {
            "set_none": True
        },
        "dns_server_1": {
            "set_none": True
        },
        "dns_server_2": {
            "set_none": True
        },
        "lease_time": {
            "set_none": True
        },
        "auto_dns": {
            "set_none": True
        }
    }

    use_existing, pool_dict = common.get_properties_and_validate(
        'pool', kwargs, validations_rules
    )

    if use_existing:
        ctx.logger.info("Used pre existed!")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = nsx_dhcp.add_dhcp_pool(client_session,
                                         pool_dict['esg_id'],
                                         pool_dict['ip_range'],
                                         pool_dict['default_gateway'],
                                         pool_dict['subnet_mask'],
                                         pool_dict['domain_name'],
                                         pool_dict['dns_server_1'],
                                         pool_dict['dns_server_2'],
                                         pool_dict['lease_time'],
                                         pool_dict['auto_dns'])

    ctx.instance.runtime_properties['resource_id'] = resource_id

    ctx.logger.info("created %s | %s" % (resource_id, pool_dict['esg_id']))


@operation
def delete(**kwargs):
    use_existing, pool_dict = common.get_properties('pool', kwargs)

    if use_existing:
        ctx.logger.info("Used pre existed!")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("We dont have resource_id")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    common.attempt_with_rerun(
        nsx_dhcp.delete_dhcp_pool,
        client_session=client_session,
        esg_id=pool_dict['esg_id'],
        pool_id=resource_id
    )

    ctx.logger.info("deleted %s" % resource_id)

    common.remove_properties('pool')
