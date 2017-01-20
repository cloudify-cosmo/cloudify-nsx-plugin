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
import nsx_nat as nsx_nat
from cloudify import exceptions as cfy_exc


def dlr_add_interface(client_session, dlr_id, interface_ls_id, interface_ip,
                      interface_subnet, name=None, vnic=None):
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
    interface['index'] = vnic

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


def get_uplink_vnic(client_session, esg_id, uplink_ls_id):
    """Search uplink vnic"""
    raw_result = client_session.read(
        'interfaces', uri_parameters={'edgeId': esg_id}
    )
    common.check_raw_result(raw_result)

    interfaces_struct = raw_result['body']

    interfaces = interfaces_struct.get('interfaces', {}).get('interface')
    if not interfaces:
        raise cfy_exc.RecoverableError(
            "No interfaces"
        )
    if isinstance(interfaces, dict):
        interfaces = [interfaces]

    for interface in interfaces:
        if interface.get('type') != 'uplink':
            continue
        if interface.get('connectedToId') != uplink_ls_id:
            continue

        return interface.get('index')

    raise cfy_exc.RecoverableError(
        "No uplink interfaces"
    )


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

    raw_result = client_session.read(
        'dhcp', uri_parameters={'edgeId': esg_id})

    common.check_raw_result(raw_result)

    current_dhcp_config = raw_result['body']

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


def update_bgp(client_session, esg_id, enabled, defaultOriginate,
               gracefulRestart, redistribution, localAS):

    raw_result = client_session.read(
        'routingBGP', uri_parameters={'edgeId': esg_id})

    common.check_raw_result(raw_result)

    current_bgp = raw_result['body']

    if not current_bgp:
        # for fully "disabled" case
        current_bgp = {
            'bgp': {}
        }

    if not current_bgp['bgp'].get('redistribution'):
        current_bgp['bgp']['redistribution'] = {}

    if enabled:
        current_bgp['bgp']['enabled'] = 'true'
    else:
        current_bgp['bgp']['enabled'] = 'false'

    if defaultOriginate:
        current_bgp['bgp']['defaultOriginate'] = 'true'
    else:
        current_bgp['bgp']['defaultOriginate'] = 'false'

    if gracefulRestart:
        current_bgp['bgp']['gracefulRestart'] = 'true'
    else:
        current_bgp['bgp']['gracefulRestart'] = 'false'

    if redistribution:
        current_bgp['bgp']['redistribution']['enabled'] = 'true'
    else:
        current_bgp['bgp']['redistribution']['enabled'] = 'false'

    if localAS:
        current_bgp['bgp']['localAS'] = localAS

    raw_result = client_session.update(
        'routingBGP', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=current_bgp
    )

    common.check_raw_result(raw_result)


def add_bgp_neighbour(client_session, esg_id, use_existing, ipAddress,
                      remoteAS, weight, holdDownTimer, keepAliveTimer,
                      password, protocolAddress, forwardingAddress):
    raw_result = client_session.read(
        'routingBGP', uri_parameters={'edgeId': esg_id})

    common.check_raw_result(raw_result)

    current_bgp = raw_result['body']

    if not current_bgp:
        # for fully "disabled" case
        current_bgp = {
            'bgp': {}
        }

    if not current_bgp['bgp'].get('bgpNeighbours'):
        current_bgp['bgp']['bgpNeighbours'] = {}
    if not current_bgp['bgp']['bgpNeighbours'].get('bgpNeighbour'):
        current_bgp['bgp']['bgpNeighbours']['bgpNeighbour'] = []

    bgp_neighbours = current_bgp['bgp']['bgpNeighbours']['bgpNeighbour']

    # case when we have only one element
    if isinstance(bgp_neighbours, dict):
        current_bgp['bgp']['bgpNeighbours']['bgpNeighbour'] = [bgp_neighbours]
        bgp_neighbours = current_bgp['bgp']['bgpNeighbours']['bgpNeighbour']

    need_add = True

    for bgp_neighbour in bgp_neighbours:
        if bgp_neighbour['ipAddress'] != ipAddress:
            continue

        if str(bgp_neighbour['remoteAS']) != str(remoteAS):
            continue

        if forwardingAddress:
            if bgp_neighbour['forwardingAddress'] != forwardingAddress:
                continue

        if protocolAddress:
            if bgp_neighbour['protocolAddress'] != protocolAddress:
                continue

        if not use_existing:
            raise cfy_exc.NonRecoverableError(
                "You already have such rule"
            )
        else:
            bgp_neighbour['weight'] = weight
            bgp_neighbour['holdDownTimer'] = holdDownTimer
            bgp_neighbour['keepAliveTimer'] = keepAliveTimer
            bgp_neighbour['password'] = password
            if protocolAddress:
                bgp_neighbour['protocolAddress'] = protocolAddress
            if forwardingAddress:
                bgp_neighbour['forwardingAddress'] = forwardingAddress
            need_add = False
            break

    if need_add:
        if use_existing:
            raise cfy_exc.NonRecoverableError(
                "You don't have such rule"
            )
        else:
            bgp_neighbour = {
                'ipAddress': ipAddress,
                'remoteAS': remoteAS,
                'weight': weight,
                'holdDownTimer': holdDownTimer,
                'keepAliveTimer': keepAliveTimer,
                'password': password
            }
            if protocolAddress:
                bgp_neighbour['protocolAddress'] = protocolAddress
            if forwardingAddress:
                bgp_neighbour['forwardingAddress'] = forwardingAddress
            bgp_neighbours.append(bgp_neighbour)

    raw_result = client_session.update(
        'routingBGP', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=current_bgp
    )

    common.check_raw_result(raw_result)

    return "%s|%s|%s|%s|%s" % (
        esg_id, ipAddress, remoteAS,
        protocolAddress if protocolAddress else "",
        forwardingAddress if forwardingAddress else ""
    )


