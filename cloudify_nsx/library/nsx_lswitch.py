# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved
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


def get_logical_switch(client_session, logical_switch_id):
    raw_result = client_session.read('logicalSwitch', uri_parameters={
        'virtualWireID': logical_switch_id
    })
    common.check_raw_result(raw_result)
    return raw_result['body']['virtualWire']


def del_logical_switch(client_session, resource_id):
    raw_result = client_session.delete(
        'logicalSwitch', uri_parameters={'virtualWireID': resource_id}
    )
    common.check_raw_result(raw_result)
