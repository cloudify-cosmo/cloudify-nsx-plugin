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
import cfy_nsx_common as common
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    # credentials
    vccontent = common.vcenter_state(kwargs)

    use_existed, dvportgroup = common.get_properties('dvportgroup', kwargs)

    if not use_existed:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented"
        )

    if 'name' in dvportgroup:
        resource_name = dvportgroup['name']
        resource_id = nsx_utils.get_vdsportgroupid(
            vccontent, dvportgroup['name']
        )
    elif 'id' in dvportgroup:
        resource_id = dvportgroup['id']
        resource_name = common.get_vdsportgroupname(
            vccontent, dvportgroup['id']
        )
    else:
        raise cfy_exc.NonRecoverableError(
            "Validation failed, please provice id or name"
        )

    _, update_to = common.get_properties('update_to', kwargs)
    if update_to:
        if 'name' in update_to:
            common.rename_vdsportgroupname(vccontent, resource_id,
                                           update_to['name'])
            resource_name = update_to['name']

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.instance.runtime_properties['resource_name'] = resource_name

    ctx.logger.info("created %s | %s" % (resource_id, resource_name))


@operation
def delete(**kwargs):
    use_existed, _ = common.get_properties('dvportgroup', kwargs)

    if not use_existed:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented!"
        )