def del_bgp_neighbour(client_session, neighbour_id):

    ids = neighbour_id.split("|")

    esg_id, ipAddress, remoteAS, protocolAddress, forwardingAddress = ids

    raw_result = client_session.read(
        'routingBGP', uri_parameters={'edgeId': esg_id})

    common.check_raw_result(raw_result)

    current_bgp = raw_result['body']

    if not current_bgp:
        raise cfy_exc.NonRecoverableError(
            "You don't have such rule"
        )

    if not current_bgp['bgp'].get('bgpNeighbours'):
        return
    if not current_bgp['bgp']['bgpNeighbours'].get('bgpNeighbour'):
        return

    bgp_neighbours = current_bgp['bgp']['bgpNeighbours']['bgpNeighbour']

    # case when we have only one element
    if isinstance(bgp_neighbours, dict):
        current_bgp['bgp']['bgpNeighbours']['bgpNeighbour'] = [bgp_neighbours]
        bgp_neighbours = current_bgp['bgp']['bgpNeighbours']['bgpNeighbour']

    for bgp_neighbour in bgp_neighbours:
        if bgp_neighbour['ipAddress'] != ipAddress:
            continue

        if str(bgp_neighbour['remoteAS']) != str(remoteAS):
            continue

        if forwardingAddress:
            if bgp_neighbour['forwardingAddress'] != forwardingAddress:
                continue

        if protocolAddress:
            if bgp_neighbour['protocolAddress'] != protocolAddress:
                continue

        bgp_neighbours.remove(bgp_neighbour)
        break

    raw_result = client_session.update(
        'routingBGP', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=current_bgp
    )

    common.check_raw_result(raw_result)


def add_bgp_neighbour_filter(client_session, use_existing, neighbour_id,
                             action, ipPrefixGe, ipPrefixLe, direction,
                             network):
    ids = neighbour_id.split("|")

    esg_id, ipAddress, remoteAS, protocolAddress, forwardingAddress = ids

    raw_result = client_session.read(
        'routingBGP', uri_parameters={'edgeId': esg_id})

    common.check_raw_result(raw_result)

    current_bgp = raw_result['body']

    if not current_bgp:
        # for fully "disabled" case
        current_bgp = {
            'bgp': {}
        }

    if not current_bgp['bgp'].get('bgpNeighbours'):
        current_bgp['bgp']['bgpNeighbours'] = {}
    if not current_bgp['bgp']['bgpNeighbours'].get('bgpNeighbour'):
        current_bgp['bgp']['bgpNeighbours']['bgpNeighbour'] = []

    bgp_neighbours = current_bgp['bgp']['bgpNeighbours']['bgpNeighbour']

    # case when we have only one element
    if isinstance(bgp_neighbours, dict):
        current_bgp['bgp']['bgpNeighbours']['bgpNeighbour'] = [bgp_neighbours]
        bgp_neighbours = current_bgp['bgp']['bgpNeighbours']['bgpNeighbour']

    bgp_neighbour_rule = False

    for bgp_neighbour in bgp_neighbours:
        if bgp_neighbour['ipAddress'] != ipAddress:
            continue

        if str(bgp_neighbour['remoteAS']) != str(remoteAS):
            continue

        if forwardingAddress:
            if bgp_neighbour['forwardingAddress'] != forwardingAddress:
                continue

        if protocolAddress:
            if bgp_neighbour['protocolAddress'] != protocolAddress:
                continue

        bgp_neighbour_rule = bgp_neighbour

    if not bgp_neighbour_rule:
        raise cfy_exc.NonRecoverableError(
            "You don't have such rule"
        )

    if not bgp_neighbour_rule.get('bgp_neighbour_rule'):
        bgp_neighbour_rule['bgpFilters'] = {}
    if not bgp_neighbour_rule['bgpFilters'].get('bgpFilter'):
        bgp_neighbour_rule['bgpFilters']['bgpFilter'] = []

    bgp_filters = bgp_neighbour_rule['bgpFilters']['bgpFilter']
    if isinstance(bgp_filters, dict):
        bgp_neighbour_rule['bgpFilters']['bgpFilter'] = [bgp_filters]
        bgp_filters = bgp_neighbour_rule['bgpFilters']['bgpFilter']

    need_add = True

    for bgp_filter in bgp_filters:
        if str(bgp_filter['network']) != network:
            continue
        if not use_existing:
            raise cfy_exc.NonRecoverableError(
                "You already have such filter(same network)"
            )
        else:
            bgp_filter['action'] = action
            bgp_filter['ipPrefixGe'] = ipPrefixGe
            bgp_filter['ipPrefixLe'] = ipPrefixLe
            bgp_filter['direction'] = direction
            need_add = False
            break

    if need_add:
        if use_existing:
            raise cfy_exc.NonRecoverableError(
                "You don't have such rule"
            )
        else:
            bgp_filter = {
                'network': network,
                'action': action,
                'ipPrefixGe': ipPrefixGe,
                'ipPrefixLe': ipPrefixLe,
                'direction': direction
            }
            bgp_filters.append(bgp_filter)

    raw_result = client_session.update(
        'routingBGP', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=current_bgp
    )

    common.check_raw_result(raw_result)

    return str(network) + "|" + neighbour_id


def del_bgp_neighbour_filter(client_session, resource_id):
    ids = resource_id.split("|")

    network = ids[0]
    esg_id = ids[1]
    ipAddress = ids[2]
    remoteAS = ids[3]
    protocolAddress = ids[4]
    forwardingAddress = ids[5]

    raw_result = client_session.read(
        'routingBGP', uri_parameters={'edgeId': esg_id})

    common.check_raw_result(raw_result)

    current_bgp = raw_result['body']

    if not current_bgp:
        return

    if not current_bgp['bgp'].get('bgpNeighbours'):
        return
    if not current_bgp['bgp']['bgpNeighbours'].get('bgpNeighbour'):
        return

    bgp_neighbours = current_bgp['bgp']['bgpNeighbours']['bgpNeighbour']

    # case when we have only one element
    if isinstance(bgp_neighbours, dict):
        current_bgp['bgp']['bgpNeighbours']['bgpNeighbour'] = [bgp_neighbours]
        bgp_neighbours = current_bgp['bgp']['bgpNeighbours']['bgpNeighbour']

    bgp_neighbour_rule = False

    for bgp_neighbour in bgp_neighbours:
        if bgp_neighbour['ipAddress'] != ipAddress:
            continue

        if str(bgp_neighbour['remoteAS']) != str(remoteAS):
            continue

        if forwardingAddress:
            if bgp_neighbour['forwardingAddress'] != forwardingAddress:
                continue

        if protocolAddress:
            if bgp_neighbour['protocolAddress'] != protocolAddress:
                continue

        bgp_neighbour_rule = bgp_neighbour

    if not bgp_neighbour_rule:
        return

    if not bgp_neighbour_rule.get('bgp_neighbour_rule'):
        return
    if not bgp_neighbour_rule['bgpFilters'].get('bgpFilter'):
        return

    bgp_filters = bgp_neighbour_rule['bgpFilters']['bgpFilter']
    if isinstance(bgp_filters, dict):
        bgp_neighbour_rule['bgpFilters']['bgpFilter'] = [bgp_filters]
        bgp_filters = bgp_neighbour_rule['bgpFilters']['bgpFilter']

    for bgp_filter in bgp_filters:
        if str(bgp_filter['network']) != network:
            continue
        bgp_filters.remove(bgp_filter)
        break

    raw_result = client_session.update(
        'routingBGP', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=current_bgp
    )

    common.check_raw_result(raw_result)


