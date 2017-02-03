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
import cloudify_nsx.library.nsx_esg_dlr as cfy_dlr
import cloudify_nsx.library.nsx_common as common


@operation
def create(**kwargs):
    validation_rules = {
        "dlr_id": {
            "required": True
        },
        "address": {
            "required": True
        }
    }

    use_existing, gateway = common.get_properties_and_validate(
        'gateway', kwargs, validation_rules
    )

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    result_raw = nsx_router.dlr_set_dgw(client_session,
                                        gateway['dlr_id'],
                                        gateway['address'])

    common.check_raw_result(result_raw)

    ctx.instance.runtime_properties['resource_id'] = gateway['dlr_id']
    ctx.logger.info("created %s" % gateway['dlr_id'])


@operation
def delete(**kwargs):
    use_existing, gateway = common.get_properties('gateway', kwargs)

    if use_existing:
        common.remove_properties('gateway')
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        common.remove_properties('gateway')
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    common.attempt_with_rerun(
        cfy_dlr.dlr_del_dgw,
        client_session=client_session,
        resource_id=resource_id
    )

    ctx.logger.info("delete %s" % resource_id)

    common.remove_properties('gateway')
