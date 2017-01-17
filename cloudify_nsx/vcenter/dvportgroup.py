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
import cloudify_nsx.library.nsx_common as common
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):

    validation_rules = {
        # we need name in any case of usage except predefined 'id'
        'name': {
            'required': True
        }
    }

    use_existing, dvportgroup = common.get_properties_and_validate(
        'dvportgroup', kwargs, validation_rules
    )

    # credentials
    vccontent = common.vcenter_state(kwargs)

    resource_id = ctx.instance.runtime_properties.get('resource_id')

    if not use_existing:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented"
        )

    if dvportgroup.get('name'):
        resource_name = dvportgroup['name']
        resource_id = nsx_utils.get_vdsportgroupid(
            vccontent, dvportgroup['name']
        )
    elif resource_id:
        resource_name = common.get_vdsportgroupname(
            vccontent, resource_id
        )
    else:
        raise cfy_exc.NonRecoverableError(
            "Validation failed, please provide id or name"
        )

    if not resource_id:
        raise cfy_exc.RecoverableError(
            message="We dont have such network yet", retry_after=10
        )

    _, update_to = common.get_properties('update_to', kwargs)
    if update_to:
        if 'name' in update_to and update_to['name']:
            common.rename_vdsportgroupname(vccontent, resource_id,
                                           update_to['name'])
            resource_name = update_to['name']

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.instance.runtime_properties['resource_name'] = resource_name

    ctx.logger.info("created %s | %s" % (resource_id, resource_name))


@operation
def delete(**kwargs):
    use_existing, _ = common.get_properties('dvportgroup', kwargs)

    if not use_existing:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented!"
        )
