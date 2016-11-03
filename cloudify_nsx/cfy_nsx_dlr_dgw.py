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
import pynsxv.library.nsx_dlr as nsx_router
import library.nsx_common as common


@operation
def create(**kwargs):
    # credentials
    client_session = common.nsx_login(kwargs)

    use_existed, gateway = common.get_properties('gateway', kwargs)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    result_raw = nsx_router.dlr_set_dgw(client_session,
                                        gateway['dlr_id'],
                                        gateway['address'])

    common.check_raw_result(result_raw)

    ctx.instance.runtime_properties['resource_dlr_id'] = gateway['dlr_id']
    ctx.instance.runtime_properties['resource_id'] = gateway['address']
    ctx.logger.info("created %s" % gateway['address'])


@operation
def delete(**kwargs):
    # credentials
    client_session = common.nsx_login(kwargs)

    use_existed, gateway = common.get_properties('gateway', kwargs)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    if 'resource_id' not in ctx.instance.runtime_properties:
        ctx.logger.info("Not fully created, skip")
        return

    result_raw = nsx_router.dlr_del_dgw(
        client_session,
        ctx.instance.runtime_properties['resource_dlr_id']
    )

    common.check_raw_result(result_raw)

    ctx.logger.info(
        "delete %s" % ctx.instance.runtime_properties['resource_id'])
    ctx.instance.runtime_properties['resource_id'] = None
