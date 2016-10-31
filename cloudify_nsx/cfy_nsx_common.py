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
from nsxramlclient.client import NsxClient
import pynsxv.library.libutils as nsx_utils
from cloudify import exceptions as cfy_exc
import time
from pyVmomi import vim


def __get_properties(name, kwargs):
    properties_dict = ctx.instance.runtime_properties.get(name, {})
    properties_dict.update(ctx.node.properties.get(name, {}))
    properties_dict.update(kwargs.get(name, {}))
    for key in properties_dict:
        if isinstance(properties_dict[key], (unicode, int)):
            properties_dict[key] = str(properties_dict[key])
    ctx.instance.runtime_properties[name] = properties_dict
    return properties_dict


def vcenter_state(kwargs):
    vcenter_auth = __get_properties('vcenter_auth', kwargs)
    ctx.logger.info("VCenter login...")
    user = vcenter_auth.get('username')
    password = vcenter_auth.get('password')
    ip = vcenter_auth.get('host')
    state = nsx_utils.connect_to_vc(ip, user, password)
    ctx.logger.info("VCenter logined")
    return state


def nsx_login(kwargs):
    nsx_auth = __get_properties('nsx_auth', kwargs)
    ctx.logger.info("NSX login...")
    user = nsx_auth.get('username')
    password = nsx_auth.get('password')
    ip = nsx_auth.get('host')
    # if node contained in some other node, try to overwrite ip
    if not ip:
        ip = ctx.instance.host_ip
        ctx.logger.info("Used host from container: %s" % ip)
    # check minimal amout of credentials
    if not ip or not user or not password:
        raise cfy_exc.NonRecoverableError(
            "please check your credentials"
        )

    raml_file = nsx_auth.get('raml')
    if not raml_file:
        raise cfy_exc.NonRecoverableError(
            "please set raml file path"
        )

    client = NsxClient(raml_file, ip, user, password)
    ctx.logger.info("NSX logined")
    return client


def get_properties(name, kwargs):

    properties_dict = __get_properties(name, kwargs)
    use_existed = properties_dict.get('use_external_resource', False)
    return use_existed, properties_dict


def get_mo_by_id(content, searchedid, vim_type):
    mo_dict = nsx_utils.get_all_objs(content, vim_type)
    for obj in mo_dict:
        if obj._moId == searchedid:
            return obj
    return None


def get_vdsportgroupname(content, searchedid):
    portgroup_mo = get_mo_by_id(content, searchedid,
                                nsx_utils.VIM_TYPES['dportgroup'])
    if portgroup_mo:
        return str(portgroup_mo.name)
    else:
        return None


def _wait_for_task(task):
    while task.info.state == vim.TaskInfo.State.running:
        time.sleep(30)
    ctx.logger.info("Waiting...")
    if task.info.state != vim.TaskInfo.State.success:
        raise cfy_exc.NonRecoverableError(
            "Error during executing task on vSphere: '{0}'"
            .format(task.info.error))


def rename_vdsportgroupname(content, searchedid, new_name):
    portgroup_mo = get_mo_by_id(content, searchedid,
                                nsx_utils.VIM_TYPES['dportgroup'])
    if not portgroup_mo:
        return False
    task = portgroup_mo.Rename(new_name)
    _wait_for_task(task)
