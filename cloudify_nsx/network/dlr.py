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
import cloudify_nsx.library.nsx_common as common
from cloudify import exceptions as cfy_exc
import cloudify_nsx.library.nsx_esg_dlr as nsx_dlr


@operation
def create(**kwargs):
    validation_rules = {
        "name": {
            "required": True
        },
        "dlr_pwd": {
            "required": True
        },
        "dlr_size": {
            "default": "compact",
            "values": [
                "compact",
                "large",
                "quadlarge",
                "xlarge"
            ]
        },
        "ha_ls_id": {
            "required": True
        },
        "uplink_ls_id": {
            "required": True
        },
        "uplink_ip": {
            "required": True
        },
        "uplink_subnet": {
            "required": True
        },
        "uplink_dgw": {
            "required": True
        }
    }

    use_existing, router_dict = common.get_properties_and_validate(
        'router', kwargs, validation_rules
    )

    ctx.logger.info("checking %s" % router_dict["name"])

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = ctx.instance.runtime_properties.get('resource_id')

    if not use_existing and not resource_id:
        resource_id, _ = nsx_router.dlr_read(
            client_session, router_dict["name"]
        )
        if use_existing:
            ctx.instance.runtime_properties['resource_id'] = resource_id
            ctx.logger.info("Used existed %s" % resource_id)
        elif resource_id:
            raise cfy_exc.NonRecoverableError(
                "Router '%s' already exists" % router_dict["name"]
            )
    if not resource_id:
        # update properties with vcenter specific values,
        # required only on create
        router_dict = common.possibly_assign_vm_creation_props(router_dict)
        resource_id, _ = nsx_router.dlr_create(
            client_session,
            router_dict['name'],
            router_dict['dlr_pwd'],
            router_dict['dlr_size'],
            router_dict['datacentermoid'],
            router_dict['datastoremoid'],
            router_dict['resourcepoolid'],
            router_dict['ha_ls_id'],
            router_dict['uplink_ls_id'],
            router_dict['uplink_ip'],
            router_dict['uplink_subnet'],
            router_dict['uplink_dgw'])
        ctx.instance.runtime_properties['resource_id'] = resource_id
        ctx.logger.info("created %s" % resource_id)

    uplink_vnic = nsx_dlr.get_uplink_vnic(
        client_session, resource_id, router_dict['uplink_ls_id'])

    ctx.instance.runtime_properties['router']['uplink_vnic'] = uplink_vnic

    nsx_dlr.update_common_edges(client_session, resource_id, kwargs, False)


@operation
def delete(**kwargs):
    use_existing, router_dict = common.get_properties('router', kwargs)

    if use_existing:
        ctx.logger.info("Used pre existed!")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("We dont have resource_id")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    try:
        client_session.delete('nsxEdge', uri_parameters={
            'edgeId': resource_id
        })
    except Exception as ex:
        ctx.logger.error("We have issue with remove: %s", str(ex))
        raise cfy_exc.RecoverableError(
            message="Retry to delete little later", retry_after=30
        )

    ctx.logger.info("deleted %s" % resource_id)

    nsx_dlr.remove_properties_edges()
