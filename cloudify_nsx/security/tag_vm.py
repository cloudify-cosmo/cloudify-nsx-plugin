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
    common.delete_object(
        nsx_security_tag.delete_tag_vm, 'vm_tag',
        kwargs
    )


@operation
def link(**kwargs):
    vm_id = ctx.source.instance.runtime_properties.get('vsphere_server_id')
    tag_id = ctx.target.instance.runtime_properties.get('resource_id')
    ctx.logger.info("Attach %s to %s" % (str(tag_id), str(vm_id)))

    # credentials reused from target
    kwargs.update(ctx.target.instance.runtime_properties)
    client_session = common.nsx_login(kwargs)

    resource_id = nsx_security_tag.add_tag_vm(
        client_session,
        tag_id,
        vm_id,
    )
    ctx.logger.info("created %s" % resource_id)


@operation
def unlink(**kwargs):
    vm_id = ctx.source.instance.runtime_properties.get('vsphere_server_id')
    tag_id = ctx.target.instance.runtime_properties.get('resource_id')
    ctx.logger.info("Deattach %s from %s" % (str(tag_id), str(vm_id)))

    # credentials reused from target
    kwargs.update(ctx.target.instance.runtime_properties)
    client_session = common.nsx_login(kwargs)

    resource_id = nsx_security_tag.tag_vm_to_resource_id(tag_id, vm_id)

    nsx_security_tag.delete_tag_vm(
        client_session,
        resource_id
    )
    ctx.logger.info("delete %s" % resource_id)
