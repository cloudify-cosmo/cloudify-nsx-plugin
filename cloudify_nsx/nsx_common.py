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

def vcenter_state(vcenter_auth):
    user = vcenter_auth.get('user')
    password = vcenter_auth.get('password')
    ip = vcenter_auth.get('ip')
    return nsx_utils.connect_to_vc(ip, user, password)

def nsx_login(nsx_auth):
    user = nsx_auth.get('user')
    password = nsx_auth.get('password')
    ip = nsx_auth.get('ip')
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

    return NsxClient(raml_file, ip, user, password)
