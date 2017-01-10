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
import library.nsx_security_tag as nsx_security_tag
import library.nsx_common as common
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    use_existing, tag = common.get_properties_and_validate(
        'tag', kwargs
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    if not resource_id:
        resource_id, _ = nsx_security_tag.get_tag(client_session,
                                                  tag['name'])

        if use_existing and resource_id:
            ctx.instance.runtime_properties['resource_id'] = resource_id
            ctx.logger.info("Used existed %s" % resource_id)
        elif resource_id:
            raise cfy_exc.NonRecoverableError(
                "Security tag '%s' already exists" % tag['name']
            )

    if not resource_id:
        resource_id, location = nsx_security_tag.add_tag(
            client_session,
            tag['name'],
            tag['description'],
        )

        ctx.instance.runtime_properties['resource_id'] = resource_id
        ctx.logger.info("created %s|%s" % (resource_id, location))


@operation
def delete(**kwargs):
    use_existing, tag = common.get_properties('tag', kwargs)

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    nsx_security_tag.delete_tag(
        client_session,
        resource_id
    )

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None
