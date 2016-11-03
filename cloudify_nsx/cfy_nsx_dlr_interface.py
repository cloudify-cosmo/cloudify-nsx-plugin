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
import library.nsx_common as common


@operation
def create(**kwargs):
    # credentials
    client_session = common.nsx_login(kwargs)

    use_existed, interface = common.get_properties('interface', kwargs)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    result_raw = nsx_router.dlr_add_interface(client_session,
                                              interface['dlr_id'],
                                              interface['interface_ls_id'],
                                              interface['interface_ip'],
                                              interface['interface_subnet'])
    common.check_raw_result(result_raw)

    resource_id = result_raw['body']['interfaces']['interface']['index']
    location = result_raw['body']['interfaces']['interface']['name']
    ctx.instance.runtime_properties['resource_dlr_id'] = interface['dlr_id']
    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.instance.runtime_properties['location'] = location
    ctx.logger.info("created %s | %s" % (resource_id, location))


@operation
def delete(**kwargs):
    use_existed, interface = common.get_properties('interface', kwargs)

    if use_existed:
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
