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
from cloudify import exceptions as cfy_exc


def add_firewall_rule(client_session, esg_id, application='any',
                      direction='any', name="", loggingEnabled=False,
                      matchTranslated=False, destination='any',
                      enabled=True, source='any', action='accept',
                      ruleTag=None, description=None):

    firewallRule = {
        'name': name,
        'source': source,
        'action': action,
        'direction': direction,
        'application': application,
        'destination': destination
    }

    common.set_boolean_property(firewallRule, 'loggingEnabled', loggingEnabled)
    common.set_boolean_property(firewallRule, 'matchTranslated',
                                matchTranslated)
    common.set_boolean_property(firewallRule, 'enabled', enabled)

    if ruleTag:
        firewallRule['ruleTag'] = ruleTag

    if description:
        firewallRule['description'] = description

    firewall_spec = {}
    firewall_spec['firewallRules'] = {}
    firewall_spec['firewallRules']['firewallRule'] = firewallRule

    result_raw = client_session.create(
        'firewallRules', uri_parameters={'edgeId': esg_id},
        request_body_dict=firewall_spec
    )

    common.check_raw_result(result_raw)

    return result_raw['objectId'], "%s|%s" % (esg_id, result_raw['objectId'])


def delete_firewall_rule(client_session, resource_id):
    """Delete firewall rule, as resource_id used response
       from add_firewall_rule"""
    try:
        esg_id, rule_id = resource_id.split("|")
    except Exception as ex:
        raise cfy_exc.NonRecoverableError(
            'Unexpected error retrieving resource ID: %s' % str(ex)
        )

    result = client_session.delete(
        'firewallRule', uri_parameters={
            'edgeId': esg_id, 'ruleId': rule_id
        })

    common.check_raw_result(result)
