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


def get_tag(client_session, name):
    return common.nsx_search(
        client_session, 'body/securityTags/securityTag',
        name, 'securityTag'
    )


def add_tag(client_session, name, description):

    security_group = {
        'securityTag': {
            'name': name
        }
    }

    if description:
        security_group['securityTag']['description'] = description

    result_raw = client_session.create(
        'securityTag',
        request_body_dict=security_group
    )

    common.check_raw_result(result_raw)

    return result_raw['objectId']


def delete_tag(client_session, resource_id):
    result = client_session.delete(
        'securityTagID',
        uri_parameters={'tagId': resource_id}
    )
    common.check_raw_result(result)


def add_tag_vm(client_session, tag_id, vm_id):
    result_raw = client_session.update(
        'securityTagVM',
        uri_parameters={
            'tagId': tag_id,
            'vmMoid': vm_id
        }
    )
    common.check_raw_result(result_raw)

    return "%s|%s" % (tag_id, vm_id)


def delete_tag_vm(client_session, resource_id):
    ids = resource_id.split("|")

    if len(ids) != 2:
        raise cfy_exc.NonRecoverableError(
            'Unexpected error retrieving resource ID'
        )

    result_raw = client_session.delete(
        'securityTagVM',
        uri_parameters={
            'tagId': ids[0],
            'vmMoid': ids[1]
        }
    )

    common.check_raw_result(result_raw)
