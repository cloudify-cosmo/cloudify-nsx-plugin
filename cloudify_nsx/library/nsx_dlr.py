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


def dlr_add_interface(client_session, dlr_id, interface_ls_id, interface_ip,
                      interface_subnet, name=None):
    """
    This function adds an interface gw to one dlr
    :param dlr_id: dlr uuid
    :param interface_ls_id: new interface logical switch
    :param interface_ip: new interface ip address
    :param interface_subnet: new interface subnet
    """

    # get a template dict for the dlr interface
    dlr_interface_dict = client_session.extract_resource_body_example(
        'interfaces', 'create'
    )

    # add default gateway to the created dlr if dgw entered
    interface = dlr_interface_dict['interfaces']['interface']
    interface['addressGroups']['addressGroup']['primaryAddress'] = interface_ip
    interface['addressGroups']['addressGroup']['subnetMask'] = interface_subnet
    interface['isConnected'] = "True"
    interface['connectedToId'] = interface_ls_id
    interface['name'] = name

    dlr_interface = client_session.create(
        'interfaces', uri_parameters={'edgeId': dlr_id},
        query_parameters_dict={'action': "patch"},
        request_body_dict=dlr_interface_dict
    )
    common.check_raw_result(dlr_interface)
    return dlr_interface


def esg_fw_default_set(client_session, esg_id, def_action,
                       logging_enabled=None):
    """
    This function sets the default firewall rule to accept or deny
    :param client_session: An instance of an NsxClient Session
    :param esg_id: dlr uuid
    :param def_action: Default firewall action, values are either
        accept or deny
    :param logging_enabled: (Optional) Is logging enabled by default
        (true/false)
    :return: True on success, False on failure
    """
    if not logging_enabled:
        logging_enabled = 'false'

    def_policy_body = client_session.extract_resource_body_example(
        'defaultFirewallPolicy', 'update'
    )
    firewall_default_policy = def_policy_body['firewallDefaultPolicy']
    firewall_default_policy['action'] = def_action
    firewall_default_policy['loggingEnabled'] = logging_enabled

    cfg_result = client_session.update('defaultFirewallPolicy',
                                       uri_parameters={'edgeId': esg_id},
                                       request_body_dict=def_policy_body)

    if cfg_result['status'] == 204:
        return True
    else:
        return False


def dhcp_server(client_session, esg_id, enabled=None, syslog_enabled=None,
                syslog_level=None):
    """
    This function enables/disables the DHCP server on an Edge Gateway
    and sets the logging status and Level

    :type client_session: nsxramlclient.client.NsxClient
    :param client_session: A nsxramlclient session Object
    :type esg_id: str
    :param esg_id: dlr uuid
    :type enabled: bool
    :param enabled: True/False The desired state of the DHCP Server
    :type syslog_enabled: str
    :param syslog_enabled: ('true'/'false') The desired logging state of
      the DHCP Server
    :type syslog_level: str
    :param syslog_level: The logging level for DHCP on this Edge
      (INFO/WARNING/etc.)
    :param relay: dhcp relay settings for dlr
    :rtype: bool
    :return: Return True on success of the operation
    """
    change_needed = False

    current_dhcp_config = client_session.read(
        'dhcp', uri_parameters={'edgeId': esg_id})['body']

    new_dhcp_config = current_dhcp_config

    if enabled:
        if current_dhcp_config['dhcp']['enabled'] == 'false':
            new_dhcp_config['dhcp']['enabled'] = 'true'
            change_needed = True
    else:
        if current_dhcp_config['dhcp']['enabled'] == 'true':
            new_dhcp_config['dhcp']['enabled'] = 'false'
            change_needed = True

    if syslog_enabled == 'true':
        if current_dhcp_config['dhcp']['logging']['enable'] == 'false':
            new_dhcp_config['dhcp']['logging']['enable'] = 'true'
            change_needed = True
    elif syslog_enabled == 'false':
        if current_dhcp_config['dhcp']['logging']['enable'] == 'true':
            new_dhcp_config['dhcp']['logging']['enable'] = 'false'
            change_needed = True

    if syslog_level:
        if current_dhcp_config['dhcp']['logging']['logLevel'] != syslog_level:
            new_dhcp_config['dhcp']['logging']['logLevel'] = syslog_level
            change_needed = True

    if not change_needed:
        return True
    else:
        result = client_session.update('dhcp',
                                       uri_parameters={'edgeId': esg_id},
                                       request_body_dict=new_dhcp_config)
        if result['status'] == 204:
            return True
        else:
            return False


def update_dhcp_relay(client_session, esg_id, relayServer=None,
                      relayAgents=None):
    current_relay_config = client_session.extract_resource_body_example(
        'dhcpRelay', 'update'
    )

    if relayServer:
        current_relay_config['relay']['relayServer'] = relayServer
    if relayAgents:
        current_relay_config['relay']['relayAgents'] = relayAgents

    raw_result = client_session.update(
        'dhcpRelay', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=current_relay_config
    )

    common.check_raw_result(raw_result)


def routing_global_config(client_session, esg_id, enabled,
                          routingGlobalConfig=None, staticRouting=None):

    routing = {
        'routing': {}
    }

    if enabled:
        routing['routing']['enabled'] = "true"
    else:
        routing['routing']['enabled'] = "true"

    if routingGlobalConfig:
        routing['routing']['routingGlobalConfig'] = routingGlobalConfig

    if staticRouting:
        routing['routing']['staticRouting'] = staticRouting

    raw_result = client_session.update(
        'routingConfig', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=routing
    )

    common.check_raw_result(raw_result)


def ospf_create(client_session, esg_id, enabled, defaultOriginate,
                gracefulRestart, redistribution, protocolAddress,
                forwardingAddress):
    current_ospf = {
        'ospf': {
            'redistribution': {
            }
        }
    }

    if enabled:
        current_ospf['ospf']['enabled'] = 'true'
    else:
        current_ospf['ospf']['enabled'] = 'false'

    if defaultOriginate:
        current_ospf['ospf']['defaultOriginate'] = 'true'
    else:
        current_ospf['ospf']['defaultOriginate'] = 'false'

    if gracefulRestart:
        current_ospf['ospf']['gracefulRestart'] = 'true'
    else:
        current_ospf['ospf']['gracefulRestart'] = 'false'

    if redistribution:
        current_ospf['ospf']['redistribution']['enabled'] = 'true'
    else:
        current_ospf['ospf']['redistribution']['enabled'] = 'false'

    if protocolAddress:
        current_ospf['ospf']['protocolAddress'] = protocolAddress

    if forwardingAddress:
        current_ospf['ospf']['forwardingAddress'] = forwardingAddress

    raw_result = client_session.update(
        'routingOSPF', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=current_ospf
    )

    common.check_raw_result(raw_result)