def ospf_create(client_session, esg_id, enabled, defaultOriginate,
                gracefulRestart, redistribution, protocolAddress=None,
                forwardingAddress=None):

    raw_result = client_session.read(
        'routingOSPF', uri_parameters={'edgeId': esg_id})

    common.check_raw_result(raw_result)

    current_ospf = raw_result['body']

    if not current_ospf:
        # for fully "disabled" case
        current_ospf = {
            'ospf': {}
        }

    if not current_ospf['ospf'].get('redistribution'):
        current_ospf['ospf']['redistribution'] = {}

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


def add_esg_ospf_area(client_session, esg_id, area_id, use_existing, area_type,
                      auth):
    raw_result = client_session.read(
        'routingOSPF', uri_parameters={'edgeId': esg_id})

    common.check_raw_result(raw_result)

    ospf = raw_result['body']

    if not ospf['ospf'].get('ospfAreas'):
        ospf['ospf']['ospfAreas'] = {}
    if not ospf['ospf']['ospfAreas'].get('ospfArea'):
        ospf['ospf']['ospfAreas']['ospfArea'] = []

    ospf_areas = ospf['ospf']['ospfAreas']['ospfArea']

    # case when we have only one element
    if isinstance(ospf_areas, dict):
        ospf['ospf']['ospfAreas']['ospfArea'] = [ospf_areas]
        ospf_areas = ospf['ospf']['ospfAreas']['ospfArea']

    need_add = True

    for area in ospf_areas:
        if str(area['areaId']) != str(area_id):
            continue
        if not use_existing:
            raise cfy_exc.NonRecoverableError(
                "You already have such rule"
            )
        else:
            area['type'] = area_type
            area['authentication'] = auth
            need_add = False
            break

    if need_add:
        if use_existing:
            raise cfy_exc.NonRecoverableError(
                "You don't have such rule"
            )
        else:
            ospf_areas.append({
                'areaId': area_id,
                'type': area_type,
                'authentication': auth})

    raw_result = client_session.update(
        'routingOSPF', uri_parameters={'edgeId': esg_id},
        request_body_dict=ospf
    )

    common.check_raw_result(raw_result)

    return "%s|%s" % (esg_id, area_id)


def add_esg_ospf_interface(client_session, esg_id, area_id, vnic, use_existing,
                           hello_interval, dead_interval, priority, cost):

    raw_result = client_session.read(
        'routingOSPF', uri_parameters={'edgeId': esg_id})

    common.check_raw_result(raw_result)

    ospf = raw_result['body']

    if not ospf['ospf'].get('ospfInterfaces'):
        ospf['ospf']['ospfInterfaces'] = {}
    if not ospf['ospf']['ospfInterfaces'].get('ospfInterface'):
        ospf['ospf']['ospfInterfaces']['ospfInterface'] = []

    ospf_interfaces = ospf['ospf']['ospfInterfaces']['ospfInterface']

    # case when we have only one element
    if isinstance(ospf_interfaces, dict):
        ospf['ospf']['ospfInterfaces']['ospfInterface'] = [ospf_interfaces]
        ospf_interfaces = ospf['ospf']['ospfInterfaces']['ospfInterface']

    need_add = True

    for interface in ospf_interfaces:
        if str(interface['areaId']) != str(area_id):
            continue

        if str(interface['vnic']) != str(vnic):
            continue

        if not use_existing:
            raise cfy_exc.NonRecoverableError(
                "You already have such rule"
            )
        else:
            interface['helloInterval'] = hello_interval
            interface['deadInterval'] = dead_interval
            interface['priority'] = priority
            interface['cost'] = cost
            need_add = False
            break

    if need_add:
        if use_existing:
            raise cfy_exc.NonRecoverableError(
                "You don't have such rule"
            )
        else:
            ospf_interfaces.append({
                'vnic': vnic,
                'areaId': area_id,
                'helloInterval': hello_interval,
                'deadInterval': dead_interval,
                'priority': priority,
                'cost': cost})

    raw_result = client_session.update(
        'routingOSPF', uri_parameters={'edgeId': esg_id},
        request_body_dict=ospf
    )

    common.check_raw_result(raw_result)

    return "%s|%s|%s" % (esg_id, area_id, vnic)


def del_esg_ospf_area(client_session, resource_id):

    esg_id, area_id = resource_id.split("|")

    raw_result = client_session.read(
        'routingOSPF', uri_parameters={'edgeId': esg_id})

    common.check_raw_result(raw_result)

    ospf = raw_result['body']

    if not ospf['ospf'].get('ospfAreas'):
        return
    if not ospf['ospf']['ospfAreas'].get('ospfArea'):
        return

    ospf_areas = ospf['ospf']['ospfAreas']['ospfArea']

    # case when we have only one element
    if isinstance(ospf_areas, dict):
        ospf['ospf']['ospfAreas']['ospfArea'] = [ospf_areas]
        ospf_areas = ospf['ospf']['ospfAreas']['ospfArea']

    for ospf_area in ospf_areas:
        if str(ospf_area['areaId']) == str(area_id):
            ospf_areas.remove(ospf_area)
            break

    raw_result = client_session.update(
        'routingOSPF', uri_parameters={'edgeId': esg_id},
        request_body_dict=ospf
    )
    common.check_raw_result(raw_result)


def del_esg_ospf_interface(client_session, resource_id):

    esg_id, area_id, vnic = resource_id.split("|")

    raw_result = client_session.read(
        'routingOSPF', uri_parameters={'edgeId': esg_id})

    common.check_raw_result(raw_result)

    ospf = raw_result['body']

    if not ospf['ospf'].get('ospfInterfaces'):
        return
    if not ospf['ospf']['ospfInterfaces'].get('ospfInterface'):
        return

    ospf_interfaces = ospf['ospf']['ospfInterfaces']['ospfInterface']

    # case when we have only one element
    if isinstance(ospf_interfaces, dict):
        ospf['ospf']['ospfInterfaces']['ospfInterface'] = [ospf_interfaces]
        ospf_interfaces = ospf['ospf']['ospfInterfaces']['ospfInterface']

    for ospf_interface in ospf_interfaces:
        if str(ospf_interface['areaId']) != str(area_id):
            continue

        if str(ospf_interface['vnic']) != str(vnic):
            continue

        ospf_interfaces.remove(ospf_interface)
        break

    raw_result = client_session.update(
        'routingOSPF', uri_parameters={'edgeId': esg_id},
        request_body_dict=ospf
    )
    common.check_raw_result(raw_result)


