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


def get_uplink_vnic(client_session, esg_id, uplink_ls_id):
    """Search uplink vnic"""
    raw_result = client_session.read(
        'interfaces', uri_parameters={'edgeId': esg_id}
    )
    interfaces_struct = raw_result['body']
    common.check_raw_result(raw_result)
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


def bgp_create(client_session, esg_id, enabled, defaultOriginate,
               gracefulRestart, redistribution, localAS):

    raw_result = client_session.read(
        'routingBGP', uri_parameters={'edgeId':  esg_id})

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


def add_bgp_neighbour(client_session, esg_id, use_existed, ipAddress,
                      remoteAS, weight, holdDownTimer, keepAliveTimer,
                      password, protocolAddress, forwardingAddress):
    raw_result = client_session.read(
        'routingBGP', uri_parameters={'edgeId':  esg_id})

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

        if not use_existed:
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
            use_existed = False
            break

    if use_existed:
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
        'routingBGP', uri_parameters={'edgeId':  esg_id})

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

    for i in xrange(len(bgp_neighbours)):
        bgp_neighbour = bgp_neighbours[i]
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


def add_bgp_neighbour_filter(client_session, use_existed, neighbour_id,
                             action, ipPrefixGe, ipPrefixLe, direction,
                             network):
    ids = neighbour_id.split("|")

    esg_id, ipAddress, remoteAS, protocolAddress, forwardingAddress = ids

    raw_result = client_session.read(
        'routingBGP', uri_parameters={'edgeId':  esg_id})

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

    for bgp_filter in bgp_filters:
        if str(bgp_filter['network']) != network:
            continue
        if not use_existed:
            raise cfy_exc.NonRecoverableError(
                "You already have such filter(same network)"
            )
        else:
            bgp_filter['action'] = action
            bgp_filter['ipPrefixGe'] = ipPrefixGe
            bgp_filter['ipPrefixLe'] = ipPrefixLe
            bgp_filter['direction'] = direction
            use_existed = False
            break

    if use_existed:
        raise cfy_exc.NonRecoverableError(
            "You don't have such rule"
        )
    else:
        bgp_filter = {
            'network': network,
            'action': action,
            'ipPrefixGe': ipPrefixGe,
            'ipPrefixLe':  ipPrefixLe,
            'direction':  direction
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
        'routingBGP', uri_parameters={'edgeId':  esg_id})

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

    for i in xrange(bgp_filters):
        bgp_filter = bgp_filters[i]
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
        'routingOSPF', uri_parameters={'edgeId':  esg_id})

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


def esg_ospf_area_add(client_session, esg_id, area_id, use_existed, area_type,
                      auth):
    raw_result = client_session.read(
        'routingOSPF', uri_parameters={'edgeId':  esg_id})

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

    for area in ospf_areas:
        if str(area['areaId']) != str(area_id):
            continue
        if not use_existed:
            raise cfy_exc.NonRecoverableError(
                "You already have such rule"
            )
        else:
            area['type'] = area_type
            area['authentication'] = auth
            use_existed = False
            break

    if use_existed:
        raise cfy_exc.NonRecoverableError(
            "You don't have such rule"
        )
    else:
        ospf_areas.append({
            'areaId': area_id,
            'type': area_type,
            'authentication': auth})

    raw_result = client_session.update(
        'routingOSPF', uri_parameters={'edgeId':  esg_id},
        request_body_dict=ospf
    )

    common.check_raw_result(raw_result)


def esg_ospf_interface_add(client_session, esg_id, area_id, vnic, use_existed,
                           hello_interval, dead_interval, priority, cost):

    raw_result = client_session.read(
        'routingOSPF', uri_parameters={'edgeId':  esg_id})

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

    for interface in ospf_interfaces:
        if str(interface['areaId']) != str(area_id):
            continue

        if str(interface['vnic']) != str(vnic):
            continue

        if not use_existed:
            raise cfy_exc.NonRecoverableError(
                "You already have such rule"
            )
        else:
            interface['helloInterval'] = hello_interval
            interface['deadInterval'] = dead_interval
            interface['priority'] = priority
            interface['cost'] = cost
            use_existed = False
            break

    if use_existed:
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
        'routingOSPF', uri_parameters={'edgeId':  esg_id},
        request_body_dict=ospf
    )

    common.check_raw_result(raw_result)


def esg_ospf_area_delete(client_session, esg_id, area_id):
    raw_result = client_session.read(
        'routingOSPF', uri_parameters={'edgeId':  esg_id})

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

    for i in xrange(len(ospf_areas)):
        if str(ospf_areas[i]['areaId']) == str(area_id):
            ospf_areas.remove(ospf_areas[i])

    raw_result = client_session.update(
        'routingOSPF', uri_parameters={'edgeId':  esg_id},
        request_body_dict=ospf
    )
    common.check_raw_result(raw_result)


def esg_ospf_interface_delete(client_session, esg_id, area_id, vnic):
    raw_result = client_session.read(
        'routingOSPF', uri_parameters={'edgeId':  esg_id})

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

    for i in xrange(len(ospf_interfaces)):
        if str(ospf_interfaces[i]['areaId']) != str(area_id):
            continue

        if str(ospf_interfaces[i]['vnic']) != str(vnic):
            continue

        ospf_interfaces.remove(ospf_interfaces[i])

    raw_result = client_session.update(
        'routingOSPF', uri_parameters={'edgeId':  esg_id},
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

    _, firewall = common.get_properties_and_validate('firewall', kwargs)

    if not esg_fw_default_set(
        client_session,
        resource_id,
        firewall['action'],
        firewall['logging']
    ):
        raise cfy_exc.NonRecoverableError(
            "Can't change firewall rules"
        )

    _, dhcp = common.get_properties_and_validate('dhcp', kwargs)

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

    _, routing = common.get_properties_and_validate('routing', kwargs)
    routing_global_config(
        client_session, resource_id,
        routing['enabled'], routing['routingGlobalConfig'],
        routing['staticRouting']
    )

    _, ospf = common.get_properties_and_validate('ospf', kwargs)
    _, bgp = common.get_properties_and_validate('bgp', kwargs)

    # disable bgp before change ospf (if need)
    if not bgp['enabled']:
        bgp_create(
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
        bgp_create(
            client_session, resource_id,
            bgp['enabled'], bgp['defaultOriginate'],
            bgp['gracefulRestart'], bgp['redistribution'],
            bgp['localAS']
        )

    if esg_restriction:
        _, nat = common.get_properties_and_validate('nat', kwargs)

        if not nsx_nat.nat_service(
            client_session,
            resource_id,
            nat['enabled']
        ):
            raise cfy_exc.NonRecoverableError(
                "Can't change nat rules"
            )
