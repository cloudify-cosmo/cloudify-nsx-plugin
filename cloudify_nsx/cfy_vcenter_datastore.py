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
from cfy_nsx_common import vcenter_state
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    # credentials
    properties = ctx.node.properties
    vcenter_auth = properties.get('vcenter_auth', {})
    vcenter_auth.update(kwargs.get('vcenter_auth', {}))
    vccontent = vcenter_state(vcenter_auth)

    datastore = properties.get('datastore', {})
    datastore.update(kwargs.get('datastore', {}))
    use_existed = datastore.get('use_external_resource', False)
    if not use_existed:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented"
        )
    ctx.instance.runtime_properties['resource_id'] = nsx_utils.get_datastoremoid(
        vccontent, str(datastore['name'])
    )


@operation
def delete(**kwargs):
    # credentials
    properties = ctx.node.properties

    datastore = properties.get('datastore', {})
    datastore.update(kwargs.get('datastore', {}))
    use_existed = datastore.get('use_external_resource', False)
    if not use_existed:
        raise cfy_exc.NonRecoverableError(
            "Not Implemented!"
        )