def esg_cfg_interface(client_session, esg_id, ifindex, ipaddr=None,
                      netmask=None, prefixlen=None, name=None, mtu=None,
                      is_connected=None, portgroup_id=None, vnic_type=None,
                      enable_send_redirects=None, enable_proxy_arp=None,
                      secondary_ips=None):
    """
    This function configures vnic interfaces on ESGs
    :param client_session: An instance of an NsxClient Session
    :param esg_id: esg uuid
    :param ifindex: The vnic index, e.g. vnic3 and the index 3
    :param ipaddr: (Optional) The primary IP Address to be configured for
      this interface
    :param netmask: (Optional) The netmask in the x.x.x.x format
    :param prefixlen: (Optional) The prefix length, this takes precedence
      over the netmask
    :param name: (Optional) The name assigned to the vnic
    :param mtu: (Optional) The vnic MTU
    :param is_connected: (Optional) The vnic connection state (true/false)
    :param portgroup_id: (Optional) The portgroup id of logical switch
      id to connenct this vnic to
    :param vnic_type: (Optional) The vnic type (uplink/internal)
    :param enable_send_redirects: (Optional) Whether the interface will
      send icmp redirects (true/false)
    :param enable_proxy_arp: (Optional) Whether the interface will do
      proxy arp (true/false)
    :param secondary_ips: (Optional) A list of additional secondary IP
      addresses in the primary IP's Subnet
    :return: Returns True on successful configuration of the Interface
    """
    vnic_config = client_session.read(
        'vnic', uri_parameters={'index': ifindex, 'edgeId': esg_id}
    )['body']

    if not mtu:
        mtu = 1500
    if not vnic_type:
        vnic_type = 'internal'

    vnic_config['vnic']['mtu'] = mtu
    vnic_config['vnic']['type'] = vnic_type
    if name:
        vnic_config['vnic']['name'] = name
    if portgroup_id:
        vnic_config['vnic']['portgroupId'] = portgroup_id
    if enable_send_redirects:
        vnic_config['vnic']['enableSendRedirects'] = enable_send_redirects
    if enable_proxy_arp:
        vnic_config['vnic']['enableProxyArp'] = enable_proxy_arp
    if is_connected:
        vnic_config['vnic']['isConnected'] = is_connected
    if ipaddr and (netmask or prefixlen):
        address_group = {}
        sec_ips = []
        if netmask:
            address_group['subnetMask'] = netmask
        if prefixlen:
            address_group['subnetPrefixLength'] = str(prefixlen)
        if secondary_ips:
            sec_ips = secondary_ips
        address_group['primaryAddress'] = ipaddr
        address_group['secondaryAddresses'] = {'ipAddress': sec_ips}
        vnic_config['vnic']['addressGroups'] = {'addressGroup': address_group}

    cfg_result = client_session.update(
        'vnic', uri_parameters={'index': ifindex, 'edgeId': esg_id},
        request_body_dict=vnic_config)
    if cfg_result['status'] == 204:
        return True
    else:
        return False


def esg_clear_interface(client_session, esg_id, ifindex):
    """
    This function resets the vnic configuration of an ESG to its default
      state
    :param client_session: An instance of an NsxClient Session
    :param esg_id: esg uuid
    :param ifindex: The vnic index, e.g. vnic3 and the index 3
    :return: Returns True on successful configuration of the Interface
    """
    vnic_config = client_session.read(
        'vnic', uri_parameters={'index': ifindex, 'edgeId': esg_id}
    )['body']

    vnic_config['vnic']['mtu'] = '1500'
    vnic_config['vnic']['type'] = 'internal'
    vnic_config['vnic']['name'] = 'vnic{}'.format(ifindex)
    vnic_config['vnic']['addressGroups'] = None
    vnic_config['vnic']['portgroupId'] = None
    vnic_config['vnic']['portgroupName'] = None
    vnic_config['vnic']['enableProxyArp'] = 'false'
    vnic_config['vnic']['enableSendRedirects'] = 'false'
    vnic_config['vnic']['isConnected'] = 'false'

    cfg_result = client_session.update(
        'vnic', uri_parameters={'index': ifindex, 'edgeId': esg_id},
        request_body_dict=vnic_config)
    if cfg_result['status'] == 204:
        return True
    else:
        return False


