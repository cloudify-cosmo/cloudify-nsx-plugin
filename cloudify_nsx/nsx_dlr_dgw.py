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
from nsx_common import nsx_login
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))
    client_session = nsx_login(nsx_auth)

    interface = properties.get('gateway', {})
    interface.update(kwargs.get('gateway', {}))
    use_existed = interface.get('use_external_resource', False)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    result_raw = nsx_router.dlr_set_dgw(client_session,
        str(interface['dlr_id']),
        str(interface['address'])
    )

    if result_raw['status'] < 200 and result_raw['status'] >= 300:
        ctx.logger.error("Status %s" % result_raw['status'])
        raise cfy_exc.NonRecoverableError(
            "Can't create gateway."
        )

    ctx.instance.runtime_properties['resource_dlr_id'] =  str(interface['dlr_id'])
    ctx.instance.runtime_properties['resource_id'] = interface['address']
    ctx.logger.info("created %s" % str(interface['address']))

@operation
def delete(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))
    client_session = nsx_login(nsx_auth)

    interface = properties.get('gateway', {})
    interface.update(kwargs.get('gateway', {}))
    use_existed = interface.get('use_external_resource', False)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    if 'resource_id' not in ctx.instance.runtime_properties:
        ctx.logger.info("Not fully created, skip")
        return

    result_raw = nsx_router.dlr_del_dgw(client_session,
        str(ctx.instance.runtime_properties['resource_dlr_id'])
    )

    if result_raw['status'] < 200 and result_raw['status'] >= 300:
        ctx.logger.error("Status %s" % result_raw['status'])
        raise cfy_exc.NonRecoverableError(
            "Can't delete gateway."
        )

    ctx.logger.info("delete %s" % ctx.instance.runtime_properties['resource_id'])
