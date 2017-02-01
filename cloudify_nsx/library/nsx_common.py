########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
from cloudify import ctx
from pkg_resources import resource_filename
from nsxramlclient.client import NsxClient
from cloudify import exceptions as cfy_exc


def _cleanup_properties(value):
    """we need such because nsxclient does not support unicode strings"""
    if isinstance(value, unicode):
        return str(value)
    if isinstance(value, dict):
        return _cleanup_properties_dict(value)
    if isinstance(value, list):
        return _cleanup_properties_list(value)
    return value


def _cleanup_properties_dict(properties_dict):
    """convert all fields in dict to string"""
    result = {}

    for key in properties_dict.iterkeys():
        value = properties_dict[key]
        if isinstance(key, (unicode, int)):
            key = str(key)
        result[key] = _cleanup_properties(value)

    return result


def _cleanup_properties_list(properties_list):
    """convert all elements in list to string"""
    result = []

    for value in properties_list:
        result.append(_cleanup_properties(value))

    return result


def _cleanup_if_empty(value):
    """return None if all fileds equal to None, else origin dict"""
    have_not_none = False
    for key in value:
        if value[key]:
            have_not_none = True
            break
    if not have_not_none:
        value = None
    return value


def _validate(check_dict, validate_rules, use_existing):
    """Validate inputs for node creation"""
    result = {}
    for name in validate_rules:
        rule = validate_rules[name]
        required_value = rule.get('required', False)
        external_use_value = rule.get('external_use', False)
        default_value = rule.get('default', False)
        set_none = rule.get('set_none', False)
        values = rule.get('values', False)
        sub_checks = rule.get('sub', None)
        value_type = rule.get('type', 'string')
        caseinsensitive = rule.get('caseinsensitive', False)

        # we can have value == false and default == true, so only check
        # field in list
        if 'default' in rule and name not in check_dict:
            value = default_value
        else:
            value = check_dict.get(name)

        # external
        if use_existing and external_use_value and not value:
            raise cfy_exc.NonRecoverableError(
                "don't have external value for %s" % name
            )

        # not external
        if not use_existing and not external_use_value:
            # zero/true/false is also value
            if required_value and not value and not isinstance(value, int):
                raise cfy_exc.NonRecoverableError(
                    "don't have value for %s " % name
                )

        # cleanup value/values in case caseinsensitive string
        if caseinsensitive and value:
            value = value.lower()

        if caseinsensitive and values:
            values = [str(v).lower() for v in values]

        if set_none and not value:
            # empty value
            value = None
        else:
            # looks as we have some list of posible values
            if values:
                if value not in values:
                    raise cfy_exc.NonRecoverableError(
                        "Wrong value %s=%s not in %s" % (
                            name, str(value), str(values)
                        )
                    )
            if sub_checks:
                value = _validate(value, sub_checks, use_existing)
                if set_none:
                    value = _cleanup_if_empty(value)

        # sory some time we have mistake in value for boolean fields
        if value_type == 'boolean' and isinstance(value, basestring):
            value = str(value).lower() == 'true'
        # for case value==0 and we need check difference with None and False
        elif value_type == 'string' and isinstance(value, int):
            value = str(value)
        result[name] = value

    return result


def _get_properties(name, kwargs):
    properties_dict = ctx.node.properties.get(name, {})
    properties_dict.update(kwargs.get(name, {}))
    properties_dict.update(ctx.instance.runtime_properties.get(name, {}))
    ctx.instance.runtime_properties[name] = properties_dict

    # update resource_id
    resource_id = None
    if not ctx.instance.runtime_properties.get('resource_id'):
        resource_id = None
        if ctx.node.properties.get('resource_id'):
            resource_id = ctx.node.properties['resource_id']

        if kwargs.get('resource_id'):
            resource_id = kwargs['resource_id']

        if resource_id:
            ctx.instance.runtime_properties['resource_id'] = resource_id

    return _cleanup_properties_dict(properties_dict)


def get_properties(name, kwargs):
    properties_dict = _get_properties(name, kwargs)
    use_existing = ctx.node.properties.get(
        'use_external_resource', False
    )
    return use_existing, properties_dict


def get_properties_and_validate(name, kwargs, validate_dict):
    use_existing, properties_dict = get_properties(name, kwargs)
    ctx.logger.info("checking %s: %s" % (name, str(properties_dict)))
    return use_existing, _validate(
        properties_dict, validate_dict, use_existing
    )


def remove_properties(name):
    if 'resource_id' in ctx.instance.runtime_properties:
        del ctx.instance.runtime_properties['resource_id']
    if name in ctx.instance.runtime_properties:
        del ctx.instance.runtime_properties[name]