def update_common_edges(client_session, resource_id, kwargs, esg_restriction):

    if esg_restriction:
        validation_rules_firewall = {
            "action": {
                "default": "accept"
            },
            "logging": {
                "default": False,
                "type": "boolean"
            }
        }
    else:
        validation_rules_firewall = {
            "action": {
                "default": "accept"
            },
            "logging": {
                "default": False,
                "type": "boolean"
            }
        }

    _, firewall = common.get_properties_and_validate(
        'firewall', kwargs, validation_rules_firewall
    )

    if not esg_fw_default_set(
        client_session,
        resource_id,
        firewall['action'],
        firewall['logging']
    ):
        raise cfy_exc.NonRecoverableError(
            "Can't change firewall rules"
        )

    if esg_restriction:
        validation_rules_dhcp = {
            "enabled": {
                "default": True,
                "type": "boolean"
            },
            "syslog_enabled": {
                "default": False,
                "type": "boolean"
            },
            "syslog_level": {
                "default": "INFO",
                "values": [
                    "EMERGENCY",
                    "ALERT",
                    "CRITICAL",
                    "ERROR",
                    "WARNING",
                    "NOTICE",
                    "INFO",
                    "DEBUG"
                ]
            }
        }
    else:
        validation_rules_dhcp = {
            "enabled": {
                "default": True,
                "type": "boolean"

            },
            "syslog_enabled": {
                "default": False,
                "type": "boolean"
            },
            "syslog_level": {
                "default": "INFO",
                "caseinsensitive": True,
                "values": [
                    "EMERGENCY",
                    "ALERT",
                    "CRITICAL",
                    "ERROR",
                    "WARNING",
                    "NOTICE",
                    "INFO",
                    "DEBUG"
                ]
            }
        }

    _, dhcp = common.get_properties_and_validate(
        'dhcp', kwargs, validation_rules_dhcp
    )

    if not dhcp_server(
        client_session,
        resource_id,
        dhcp['enabled'],
        dhcp['syslog_enabled'],
        dhcp['syslog_level']
    ):
        raise cfy_exc.NonRecoverableError(
            "Can't change dhcp rules"
        )

    if esg_restriction:
        validation_rules_routing = {
            "enabled": {
                "default": True,
                "type": "boolean"
            },
            "staticRouting": {
                "set_none": True,
                "sub": {
                    "defaultRoute": {
                        "set_none": True,
                        "sub": {
                            "gatewayAddress": {
                                "set_none": True
                            },
                            "vnic": {
                                "set_none": True
                            },
                            "mtu": {
                                "set_none": True
                            }
                        }
                    }
                }
            },
            "routingGlobalConfig": {
                "sub": {
                    "routerId": {
                        "set_none": True
                    },
                    "ecmp": {
                        "default": False,
                        "type": "boolean"
                    },
                    "logging": {
                        "sub": {
                            "logLevel": {
                                "default": "INFO",
                                "caseinsensitive": True,
                                "values": [
                                    "EMERGENCY",
                                    "ALERT",
                                    "CRITICAL",
                                    "ERROR",
                                    "WARNING",
                                    "NOTICE",
                                    "INFO",
                                    "DEBUG"
                                ]
                            },
                            "enable": {
                                "default": False,
                                "type": "boolean"
                            }
                        }
                    }
                }
            }
        }
    else:
        validation_rules_routing = {
            "enabled": {
                "default": True,
                "type": "boolean"
            },
            "staticRouting": {
                "set_none": True,
                "sub": {
                    "defaultRoute": {
                        "set_none": True,
                        "sub": {
                            "gatewayAddress": {
                                "set_none": True
                            },
                            "vnic": {
                                "set_none": True
                            },
                            "mtu": {
                                "set_none": True
                            }
                        }
                    }
                }
            },
            "routingGlobalConfig": {
                "sub": {
                    "routerId": {
                        "set_none": True
                    },
                    "ecmp": {
                        "default": False,
                        "type": "boolean"
                    },
                    "logging": {
                        "sub": {
                            "logLevel": {
                                "default": "INFO",
                                "caseinsensitive": True,
                                "values": [
                                    "EMERGENCY",
                                    "ALERT",
                                    "CRITICAL",
                                    "ERROR",
                                    "WARNING",
                                    "NOTICE",
                                    "INFO",
                                    "DEBUG"
                                ]
                            },
                            "enable": {
                                "default": False,
                                "type": "boolean"
                            }
                        }
                    }
                }
            }
        }

    _, routing = common.get_properties_and_validate(
        'routing', kwargs, validation_rules_routing
    )
    routing_global_config(
        client_session, resource_id,
        routing['enabled'], routing['routingGlobalConfig'],
        routing['staticRouting']
    )

    if esg_restriction:
        validation_rules_ospf = {
            "enabled": {
                "default": False,
                "type": "boolean"
            },
            "defaultOriginate": {
                "default": False,
                "type": "boolean"
            },
            "gracefulRestart": {
                "default": False,
                "type": "boolean"
            },
            "redistribution": {
                "default": False,
                "type": "boolean"
            }
        }
    else:
        validation_rules_ospf = {
            "enabled": {
                "default": False,
                "type": "boolean"
            },
            "defaultOriginate": {
                "default": False,
                "type": "boolean"
            },
            "gracefulRestart": {
                "default": False,
                "type": "boolean"
            },
            "redistribution": {
                "default": False,
                "type": "boolean"
            },
            "protocolAddress": {
                "set_none": True
            },
            "forwardingAddress": {
                "set_none": True
            }
        }

    _, ospf = common.get_properties_and_validate(
        'ospf', kwargs, validation_rules_ospf
    )

    if esg_restriction:
        validation_rules_bgp = {
            "enabled": {
                "default": False,
                "type": "boolean"
            },
            "defaultOriginate": {
                "default": False,
                "type": "boolean"
            },
            "gracefulRestart": {
                "default": False,
                "type": "boolean"
            },
            "redistribution": {
                "default": False,
                "type": "boolean"
            },
            "localAS": {
                "type": "string",
                "set_none": True
            }
        }
    else:
        validation_rules_bgp = {
            "enabled": {
                "default": False,
                "type": "boolean"
            },
            "defaultOriginate": {
                "default": False,
                "type": "boolean"
            },
            "gracefulRestart": {
                "default": False,
                "type": "boolean"
            },
            "redistribution": {
                "default": False,
                "type": "boolean"
            },
            "localAS": {
                "type": "string",
                "set_none": True
            }
        }

    _, bgp = common.get_properties_and_validate(
        'bgp', kwargs, validation_rules_bgp
    )

    # disable bgp before change ospf (if need)
    if not bgp['enabled']:
        update_bgp(
            client_session, resource_id,
            bgp['enabled'], bgp['defaultOriginate'],
            bgp['gracefulRestart'], bgp['redistribution'],
            bgp['localAS']
        )

    if esg_restriction:
        ospf_create(
            client_session, resource_id,
            ospf['enabled'], ospf['defaultOriginate'],
            ospf['gracefulRestart'], ospf['redistribution']
        )
    else:
        ospf_create(
            client_session, resource_id,
            ospf['enabled'], ospf['defaultOriginate'],
            ospf['gracefulRestart'], ospf['redistribution'],
            ospf['protocolAddress'], ospf['forwardingAddress']
        )

    # enable bgp after change ospf (if need)
    if bgp['enabled']:
        update_bgp(
            client_session, resource_id,
            bgp['enabled'], bgp['defaultOriginate'],
            bgp['gracefulRestart'], bgp['redistribution'],
            bgp['localAS']
        )

    if esg_restriction:
        validation_rules_nat = {
            "enabled": {
                "default": True,
                "type": "boolean"
            }
        }

        _, nat = common.get_properties_and_validate(
            'nat', kwargs, validation_rules_nat
        )

        if not nsx_nat.nat_service(
            client_session,
            resource_id,
            nat['enabled']
        ):
            raise cfy_exc.NonRecoverableError(
                "Can't change nat rules"
            )


