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
import pynsxv.library.nsx_dlr as nsx_router
import library.nsx_esg_dlr as cfy_dlr
import library.nsx_common as common


@operation
def create(**kwargs):
    use_existing, interface = common.get_properties_and_validate(
        'interface', kwargs
    )

    if use_existing:
        ctx.logger.info("Used existed, no changes made")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    result_raw = cfy_dlr.dlr_add_interface(client_session,
                                           interface['dlr_id'],
                                           interface['interface_ls_id'],
                                           interface['interface_ip'],
                                           interface['interface_subnet'],
                                           interface['name'],
                                           interface['vnic'])

    resource_id = result_raw['body']['interfaces']['interface']['index']
    ctx.instance.runtime_properties['resource_dlr_id'] = interface['dlr_id']
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

    result_raw = nsx_router.dlr_del_interface(
        client_session,
        ctx.instance.runtime_properties['resource_dlr_id'],
        resource_id
    )

    common.check_raw_result(result_raw)

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None
