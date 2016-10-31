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
from cfy_nsx_common import vcenter_state, get_properties
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    # credentials
    vccontent = vcenter_state(kwargs)

    use_existed, datacenter = get_properties('datacenter', kwargs)

    if not use_existed:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented"
        )

    resource_id = nsx_utils.get_datacentermoid(
        vccontent, datacenter['name']
    )
    ctx.instance.runtime_properties['resource_id'] = resource_id


@operation
def delete(**kwargs):
    use_existed, _ = get_properties('datacenter', kwargs)

    if not use_existed:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented"
        )
