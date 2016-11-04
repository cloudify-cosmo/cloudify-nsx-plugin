# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import nsx_common as common


def dlr_add_interface(client_session, dlr_id, interface_ls_id, interface_ip, interface_subnet, name=None):
    """
    This function adds an interface gw to one dlr
    :param dlr_id: dlr uuid
    :param interface_ls_id: new interface logical switch
    :param interface_ip: new interface ip address
    :param interface_subnet: new interface subnet
    """

    # get a template dict for the dlr interface
    dlr_interface_dict = client_session.extract_resource_body_example('interfaces', 'create')

    # add default gateway to the created dlr if dgw entered
    interface = dlr_interface_dict['interfaces']['interface']
    interface['addressGroups']['addressGroup']['primaryAddress'] = interface_ip
    interface['addressGroups']['addressGroup']['subnetMask'] = interface_subnet
    interface['isConnected'] = "True"
    interface['connectedToId'] = interface_ls_id
    interface['name'] = name

    dlr_interface = client_session.create('interfaces', uri_parameters={'edgeId': dlr_id},
                                          query_parameters_dict={'action': "patch"},
                                          request_body_dict=dlr_interface_dict)
    common.check_raw_result(dlr_interface)
    return dlr_interface

def esg_fw_default_set(client_session, esg_id, def_action, logging_enabled=None):
    """
    This function sets the default firewall rule to accept or deny
    :param client_session: An instance of an NsxClient Session
    :param esg_id: dlr uuid
    :param def_action: Default firewall action, values are either accept or deny
    :param logging_enabled: (Optional) Is logging enabled by default (true/false)
    :return: True on success, False on failure
    """
    if not logging_enabled:
        logging_enabled = 'false'

    def_policy_body = client_session.extract_resource_body_example('defaultFirewallPolicy', 'update')
    def_policy_body['firewallDefaultPolicy']['action'] = def_action
    def_policy_body['firewallDefaultPolicy']['loggingEnabled'] = logging_enabled

    cfg_result = client_session.update('defaultFirewallPolicy', uri_parameters={'edgeId': esg_id},
                                  request_body_dict=def_policy_body)

    if cfg_result['status'] == 204:
        return True
    else:
        return False