def add_routing_prefix(client_session, use_existing, esg_id, name, ipAddress):

    raw_result = client_session.read(
        'routingConfig', uri_parameters={'edgeId': str(esg_id)})

    common.check_raw_result(raw_result)

    routing = raw_result['body']

    if not routing:
        routing = {
            'routing': {}
        }

    if not routing['routing'].get('routingGlobalConfig'):
        routing['routing']['routingGlobalConfig'] = {}

    if not routing['routing']['routingGlobalConfig'].get('ipPrefixes'):
        routing['routing']['routingGlobalConfig']['ipPrefixes'] = {}

    prefixes_parent = routing['routing']['routingGlobalConfig']['ipPrefixes']

    if not prefixes_parent.get('ipPrefix'):
        prefixes_parent['ipPrefix'] = []

    prefixes = prefixes_parent['ipPrefix']

    if isinstance(prefixes, dict):
        prefixes_parent['ipPrefix'] = [prefixes]
        prefixes = prefixes_parent['ipPrefix']

    need_add = True
    for prefix in prefixes:
        if prefix['name'] != name:
            continue

        if not use_existing:
            raise cfy_exc.NonRecoverableError(
                "You already have such prefix"
            )
        else:
            prefix['ipAddress'] = ipAddress
            need_add = False
            break

    if need_add:
        if use_existing:
            raise cfy_exc.NonRecoverableError(
                "You don't have such prefix"
            )
        else:
            prefix = {
                'name': name,
                'ipAddress': ipAddress
            }
            prefixes.append(prefix)

    raw_result = client_session.update(
        'routingConfig', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=routing
    )

    common.check_raw_result(raw_result)

    return "%s|%s" % (esg_id, name)


def del_routing_prefix(client_session, resource_id):

    esg_id, name = resource_id.split("|")

    raw_result = client_session.read(
        'routingConfig', uri_parameters={'edgeId': str(esg_id)})

    common.check_raw_result(raw_result)

    routing = raw_result['body']

    if not routing:
        return

    if not routing['routing'].get('routingGlobalConfig'):
        return

    if not routing['routing']['routingGlobalConfig'].get('ipPrefixes'):
        return

    prefixes_parent = routing['routing']['routingGlobalConfig']['ipPrefixes']

    if not prefixes_parent.get('ipPrefix'):
        return

    prefixes = prefixes_parent['ipPrefix']

    if isinstance(prefixes, dict):
        prefixes_parent['ipPrefix'] = [prefixes]
        prefixes = prefixes_parent['ipPrefix']

    for prefix in prefixes:
        if prefix['name'] != name:
            continue

        prefixes.remove(prefix)
        break

    raw_result = client_session.update(
        'routingConfig', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=routing
    )

    common.check_raw_result(raw_result)


def add_routing_rule(client_session, use_existing, esg_id, routing_type,
                     prefixName, routing_from, action):

    # convert boolean to 'correct' string values for routing
    for key in routing_from:
        if routing_from[key]:
            routing_from[key] = "true"
        else:
            routing_from[key] = "false"

    raw_result = client_session.read(
        'routingConfig', uri_parameters={'edgeId': str(esg_id)})

    common.check_raw_result(raw_result)

    routing = raw_result['body']

    if not routing:
        routing = {
            'routing': {}
        }

    # search routing type
    if routing_type in routing['routing']:
        routing_sub_dict = routing['routing'][routing_type]

    if not isinstance(routing_sub_dict, dict):
        routing['routing'][routing_type] = routing_sub_dict = {}

    # seach redistribution
    if 'redistribution' in routing_sub_dict:
        redistribution = routing_sub_dict['redistribution']

    if not isinstance(redistribution, dict):
        redistribution = routing_sub_dict['redistribution'] = {}

    # parent rules
    if 'rules' in redistribution:
        redistribution_rules = redistribution['rules']

    if not isinstance(redistribution_rules, dict):
        redistribution['rules'] = redistribution_rules = {}

    # rules dict
    if 'rule' not in redistribution_rules:
        redistribution_rules['rule'] = []

    rules = redistribution_rules['rule']
    if isinstance(rules, dict):
        redistribution_rules['rule'] = [rules]
        rules = redistribution_rules['rule']

    need_add = True

    for rule in rules:
        if rule['prefixName'] != prefixName:
            continue

        if not use_existing:
            raise cfy_exc.NonRecoverableError(
                "You already have such rule"
            )
        else:
            rule['from'] = routing_from
            rule['action'] = action
            need_add = False
            break

    if need_add:
        if use_existing:
            raise cfy_exc.NonRecoverableError(
                "You don't have such rule"
            )
        else:
            rule = {
                'prefixName': prefixName,
                'from': routing_from,
                'action': action
            }
            rules.append(rule)

    raw_result = client_session.update(
        'routingConfig', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=routing
    )

    common.check_raw_result(raw_result)

    return "%s|%s|%s" % (esg_id, routing_type, prefixName)


def del_routing_rule(client_session, resource_id):

    esg_id, routing_type, prefixName = resource_id.split("|")

    raw_result = client_session.read(
        'routingConfig', uri_parameters={'edgeId': str(esg_id)})

    common.check_raw_result(raw_result)

    routing = raw_result['body']

    if not routing:
        return

    # search routing type
    if routing_type in routing['routing']:
        routing_sub_dict = routing['routing'][routing_type]

    if not isinstance(routing_sub_dict, dict):
        routing['routing'][routing_type] = routing_sub_dict = {}

    # seach redistribution
    if 'redistribution' in routing_sub_dict:
        redistribution = routing_sub_dict['redistribution']

    if not isinstance(redistribution, dict):
        redistribution = routing_sub_dict['redistribution'] = {}

    # parent rules
    if 'rules' in redistribution:
        redistribution_rules = redistribution['rules']

    if not isinstance(redistribution_rules, dict):
        redistribution['rules'] = redistribution_rules = {}

    # rules dict
    if 'rule' not in redistribution_rules:
        redistribution_rules['rule'] = []

    rules = redistribution_rules['rule']
    if isinstance(rules, dict):
        redistribution_rules['rule'] = [rules]
        rules = redistribution_rules['rule']

    need_save = False
    for rule in rules:
        if rule['prefixName'] != prefixName:
            continue

        rules.remove(rule)
        need_save = True
        break

    if not need_save:
        return

    raw_result = client_session.update(
        'routingConfig', uri_parameters={'edgeId': str(esg_id)},
        request_body_dict=routing
    )

    common.check_raw_result(raw_result)