def nsx_login(kwargs):
    nsx_auth = _get_properties('nsx_auth', kwargs)

    ctx.logger.info("NSX login...")
    user = nsx_auth.get('username')
    password = nsx_auth.get('password')
    ip = nsx_auth.get('host')
    # if node contained in some other node, try to overwrite ip
    if not ip:
        ip = ctx.instance.host_ip
        ctx.logger.info("Used host from container: %s" % ip)
    # check minimal amout of credentials
    if not ip or not user or not password:
        raise cfy_exc.NonRecoverableError(
            "please check your credentials"
        )

    raml_file = nsx_auth.get('raml')
    if not raml_file:
        resource_dir = resource_filename(__name__, 'api_spec')
        raml_file = '{}/nsxvapi.raml'.format(resource_dir)
        ctx.logger.info("Will be used internal: %s" % raml_file)

    client = NsxClient(raml_file, ip, user, password)
    ctx.logger.info("NSX logged in")
    return client


def check_raw_result(result_raw):
    if result_raw['status'] < 200 or result_raw['status'] >= 300:
        ctx.logger.error("Status %s" % result_raw['status'])
        raise cfy_exc.NonRecoverableError(
            "We have error with request."
        )


def get_logical_switch(client_session, logical_switch_id):
    raw_result = client_session.read('logicalSwitch', uri_parameters={
        'virtualWireID': logical_switch_id
    })
    check_raw_result(raw_result)
    return raw_result['body']['virtualWire']


def get_edgegateway(client_session, edgeId):
    raw_result = client_session.read('nsxEdge', uri_parameters={
        'edgeId': edgeId
    })
    check_raw_result(raw_result)
    return raw_result['body']['edge']


def all_relationships_are_present(relationships,
                                  expected_relationships):
    relationships = [relationship.type for relationship in relationships]
    return all((
        expected in relationships
        for expected in expected_relationships
    ))


def any_relationships_are_present(relationships,
                                  expected_relationships):
    relationships = [relationship.type for relationship in relationships]
    return any((
        expected in relationships
        for expected in expected_relationships
    ))


def get_attribute_from_relationship(relationships,
                                    target_relationship,
                                    target_property):
    result = None
    for relationship in relationships:
        if relationship.type == target_relationship:
            result = relationship.target.instance.runtime_properties.get(
                target_property,
            )
    return result


def possibly_assign_vm_creation_props(properties_dict):
    vsphere_id_property_attribute_mapping = (
        (
            'cloudify.nsx.relationships.deployed_on_datacenter',
            'datacentermoid',
            'vsphere_datacenter_id',
        ),
        (
            'cloudify.nsx.relationships.deployed_on_datastore',
            'datastoremoid',
            'vsphere_datastore_id',
        ),
        (
            'cloudify.nsx.relationships.deployed_on_cluster',
            # Yes, it's not a resource pool, but this is the way
            # pynsxv wants things called...
            'resourcepoolid',
            'vsphere_cluster_id',
        ),
    )
    vsphere_id_relationships = (
        item[0] for item in vsphere_id_property_attribute_mapping
    )
    prop_ids = (
        item[1] for item in vsphere_id_property_attribute_mapping
    )

    all_vsphere_id_relationships = all_relationships_are_present(
        relationships=ctx.instance.relationships,
        expected_relationships=vsphere_id_relationships,
    )
    any_vsphere_id_relationships = any_relationships_are_present(
        relationships=ctx.instance.relationships,
        expected_relationships=vsphere_id_relationships,
    )
    any_prop_ids_set = any((
        properties_dict.get(prop) is not None
        for prop in prop_ids
    ))

    if (
        (any_vsphere_id_relationships and any_prop_ids_set) or
        (any_vsphere_id_relationships and not all_vsphere_id_relationships)
    ):
        raise cfy_exc.NonRecoverableError(
            'vSphere object IDs must either be provided entirely from '
            'relationships ({rels}) or entirely from properties '
            '({props}).'.format(
                rels=', '.join(vsphere_id_relationships),
                props=', '.join(prop_ids),
            )
        )
    elif all_vsphere_id_relationships:
        # Set the attributes based on the relationships
        for rel, prop, attr in vsphere_id_property_attribute_mapping:
            value = get_attribute_from_relationship(
                relationships=ctx.instance.relationships,
                target_relationship=rel,
                target_property=attr,
            )
            if value is None:
                raise cfy_exc.NonRecoverableError(
                    'Failed to retrieve {prop} from target of {rel}. '
                    'Could not get appropriate value from runtime '
                    'property: {attr}'.format(
                        prop=prop,
                        rel=rel,
                        attr=attr,
                    )
                )
            # We have to cast to str, because if we don't then we pass unicode
            # which causes pynsxv to complain that the value is set to 'null'
            properties_dict[prop] = str(value)

    return properties_dict
