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
from cfy_nsx_common import nsx_login
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))
    client_session = nsx_login(nsx_auth)

    router_dict = properties.get('router', {})
    router_dict.update(kwargs.get('router', {}))
    use_existed = router_dict.get('use_external_resource', False)

    ctx.logger.info("checking %s" % str(router_dict["name"]))

    resource_id, _ = nsx_router.dlr_read(client_session, str(router_dict["name"]))
    if use_existed:
        ctx.instance.runtime_properties['resource_id'] = resource_id
        ctx.logger.info("Used existed %s" % str(resource_id))
        return
    if resource_id:
        raise cfy_exc.NonRecoverableError(
            "We already have such router"
        )

    resource_id, location = nsx_router.dlr_create(client_session,
        str(router_dict['name']),
        str(router_dict['dlr_pwd']),
        str(router_dict['dlr_size']),
        str(router_dict['datacentermoid']),
        str(router_dict['datastoremoid']),
        str(router_dict['resourcepoolid']),
        str(router_dict['ha_ls_id']),
        str(router_dict['uplink_ls_id']),
        str(router_dict['uplink_ip']),
        str(router_dict['uplink_subnet']),
        str(router_dict['uplink_dgw'])
    )
    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.instance.runtime_properties['location'] = location
    ctx.logger.info("created %s | %s" % (str(resource_id), str(location)))

@operation
def delete(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))

    router_dict = properties.get('router', {})
    router_dict.update(kwargs.get('router', {}))
    use_existed = router_dict.get('use_external_resource', False)

    if use_existed:
        ctx.logger.info("Used pre existed!")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("We dont have resource_id")
        return

    client_session = nsx_login(nsx_auth)

    ctx.logger.info("deleting %s" % str(resource_id))

    client_session.delete('nsxEdge', uri_parameters={'edgeId': resource_id})

    ctx.logger.info("deleted %s" % str(resource_id))

    ctx.instance.runtime_properties['resource_id'] = None