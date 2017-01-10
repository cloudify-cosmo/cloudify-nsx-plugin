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
import library.nsx_common as common
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    use_existing, datacenter = common.get_properties_and_validate(
        'datacenter', kwargs
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    if not use_existing:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented"
        )

    # credentials
    vccontent = common.vcenter_state(kwargs)

    resource_id = nsx_utils.get_datacentermoid(
        vccontent, datacenter['name']
    )

    ctx.logger.info("Found %s" % resource_id)
    ctx.instance.runtime_properties['resource_id'] = resource_id


@operation
def delete(**kwargs):
    use_existing, _ = common.get_properties('datacenter', kwargs)

    if not use_existing:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented"
        )
