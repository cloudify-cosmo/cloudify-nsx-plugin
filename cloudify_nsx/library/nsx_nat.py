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


def nat_service(client_session, esg_id, enabled):
    change_needed = False

    current_nat_config = client_session.read(
        'edgeNat', uri_parameters={'edgeId': esg_id}
    )['body']
    new_nat_config = current_nat_config

    if enabled:
        if current_nat_config['nat']['enabled'] == 'false':
            new_nat_config['nat']['enabled'] = 'true'
            change_needed = True
    else:
        if current_nat_config['nat']['enabled'] == 'true':
            new_nat_config['nat']['enabled'] = 'false'
            change_needed = True

    if not change_needed:
        return True
    else:
        result = client_session.update(
            'edgeNat', uri_parameters={'edgeId': esg_id},
            request_body_dict=new_nat_config
        )
        if result['status'] == 204:
            return True
        else:
            return False


def add_nat_rule(client_session, esg_id, action, originalAddress,
                 translatedAddress, vnic=None, ruleTag=None,
                 loggingEnabled=False, enabled=True, description='',
                 protocol='any', translatedPort='any', originalPort='any'):

    nat_spec = client_session.extract_resource_body_example(
        'edgeNatRules', 'create'
    )

    nat_rule = {
        'ruleTag': ruleTag,
        'action': action,
        'vnic': vnic,
        'originalAddress': originalAddress,
        'translatedAddress': translatedAddress,
        'description': description,
        'protocol': protocol,
        'translatedPort': originalPort,
        'originalPort': translatedPort
    }

    if loggingEnabled:
        nat_rule['loggingEnabled'] = 'true'
    else:
        nat_rule['loggingEnabled'] = 'false'
    if enabled:
        nat_rule['enabled'] = 'true'
    else:
        nat_rule['enabled'] = 'false'

    nat_spec['natRules']['natRule'] = nat_rule

    result_raw = client_session.create(
        'edgeNatRules', uri_parameters={'edgeId': esg_id},
        request_body_dict=nat_spec
    )

    common.check_raw_result(result_raw)

    return result_raw['objectId']


def delete_nat_rule(client_session, esg_id, resource_id):
    result = client_session.delete(
        'edgeNatRule', uri_parameters={'edgeId': esg_id, 'ruleID': resource_id}
    )

    if result['status'] == 204:
        return True
    else:
        return None
