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
import pynsxv.library.libutils as nsx_utils
from cfy_nsx_common import vcenter_state, get_vdsportgroupname
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    # credentials
    properties = ctx.node.properties
    vcenter_auth = properties.get('vcenter_auth', {})
    vcenter_auth.update(kwargs.get('vcenter_auth', {}))
    vccontent = vcenter_state(vcenter_auth)

    dvportgroup = properties.get('dvportgroup', {})
    dvportgroup.update(kwargs.get('dvportgroup', {}))
    use_existed = dvportgroup.get('use_external_resource', False)
    if not use_existed:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented"
        )
    if 'name' in dvportgroup:
        ctx.instance.runtime_properties['resource_name'] = str(dvportgroup['name'])
        ctx.instance.runtime_properties['resource_id'] = nsx_utils.get_vdsportgroupid(
            vccontent, str(dvportgroup['name'])
        )
    elif 'id' in dvportgroup:
        ctx.instance.runtime_properties['resource_id'] = dvportgroup['id']
        ctx.instance.runtime_properties['resource_name'] = get_vdsportgroupname(
            vccontent, str(dvportgroup['id'])
        )
    else:
        raise cfy_exc.NonRecoverableError(
            "Validation failed, please provice id or name"
        )

    ctx.logger.info("created %s | %s" % (
        ctx.instance.runtime_properties['resource_id'],
        ctx.instance.runtime_properties['resource_name']
    ))

@operation
def delete(**kwargs):
    # credentials
    properties = ctx.node.properties

    dvportgroup = properties.get('dvportgroup', {})
    dvportgroup.update(kwargs.get('dvportgroup', {}))
    use_existed = dvportgroup.get('use_external_resource', False)
    if not use_existed:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented!"
        )
