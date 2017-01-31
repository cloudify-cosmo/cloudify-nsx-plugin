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


def get_tag(client_session, name):
    result_raw = client_session.read('securityTag')

    common.check_raw_result(result_raw)

    if 'securityTags' not in result_raw['body']:
        return None, None

    if 'securityTag' not in result_raw['body']['securityTags']:
        return None, None

    tags = result_raw['body']['securityTags']['securityTag']

    if isinstance(tags, dict):
        tags = [tags]

    for tag in tags:
        if 'name' in tag:
            if str(tag['name']) == str(name):
                return tag['objectId'], tag

    return None, None


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


def delete_tag(client_session, securityid):
    result = client_session.delete(
        'securityTagID',
        uri_parameters={'tagId': securityid}
    )

    if result['status'] == 204:
        return True
    else:
        return None


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

    result_raw = client_session.delete(
        'securityTagVM',
        uri_parameters={
            'tagId': ids[0],
            'vmMoid': ids[1]
        }
    )

    common.check_raw_result(result_raw)