def esg_dgw_clear(client_session, esg_id):
    """
    This function clears the default gateway config on an ESG
    :param client_session: An instance of an NsxClient Session
    :param esg_id: The id of the ESG to list interfaces of
    :return: True on success, False on failure
    """

    rtg_cfg = client_session.read(
        'routingConfigStatic', uri_parameters={'edgeId': esg_id}
    )['body']
    rtg_cfg['staticRouting']['defaultRoute'] = None

    cfg_result = client_session.update(
        'routingConfigStatic', uri_parameters={'edgeId': esg_id},
        request_body_dict=rtg_cfg
    )
    if cfg_result['status'] == 204:
        return True
    else:
        return False


def esg_dgw_set(client_session, esg_id, dgw_ip, vnic, mtu=None,
                admin_distance=None):
    """
    This function sets the default gateway on an ESG
    :param client_session: An instance of an NsxClient Session
    :param esg_id: The id of the ESG to list interfaces of
    :param dgw_ip: The default gateway ip (next hop)
    :param vnic: (Optional) The vnic index of were the default gateway
        is reachable on
    :param mtu: (Optional) The MTU of the defautl gateway (default=1500)
    :param admin_distance: (OIptional) Admin distance of the defautl
        route (default=1)
    :return: True on success, False on failure
    """
    if not mtu:
        mtu = '1500'
    if not admin_distance:
        admin_distance = '1'

    rtg_cfg = client_session.read(
        'routingConfigStatic', uri_parameters={'edgeId': esg_id}
    )['body']
    rtg_cfg['staticRouting']['defaultRoute'] = {
        'vnic': vnic, 'gatewayAddress': dgw_ip,
        'adminDistance': admin_distance, 'mtu': mtu
    }

    cfg_result = client_session.update(
        'routingConfigStatic', uri_parameters={'edgeId': esg_id},
        request_body_dict=rtg_cfg
    )
    if cfg_result['status'] == 204:
        return True
    else:
        return False


def esg_route_add(client_session, esg_id, network, next_hop, vnic=None,
                  mtu=None, admin_distance=None, description=None):
    """
    This function adds a static route to an ESG
    :param client_session: An instance of an NsxClient Session
    :param esg_id: The name of the ESG where the route should be added
    :param network: The routes network in the x.x.x.x/yy format,
        e.g. 192.168.1.0/24
    :param next_hop: The next hop ip
    :param vnic: (Optional) The vnic index of were this route is reachable on
    :param mtu: (Optional) The MTU of the route (default=1500)
    :param admin_distance: (Optional) Admin distance of the defautl route
        (default=1)
    :param description: (Optional) A description for this route
    :return: True on success, False on failure
    """
    if not mtu:
        mtu = '1500'
    if not admin_distance:
        admin_distance = '1'

    rtg_cfg = client_session.read(
        'routingConfigStatic', uri_parameters={'edgeId': esg_id}
    )['body']
    if rtg_cfg['staticRouting']['staticRoutes']:
        routes = client_session.normalize_list_return(
            rtg_cfg['staticRouting']['staticRoutes']['route']
        )
    else:
        routes = []

    new_route = {
        'vnic': vnic, 'network': network, 'nextHop': next_hop,
        'adminDistance': admin_distance, 'mtu': mtu,
        'description': description
    }
    routes.append(new_route)
    rtg_cfg['staticRouting']['staticRoutes'] = {'route': routes}

    cfg_result = client_session.update(
        'routingConfigStatic', uri_parameters={'edgeId': esg_id},
        request_body_dict=rtg_cfg
    )

    if cfg_result['status'] == 204:
        return True
    else:
        return False


def esg_route_del(client_session, esg_id, network, next_hop):
    """
    This function deletes a static route to an ESG
    :param client_session: An instance of an NsxClient Session
    :param esg_id: The id of the ESG where the route should be deleted
    :param network: The routes network in the x.x.x.x/yy format,
        e.g. 192.168.1.0/24
    :param next_hop: The next hop ip
    :return: True on success, False on failure
    """

    rtg_cfg = client_session.read(
        'routingConfigStatic', uri_parameters={'edgeId': esg_id}
    )['body']
    if rtg_cfg['staticRouting']['staticRoutes']:
        routes = client_session.normalize_list_return(
            rtg_cfg['staticRouting']['staticRoutes']['route']
        )
    else:
        return False

    routes_filtered = [
        route for route in routes if not (
            route['network'] == network and route['nextHop'] == next_hop
        )
    ]
    if len(routes_filtered) == len(routes):
        return False
    rtg_cfg['staticRouting']['staticRoutes'] = {'route': routes_filtered}

    cfg_result = client_session.update(
        'routingConfigStatic', uri_parameters={'edgeId': esg_id},
        request_body_dict=rtg_cfg
    )
    if cfg_result['status'] == 204:
        return True
    else:
        return False


def add_dhcp_pool(client_session, esg_id, ip_range, default_gateway=None,
                  subnet_mask=None, domain_name=None, dns_server_1=None,
                  dns_server_2=None, lease_time=None, auto_dns=None):
    """
    This function adds a DHCP Pool to an edge DHCP Server

    :type client_session: nsxramlclient.client.NsxClient
    :param client_session: A nsxramlclient session Object
    :type esg_id: str
    :param esg_id: The id of a Edge Service Gateway used for DHCP
    :type ip_range: str
    :param ip_range: An IP range, e.g. 192.168.178.10-192.168.178.100
        for this IP Pool
    :type default_gateway: str
    :param default_gateway: The default gateway for the specified subnet
    :type subnet_mask: str
    :param subnet_mask: The subnet mask (e.g. 255.255.255.0) for the
        specified subnet
    :type domain_name: str
    :param domain_name: The DNS domain name (e.g. vmware.com) for the
        specified subnet
    :type dns_server_1: str
    :param dns_server_1: The primary DNS Server
    :type dns_server_2: str
    :param dns_server_2: The secondary DNS Server
    :type lease_time: str
    :param lease_time: The lease time in seconds, use 'infinite' to
        disable expiry of DHCP leases
    :type auto_dns: str
    :param auto_dns: ('true'/'false') If set to true, the DNS servers
        and domain name set for NSX-Manager will be used
    :rtype: str
    :return: Returns a string containing the pool id of the created
        DHCP Pool
    """

    dhcp_pool_dict = {'ipRange': ip_range,
                      'defaultGateway': default_gateway,
                      'subnetMask': subnet_mask,
                      'domainName': domain_name,
                      'primaryNameServer': dns_server_1,
                      'secondaryNameServer': dns_server_2,
                      'leaseTime': lease_time,
                      'autoConfigureDNS': auto_dns}

    result = client_session.create(
        'dhcpPool', uri_parameters={'edgeId': esg_id},
        request_body_dict={'ipPool': dhcp_pool_dict}
    )

    if result['status'] != 204:
        return None
    else:
        return result['objectId']


