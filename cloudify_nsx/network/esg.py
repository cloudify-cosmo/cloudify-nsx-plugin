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
import pynsxv.library.nsx_esg as nsx_esg
import cloudify_nsx.library.nsx_common as common
from cloudify import exceptions as cfy_exc
import cloudify_nsx.library.nsx_esg_dlr as nsx_dlr


@operation
def create(**kwargs):
    validation_rules = {
        # we need name in any case of usage except predefined 'id'
        "name": {
            "required": True,
            "external_use": False
        },
        "esg_pwd": {
            "required": True,
            "external_use": False
        },
        "esg_size": {
            "default": "compact",
            "values": [
                "compact",
                "large",
                "quadlarge",
                "xlarge"
            ]
        },
        "datacentermoid": {
            "required": True,
            "external_use": False
        },
        "datastoremoid": {
            "required": True,
            "external_use": False
        },
        "resourcepoolid": {
            "required": True,
            "external_use": False
        },
        "default_pg": {
            "required": True,
            "external_use": False
        },
        "esg_username": {
            "default": "admin"
        },
        "esg_remote_access": {
            "default": False,
            "type": "boolean"
        }
    }

    use_existing, edge_dict = common.get_properties_and_validate(
        'edge', kwargs, validation_rules
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')

    # credentials
    client_session = common.nsx_login(kwargs)

    if use_existing and resource_id:
        name = common.get_edgegateway(client_session, resource_id)['name']
        edge_dict['name'] = name
        ctx.instance.runtime_properties['edge']['name'] = name

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)

    if not resource_id:
        resource_id, _ = nsx_esg.esg_read(client_session, edge_dict["name"])
        if use_existing:
            ctx.instance.runtime_properties['resource_id'] = resource_id
            ctx.logger.info("Used existed %s" % resource_id)
        elif resource_id:
            raise cfy_exc.NonRecoverableError(
                "Edge '%s' already exists" % edge_dict["name"]
            )

    if not resource_id:
        resource_id, location = nsx_esg.esg_create(
            client_session,
            edge_dict['name'],
            edge_dict['esg_pwd'],
            edge_dict['esg_size'],
            edge_dict['datacentermoid'],
            edge_dict['datastoremoid'],
            edge_dict['resourcepoolid'],
            edge_dict['default_pg'],
            edge_dict['esg_username'],
            edge_dict['esg_remote_access']
        )

        ctx.instance.runtime_properties['resource_id'] = resource_id
        ctx.instance.runtime_properties['location'] = location
        ctx.logger.info("created %s | %s" % (resource_id, location))

    nsx_dlr.update_common_edges(client_session, resource_id, kwargs, True)


@operation
def delete(**kwargs):
    use_existing, edge_dict = common.get_properties('edge', kwargs)

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("We dont have resource_id")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    if use_existing:
        ctx.logger.info("Used existed %s" % edge_dict.get('name'))
        nsx_dlr.update_common_edges(client_session, resource_id, kwargs, True)
        return

    ctx.logger.info("checking %s" % resource_id)

    client_session.delete('nsxEdge', uri_parameters={'edgeId': resource_id})

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None
