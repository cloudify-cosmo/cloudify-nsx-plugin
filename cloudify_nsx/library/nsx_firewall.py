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


def add_firewall_rule(client_session, esg_id, application='any',
                      direction='any', name="", loggingEnabled=False,
                      matchTranslated=False, destination='any',
                      enabled=True, source='any', action='accept',
                      ruleTag=None, description=None):

    firewall_spec = {}
    firewall_spec['firewallRules'] = {}
    firewall_spec['firewallRules']['firewallRule'] = {}

    firewall_spec['firewallRules']['firewallRule']['name'] = name
    firewall_spec['firewallRules']['firewallRule']['action'] = action


    firewall_spec['firewallRules']['firewallRule']['direction'] = direction
    firewall_spec['firewallRules']['firewallRule']['application'] = application
    if loggingEnabled:
        firewall_spec['firewallRules']['firewallRule']['loggingEnabled'] = 'true'
    else:
        firewall_spec['firewallRules']['firewallRule']['loggingEnabled'] = 'false'

    if matchTranslated:
        firewall_spec['firewallRules']['firewallRule']['matchTranslated'] = 'true'
    else:
        firewall_spec['firewallRules']['firewallRule']['matchTranslated'] = 'false'

    firewall_spec['firewallRules']['firewallRule']['destination'] = destination
    if enabled:
        firewall_spec['firewallRules']['firewallRule']['enabled'] = 'true'
    else:
        firewall_spec['firewallRules']['firewallRule']['enabled'] = 'false'
    firewall_spec['firewallRules']['firewallRule']['source'] = source
    if ruleTag:
        firewall_spec['firewallRules']['firewallRule']['ruleTag'] = ruleTag
    if description:
        firewall_spec['firewallRules']['firewallRule']['description'] = description

    result = client_session.create(
        'firewallRules', uri_parameters={'edgeId': esg_id},
        request_body_dict=firewall_spec
    )

    if result['status'] >= 200 and result['status'] < 300:
        return result['objectId'], result['location']
    else:
        return None, None


def delete_firewall_rule(client_session, esg_id, resource_id):
    result = client_session.delete(
        'firewallRule', uri_parameters={'edgeId': esg_id, 'ruleId': resource_id}
    )

    if result['status'] == 204:
        return True
    else:
        return None