def delete_dhcp_pool(client_session, esg_id, pool_id):
    """
    This function deletes a DHCP Pools from an edge DHCP Server

    :type client_session: nsxramlclient.client.NsxClient
    :param client_session: A nsxramlclient session Object
    :type esg_id: str
    :param esg_id: The id of a Edge Service Gateway used for DHCP
    :type pool_id: str
    :param pool_id: The Id of the pool to be deleted (e.g. pool-3)
    :rtype: bool
    :return: Returns None if Edge was not found or the operation failed,
        returns true on success
    """

    result = client_session.delete(
        'dhcpPoolID', uri_parameters={'edgeId': esg_id, 'poolID': pool_id})

    if result['status'] == 204:
        return True
    else:
        return None


def add_mac_binding(client_session, esg_id, mac, hostname, ip,
                    default_gateway=None, subnet_mask=None, domain_name=None,
                    dns_server_1=None, dns_server_2=None, lease_time=None,
                    auto_dns=None):
    """
    This function add a MAC based static binding entry to an edge DHCP Server

    :type client_session: nsxramlclient.client.NsxClient
    :param client_session: A nsxramlclient session Object
    :type esg_id: str
    :param esg_id: The display name of a Edge Service Gateway used for DHCP
    :type mac: str
    :param mac: The MAC Address of the static binding
    :type hostname: str
    :param hostname: The hostname for this static binding
    :type ip: str
    :param ip: The IP Address for this static binding
    :type default_gateway: str
    :param default_gateway: The default gateway for the specified binding
    :type subnet_mask: str
    :param subnet_mask: The subnet mask (e.g. 255.255.255.0) for the
        specified binding
    :type domain_name: str
    :param domain_name: The DNS domain name (e.g. vmware.com) for the
        specified binding
    :type dns_server_1: str
    :param dns_server_1: The primary DNS Server
    :type dns_server_2: str
    :param dns_server_2: The secondary DNS Server
    :type lease_time: str
    :param lease_time: The lease time in seconds, use 'infinite' to
        disable expiry of DHCP leases
    :type auto_dns: str
    :param auto_dns: ('true'/'false') If set to true, the DNS servers
        and domain name set for NSX-Manager will be used
    :rtype: str
    :return: Returns a string containing the binding id of the created DHCP
        binding
    """

    binding_dict = {
        'macAddress': mac, 'hostname': hostname, 'ipAddress': ip,
        'defaultGateway': default_gateway, 'subnetMask': subnet_mask,
        'domainName': domain_name, 'primaryNameServer': dns_server_1,
        'secondaryNameServer': dns_server_2, 'leaseTime': lease_time,
        'autoConfigureDNS': auto_dns
    }

    result = client_session.create(
        'dhcpStaticBinding', uri_parameters={'edgeId': esg_id},
        request_body_dict={'staticBinding': binding_dict}
    )
    if result['status'] != 204:
        return None
    else:
        return result['objectId']


def add_vm_binding(client_session, esg_id, vm_id, vnic_id, hostname, ip,
                   default_gateway=None, subnet_mask=None, domain_name=None,
                   dns_server_1=None, dns_server_2=None, lease_time=None,
                   auto_dns=None):
    """
    This function add a VM based static binding entry to an edge DHCP Server

    :type client_session: nsxramlclient.client.NsxClient
    :param client_session: A nsxramlclient session Object
    :type esg_id: str
    :param esg_id: The id of a Edge Service Gateway used for DHCP
    :type vm_id: str
    :param vm_id: The VM managed object Id in vCenter for the VM to be
        attached to this binding entry
    :type vnic_id: str
    :param vnic_id: The vnic index for the VM interface attached to this
        binding entry (e.g. vnic0 has index 0)
    :type hostname: str
    :param hostname: The hostname for this static binding
    :type ip: str
    :param ip: The IP Address for this static binding
    :type default_gateway: str
    :param default_gateway: The default gateway for the specified binding
    :type subnet_mask: str
    :param subnet_mask: The subnet mask (e.g. 255.255.255.0) for the
        specified binding
    :type domain_name: str
    :param domain_name: The DNS domain name (e.g. vmware.com) for the
        specified binding
    :type dns_server_1: str
    :param dns_server_1: The primary DNS Server
    :type dns_server_2: str
    :param dns_server_2: The secondary DNS Server
    :type lease_time: str
    :param lease_time: The lease time in seconds, use 'infinite' to disable
        expiry of DHCP leases
    :type auto_dns: str
    :param auto_dns: ('true'/'false') If set to true, the DNS servers and
        domain name set for NSX-Manager will be used
    :rtype: str
    :return: Returns a string containing the binding id of the created DHCP
        binding
    """

    binding_dict = {'vmId': vm_id, 'vnicId': vnic_id, 'hostname': hostname,
                    'ipAddress': ip, 'defaultGateway': default_gateway,
                    'subnetMask': subnet_mask, 'domainName': domain_name,
                    'primaryNameServer': dns_server_1,
                    'secondaryNameServer': dns_server_2,
                    'leaseTime': lease_time,
                    'autoConfigureDNS': auto_dns}

    result = client_session.create(
        'dhcpStaticBinding', uri_parameters={'edgeId': esg_id},
        request_body_dict={'staticBinding': binding_dict}
    )
    if result['status'] != 204:
        return None
    else:
        return result['objectId']


def delete_dhcp_binding(client_session, esg_id, binding_id):
    """
    This function deletes a DHCP binding from an edge DHCP Server

    :type client_session: nsxramlclient.client.NsxClient
    :param client_session: A nsxramlclient session Object
    :type esg_id: str
    :param esg_id: The id of a Edge Service Gateway used for DHCP
    :type binding_id: str
    :param binding_id: The Id of the binding to be deleted (e.g. binding-3)
    :rtype: bool
    :return: Returns None if Edge was not found or the operation failed,
        returns true on success
    """

    result = client_session.delete(
        'dhcpStaticBindingID',
        uri_parameters={'edgeId': esg_id, 'bindingID': binding_id}
    )

    if result['status'] == 204:
        return True
    else:
        return None
