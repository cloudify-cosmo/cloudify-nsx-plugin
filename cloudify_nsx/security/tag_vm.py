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
from cloudify import exceptions as cfy_exc
import cloudify_nsx.library.nsx_security_tag as nsx_security_tag
import cloudify_nsx.library.nsx_common as common


@operation
def create(**kwargs):
    validation_rules = {
        "tag_id": {
            "required": True
        },
        "vm_id": {
            "required": True
        }
    }

    use_existing, vm_tag = common.get_properties_and_validate(
        'vm_tag', kwargs, validation_rules
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = nsx_security_tag.add_tag_vm(
        client_session,
        vm_tag['tag_id'],
        vm_tag['vm_id'],
    )

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s" % resource_id)


@operation
def delete(**kwargs):
    use_existing, vm_tag = common.get_properties('vm_tag', kwargs)

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    try:
        nsx_security_tag.delete_tag_vm(
            client_session, resource_id
        )
    except Exception as ex:
        ctx.logger.error("We have issue with remove: %s", str(ex))
        raise cfy_exc.RecoverableError(
            message="Retry to delete little later", retry_after=30
        )

    ctx.logger.info("deleted %s" % resource_id)

    common.remove_properties('vm_tag')
