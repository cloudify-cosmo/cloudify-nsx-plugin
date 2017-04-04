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
import unittest
import mock
import pytest
import copy
import cloudify_nsx.library.nsx_common as common
import cloudify_nsx.nsx_object as nsx_object_type
from cloudify import exceptions as cfy_exc
from cloudify.state import current_ctx
import test_nsx_base


class NsxCommonTest(test_nsx_base.NSXBaseTest):

    def setUp(self):
        super(NsxCommonTest, self).setUp()

    def tearDown(self):
        current_ctx.clear()
        super(NsxCommonTest, self).tearDown()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_cleanup_properties(self):
        """Check nsx_common._cleanup_properties func"""
        self.assertEqual(
            common._cleanup_properties(u'test_unicode'),
            'test_unicode'
        )
        self.assertFalse(
            isinstance(common._cleanup_properties(u'test_unicode'), unicode)
        )

        self.assertEqual(
            common._cleanup_properties([u'test_unicode', 1, True]),
            ['test_unicode', 1, True]
        )

        self.assertEqual(
            common._cleanup_properties({
                u'test_unicode': u'test_unicode',
                'other': [1, True]
            }),
            {
                'test_unicode': 'test_unicode',
                'other': [1, True]
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_cleanup_if_empty(self):
        """Check nsx_common._cleanup_if_empty func"""
        self.assertEqual(
            common._cleanup_if_empty({}),
            None
        )
        self.assertEqual(
            common._cleanup_if_empty({'a': None, 'b': None}),
            None
        )
        self.assertEqual(
            common._cleanup_if_empty({'a': None, 'b': 1}),
            {'a': None, 'b': 1}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_validate_empty(self):
        """Check nsx_common._validate func: empty"""
        self.assertEqual(
            common._validate({}, {}, False),
            {}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_validate_default(self):
        """Check nsx_common._validate func: default"""
        self.assertEqual(
            common._validate({}, {'a': {'default': 'd'}}, False),
            {'a': 'd'}
        )

        self.assertEqual(
            common._validate({'a': 'c'}, {'a': {'default': 'd'}}, False),
            {'a': 'c'}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_validate_external(self):
        """Check nsx_common._validate func: external"""
        with self.assertRaises(cfy_exc.NonRecoverableError):
            common._validate({}, {'a': {'external_use': True}}, True)

        self.assertEqual(
            common._validate({}, {'a': {'external_use': False}}, True),
            {'a': None}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_validate_required(self):
        """Check nsx_common._validate func: required"""
        with self.assertRaises(cfy_exc.NonRecoverableError):
            common._validate({}, {'a': {'required': True}}, False)

    @pytest.mark.internal
    @pytest.mark.unit
    def test_validate_caseinsensitive(self):
        """Check nsx_common._validate func: caseinsensitive"""
        self.assertEqual(
            common._validate(
                {'a': 'AbC'}, {'a': {'caseinsensitive': True}}, False
            ),
            {'a': 'abc'}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_validate_values(self):
        """Check nsx_common._validate func: values"""
        self.assertEqual(
            common._validate(
                {'a': 'a'}, {'a': {'values': ['a', 'b', 'c']}}, False
            ),
            {'a': 'a'}
        )
        with self.assertRaises(cfy_exc.NonRecoverableError):
            common._validate(
                {'a': 'd'}, {'a': {'values': ['a', 'b', 'c']}}, False
            )

        with self.assertRaises(cfy_exc.NonRecoverableError):
            common._validate(
                {'a': 'D'}, {'a': {'values': ['a', 'b', 'c']}}, False
            )

        self.assertEqual(
            common._validate(
                {'a': 'A'}, {'a': {
                    'caseinsensitive': True, 'values': ['a', 'b', 'c']
                }}, False
            ),
            {'a': 'a'}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_validate_set_None(self):
        """Check nsx_common._validate func: set None"""
        self.assertEqual(
            common._validate(
                {}, {'a': {'set_none': True}}, False
            ),
            {'a': None}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_validate_sub_checks(self):
        """Check nsx_common._validate func: sub checks"""
        self.assertEqual(
            common._validate(
                {'a': {'b': 'c'}},
                {'a': {
                    'sub': {
                        'b': {
                            'values': ['a', 'b', 'c']
                        }
                    }
                }}, False
            ),
            {'a': {'b': 'c'}}
        )

        self.assertEqual(
            common._validate(
                {'a': {'g': None}},
                {'a': {
                    'set_none': True,
                    'sub': {
                        'b': {
                            'set_none': True,
                            'values': ['a', 'b', 'c']
                        }
                    }
                }}, False
            ),
            {'a': None}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_validate_boolean_type(self):
        """Check nsx_common._validate func: boolean type"""
        self.assertEqual(
            common._validate(
                {'a': 'true'},
                {'a': {
                    'type': 'boolean'
                }}, False
            ),
            {'a': True}
        )

        self.assertEqual(
            common._validate(
                {'a': 'True'},
                {'a': {
                    'type': 'boolean'
                }}, False
            ),
            {'a': True}
        )

        self.assertEqual(
            common._validate(
                {'a': 'false'},
                {'a': {
                    'type': 'boolean'
                }}, False
            ),
            {'a': False}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_validate_string_type(self):
        """Check nsx_common._validate func: string type"""
        self.assertEqual(
            common._validate(
                {'a': 0},
                {'a': {
                    'type': 'string'
                }}, False
            ),
            {'a': '0'}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_get_properties(self):
        """Check nsx_common._get_properties func"""
        self._regen_ctx()
        self.fake_ctx.node.properties['a'] = {
            'node_properties': 'node.properties',
            'common': 'a'
        }

        self.fake_ctx.instance.runtime_properties['a'] = {
            'instance_runtime_properties': 'instance.runtime_properties',
            'common': 'b'
        }

        self.assertEqual(
            common._get_properties('a', {'a': {
                'kwargs': 'kwargs',
                'common': 'c',
                'unicode': u'unicode'
            }}),
            {
                'common': 'b',
                'instance_runtime_properties': 'instance.runtime_properties',
                'node_properties': 'node.properties',
                'kwargs': 'kwargs',
                'unicode': 'unicode'
            }
        )

        self.assertEqual(
            self.fake_ctx.instance.runtime_properties['a'],
            {
                'common': 'b',
                'instance_runtime_properties': 'instance.runtime_properties',
                'node_properties': 'node.properties',
                'kwargs': 'kwargs',
                'unicode': u'unicode'
            }
        )

        self._regen_ctx()
        self.fake_ctx.instance.runtime_properties['resource_id'] = 10
        self.fake_ctx.node.properties['resource_id'] = 15
        self.assertEqual(
            common._get_properties('a', {'resource_id': 43}),
            {}
        )

        self.assertEqual(
            self.fake_ctx.instance.runtime_properties['resource_id'],
            10
        )

        self._regen_ctx()
        self.fake_ctx.node.properties['resource_id'] = 10
        self.assertEqual(
            common._get_properties('a', {'resource_id': 43}),
            {}
        )
        self.assertEqual(
            self.fake_ctx.instance.runtime_properties['resource_id'],
            43
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_get_properties_public(self):
        """Check nsx_common.get_properties func"""
        self._regen_ctx()
        self.assertEqual(
            common.get_properties('some_name', {'some_name': {
                'somevalue': True
            }}),
            (False, {'somevalue': True})
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_get_properties_public_external_properties(self):
        """Check nsx_common.get_properties func:
           use_external_resource in properties"""
        self._regen_ctx()
        self.fake_ctx.node.properties['use_external_resource'] = True
        self.assertEqual(
            common.get_properties('some_name', {'some_name': {
                'somevalue': False
            }}),
            (True, {'somevalue': False})
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_get_properties_public_external_inputs(self):
        """Check nsx_common.get_properties func:
           use_external_resource in inputs"""
        self._regen_ctx()
        self.assertEqual(
            common.get_properties('some_name', {'some_name': {
                'somevalue': False
            }, 'use_external_resource': True}),
            (True, {'somevalue': False})
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_get_properties_public_external_inputs_presaved(self):
        """Check nsx_common.get_properties func:
           use_external_resource in inputs, prestored"""
        self._regen_ctx()
        # case when in install we already set use_external_resource
        # to input
        runtime_properties = self.fake_ctx.instance.runtime_properties
        runtime_properties['use_external_resource'] = True
        self.assertEqual(
            common.get_properties('some_name', {'some_name': {
                'somevalue': False
            }}),
            (True, {'somevalue': False})
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_get_properties_and_validate(self):
        """Check nsx_common.get_properties_and_validate func"""
        self._regen_ctx()
        self.assertEqual(
            common.get_properties_and_validate('some_name', {'some_name': {
                'somevalue': True,
                'not_showed': 'really'
            }}, {'somevalue': {'type': 'boolean'}}),
            (False, {'somevalue': True})
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_check_raw_result(self):
        """Check nsx_common.check_raw_result func"""
        self._regen_ctx()
        # common response on successful result
        common.check_raw_result({'status': 204})
        # check other posible successful results
        for i in xrange(200, 299):
            common.check_raw_result({'status': i})

        with self.assertRaises(cfy_exc.NonRecoverableError) as error:
            common.check_raw_result({'status': 199})
        self.assertEqual(
            str(error.exception),
            "We have error with request."
        )

        with self.assertRaises(cfy_exc.NonRecoverableError) as error:
            common.check_raw_result({'status': 300})
        self.assertEqual(
            str(error.exception),
            "We have error with request."
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_remove_properties(self):
        """Check nsx_common.remove_properties func"""
        self._regen_ctx()
        runtime_properties = self.fake_ctx.instance.runtime_properties
        runtime_properties['resource_id'] = '1'
        runtime_properties['resource'] = '2'
        runtime_properties['not_resource'] = '3'
        runtime_properties['nsx_auth'] = '4'
        runtime_properties['use_external_resource'] = '5'
        common.remove_properties('resource')
        self.assertEqual(
            self.fake_ctx.instance.runtime_properties,
            {'not_resource': '3'}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_attempt_with_rerun(self):
        """Check nsx_common.attempt_with_rerun func"""
        self._regen_ctx()

        def func_error(need_error):
            if need_error:
                raise need_error()

        common.attempt_with_rerun(func_error, need_error=False)

        fake_sleep = mock.MagicMock()
        with mock.patch(
            'time.sleep',
            fake_sleep
        ):
            with self.assertRaises(cfy_exc.NonRecoverableError):
                common.attempt_with_rerun(
                    func_error, need_error=cfy_exc.NonRecoverableError
                )
            fake_sleep.assert_not_called()

            with self.assertRaises(cfy_exc.RecoverableError):
                common.attempt_with_rerun(
                    func_error, need_error=cfy_exc.RecoverableError
                )
            fake_sleep.assert_called_with(30)

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_login_no_credentials(self):
        """Check nsx_common.attempt_with_rerun func: no credentials"""
        self._regen_ctx()

        fake_client = mock.MagicMock()
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            # no credentials
            with self.assertRaises(cfy_exc.NonRecoverableError) as error:
                common.nsx_login({})
            fake_client.assert_not_called()

            self.assertEqual(
                str(error.exception),
                "please check your credentials"
            )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_login_ip_from_instance(self):
        """Check nsx_common.attempt_with_rerun func: ip from instance ip"""
        self._regen_ctx()
        fake_client = mock.MagicMock(return_value='Called')
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            # instance ip
            self.fake_ctx.instance.host_ip = "instance_ip"
            self.assertEqual(
                common.nsx_login({
                    'nsx_auth': {
                        'username': 'username',
                        'password': 'password',
                        'raml': 'raml'
                    }
                }), 'Called'
            )
            fake_client.assert_called_with(
                'raml', 'instance_ip', 'username', 'password'
            )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_login_ip_from_inputs(self):
        """Check nsx_common.attempt_with_rerun func:ip from inputs"""
        self._regen_ctx()
        fake_client = mock.MagicMock(return_value='Called')
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            # with ip from params
            self.assertEqual(
                common.nsx_login({
                    'nsx_auth': {
                        'username': 'username',
                        'password': 'password',
                        'raml': 'raml',
                        'host': 'ip'
                    }
                }), 'Called'
            )
            fake_client.assert_called_with(
                'raml', 'ip', 'username', 'password'
            )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_login_without_raml(self):
        """Check nsx_common.attempt_with_rerun func: withour raml"""
        self._regen_ctx()
        fake_client = mock.MagicMock(return_value='Called')
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            with mock.patch(
                'cloudify_nsx.library.nsx_common.resource_filename',
                mock.MagicMock(return_value='other_raml')
            ):
                # without raml
                self.assertEqual(
                    common.nsx_login({
                        'nsx_auth': {
                            'username': 'username',
                            'password': 'password',
                            'host': 'ip'
                        }
                    }), 'Called'
                )

            fake_client.assert_called_with(
                'other_raml/nsxvapi.raml', 'ip', 'username', 'password'
            )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_delete_object_not_fully(self):
        """Check nsx_common.attempt_with_rerun func: not fully created"""
        self._regen_ctx()
        fake_client = mock.MagicMock()
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            self.fake_ctx.instance.runtime_properties['resource_id'] = None
            self.fake_ctx.instance.runtime_properties['d'] = None
            self.fake_ctx.instance.runtime_properties['m'] = None
            common.delete_object(None, 'a', {'a': {'b': 'c'}}, ['d', 'm'])
            self.assertEqual(self.fake_ctx.instance.runtime_properties, {})

    @pytest.mark.internal
    @pytest.mark.unit
    def test_delete_object_use_external(self):
        """Check nsx_common.attempt_with_rerun func: use external"""
        self._regen_ctx()
        fake_client = mock.MagicMock()
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            self.fake_ctx.instance.runtime_properties['resource_id'] = '!'
            self.fake_ctx.node.properties['use_external_resource'] = True
            self.fake_ctx.instance.runtime_properties['d'] = 'f'
            self.fake_ctx.instance.runtime_properties['m'] = 'g'
            common.delete_object(None, 'a', {'a': {'b': 'c'}}, ['d', 'm'])
            self.assertEqual(self.fake_ctx.instance.runtime_properties, {})

    @pytest.mark.internal
    @pytest.mark.unit
    def test_delete_object_call_with_exception(self):
        """Check nsx_common.attempt_with_rerun func: call with exception"""
        self._regen_ctx()
        self.fake_ctx.instance.runtime_properties['resource_id'] = 'r_id'
        kwargs = {
            'a': {'b': 'c'},
            'nsx_auth': {
                'username': 'username',
                'password': 'password',
                'host': 'host',
                'raml': 'raml'
            }
        }
        fake_client = mock.MagicMock(
            side_effect=cfy_exc.NonRecoverableError()
        )
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):

            with self.assertRaises(cfy_exc.NonRecoverableError):
                common.delete_object(None, 'a', kwargs, ['d', 'm'])

            fake_client.assert_called_with(
                'raml', 'host', 'username', 'password'
            )
            runtime = self.fake_ctx.instance.runtime_properties
            self.assertEqual(runtime['resource_id'], 'r_id')
            self.assertEqual(
                runtime['nsx_auth'], {
                    'username': 'username',
                    'password': 'password',
                    'host': 'host',
                    'raml': 'raml'
                }
            )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_delete_object_positive(self):
        """Check nsx_common.attempt_with_rerun func: success"""
        self._regen_ctx()
        self.fake_ctx.instance.runtime_properties['resource_id'] = 'r_id'
        kwargs = {
            'a': {'b': 'c'},
            'nsx_auth': {
                'username': 'username',
                'password': 'password',
                'host': 'host',
                'raml': 'raml'
            }
        }
        fake_client_result = mock.MagicMock()
        fake_client = mock.MagicMock(
            return_value=fake_client_result
        )
        fake_func_for_call = mock.MagicMock()
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            common.delete_object(fake_func_for_call, 'a', kwargs, ['d', 'm'])
            fake_client.assert_called_with(
                'raml', 'host', 'username', 'password'
            )
            fake_func_for_call.assert_called_with(
                client_session=fake_client_result, resource_id='r_id'
            )
            self.assertEqual(self.fake_ctx.instance.runtime_properties, {})

    @pytest.mark.internal
    @pytest.mark.unit
    def test_set_boolean_property_recreate_path(self):
        """Check nsx_common.set_boolean_property func: recreate path"""
        # recreate path
        a = {}
        self.assertTrue(common.set_boolean_property(a, 'b/c', True))
        self.assertEqual(a, {'b': {'c': 'true'}})

    @pytest.mark.internal
    @pytest.mark.unit
    def test_set_boolean_property_without_changes(self):
        """Check nsx_common.set_boolean_property func:
           already have correct value"""
        a = {'b': {'c': 'true'}}
        self.assertFalse(common.set_boolean_property(a, 'b/c', True))
        self.assertEqual(a, {'b': {'c': 'true'}})

    @pytest.mark.internal
    @pytest.mark.unit
    def test_set_boolean_property_with_changes(self):
        """Check nsx_common.set_boolean_property func: need to update"""
        a = {'b': {'c': 'true'}}
        self.assertTrue(common.set_boolean_property(a, 'b/c', False))
        self.assertEqual(a, {'b': {'c': 'false'}})

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_read(self):
        """Check nsx_common.nsx_read func"""
        self._regen_ctx()
        client_session = mock.Mock()

        # we raise error?
        client_session.read = mock.Mock(return_value={
            'body': {}, 'status': 300
        })
        with self.assertRaises(cfy_exc.NonRecoverableError) as error:
            common.nsx_read(client_session, 'body/a', 'secret',
                            uri_parameters={'scopeId': 'scopeId'})
        self.assertEqual(
            str(error.exception),
            "We have error with request."
        )

        # return None for not existed
        client_session.read = mock.Mock(return_value={
            'body': {'b': 'c'}, 'status': 204
        })
        self.assertEqual(
            common.nsx_read(client_session, 'body/a', 'secret',
                            uri_parameters={'scopeId': 'scopeId'}),
            None
        )
        client_session.read.assert_called_with(
            'secret', uri_parameters={'scopeId': 'scopeId'}
        )

        # return real value
        self.assertEqual(
            common.nsx_read(client_session, 'body/b', 'secret',
                            uri_parameters={'scopeId': 'scopeId'}),
            'c'
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_search_error_raise(self):
        """Check nsx_common.nsx_search func: error raise"""
        self._regen_ctx()
        client_session = mock.Mock()

        # we raise error?
        client_session.read = mock.Mock(return_value={
            'body': {}, 'status': 300
        })
        with self.assertRaises(cfy_exc.NonRecoverableError) as error:
            common.nsx_search(client_session, 'body/a', 'b', 'secret',
                              uri_parameters={'scopeId': 'scopeId'})
        self.assertEqual(
            str(error.exception),
            "We have error with request."
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_search_no_results(self):
        """Check nsx_common.nsx_search func: no result"""
        self._regen_ctx()
        client_session = mock.Mock()

        # no results
        client_session.read = mock.Mock(return_value={
            'body': {}, 'status': 204
        })
        self.assertEqual(
            common.nsx_search(client_session, 'body/a', 'a', 'secret',
                              uri_parameters={'scopeId': 'scopeId'}),
            (None, None)
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_search_dict(self):
        """Check nsx_common.nsx_search func: dict_result"""
        self._regen_ctx()
        client_session = mock.Mock()

        # dict result
        client_session.read = mock.Mock(return_value={
            'body': {'a': {'name': 'b', 'objectId': 'c'}}, 'status': 204
        })
        self.assertEqual(
            common.nsx_search(client_session, 'body/a', 'b', 'secret',
                              uri_parameters={'scopeId': 'scopeId'}),
            ('c', {'name': 'b', 'objectId': 'c'})
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_search_list(self):
        """Check nsx_common.nsx_search func: list result"""
        self._regen_ctx()
        client_session = mock.Mock()

        # list result
        client_session.read = mock.Mock(return_value={
            'body': {'a': [{
                'name': 'b',
                'objectId': 'c'
            }, {
                'name': 'd',
                'objectId': 'e'
            }]}, 'status': 204
        })
        self.assertEqual(
            common.nsx_search(client_session, 'body/a', 'd', 'secret',
                              uri_parameters={'scopeId': 'scopeId'}),
            ('e', {'name': 'd', 'objectId': 'e'})
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_search_no_object(self):
        """Check nsx_common.nsx_search func: no object"""
        self._regen_ctx()
        client_session = mock.Mock()

        # object not exist
        client_session.read = mock.Mock(return_value={
            'body': {'a': [{
                'name': 'b',
                'objectId': 'c'
            }, {
                'name': 'd',
                'objectId': 'e'
            }]}, 'status': 204
        })
        self.assertEqual(
            common.nsx_search(client_session, 'body/a', 'g', 'secret',
                              uri_parameters={'scopeId': 'scopeId'}),
            (None, None)
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_struct_get_list_create(self):
        """Check nsx_common.nsx_struct_get_list func create"""

        # create
        nsx_object = {}
        self.assertEqual(
            common.nsx_struct_get_list(nsx_object, 'a/b/c'),
            []
        )
        self.assertEqual(
            nsx_object,
            {
                'a': {
                    'b': {
                        'c': [
                        ]
                    }
                }
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_struct_get_list_list(self):
        """Check nsx_common.nsx_struct_get_list func list"""

        # list by path
        nsx_object = {
            'a': {
                'b': [{
                    'c': 'd'
                }, {
                    'e': 'f'
                }]
            }
        }
        self.assertEqual(
            common.nsx_struct_get_list(nsx_object, 'a/b'),
            [{
                'c': 'd'
            }, {
                'e': 'f'
            }]
        )
        self.assertEqual(
            nsx_object,
            {
                'a': {
                    'b': [{
                        'c': 'd'
                    }, {
                        'e': 'f'
                    }]
                }
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_nsx_struct_get_list_dict2list(self):
        """Check nsx_common.nsx_struct_get_list func dict2list"""
        # convert dict to list
        nsx_object = {
            'a': {
                'b': {
                    'c': 'd'
                }
            }
        }
        self.assertEqual(
            common.nsx_struct_get_list(nsx_object, 'a/b'),
            [{
                'c': 'd'
            }]
        )
        self.assertEqual(
            nsx_object,
            {
                'a': {
                    'b': [{
                        'c': 'd'
                    }]
                }
            }
        )

    def test_delete_nsx_object_type(self):
        """Check delete properties after delete nsx object type"""
        self._regen_ctx()
        runtime_properties = self.fake_ctx.instance.runtime_properties
        runtime_properties['resource_id'] = 1
        runtime_properties['use_external_resource'] = 2
        runtime_properties['other'] = 3

        nsx_object_type.delete(ctx=self.fake_ctx, nsx_object={'a': 'b'})

        self.assertEqual(
            self.fake_ctx.instance.runtime_properties,
            {'other': 3}
        )

    def _test_nsx_object_type_common(self, func_kwargs, read_response=None,
                                     resource_id=None, read_all_response=None):
        fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
            None, func_kwargs
        )
        runtime_properties = self.fake_ctx.instance.runtime_properties
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            if read_response:
                fake_cs_result.read = mock.Mock(
                    return_value=copy.deepcopy(read_response)
                )

            if read_all_response:
                fake_cs_result.read_all_pages = mock.Mock(
                    return_value=copy.deepcopy(read_all_response)
                )

            nsx_object_type.create(**kwargs)

            self.assertEqual(
                runtime_properties['use_external_resource'],
                runtime_properties['resource_id'] is not None
            )

            self.assertEqual(
                runtime_properties['resource_id'], resource_id
            )

            if not read_response:
                # doesn't need read at all
                fake_cs_result.read.assert_not_called()

            if not read_all_response:
                # doesn't need read_all_pages at all
                fake_cs_result.read_all_pages.assert_not_called()

    def test_create_nsx_object_type_group_withresult(self):
        """Check nsx object create type: group exist"""
        self._test_nsx_object_type_common(
            {'nsx_object': {'name': 'name', 'type': 'group'}},
            {
                'status': 204,
                'body': test_nsx_base.SEC_GROUP_LIST
            },
            'id'
        )

    def test_create_nsx_object_type_group_withoutresult(self):
        """Check nsx object create type: group not found"""
        self._test_nsx_object_type_common(
            {'nsx_object': {'name': 'other', 'type': 'group'}},
            {
                'status': 204,
                'body': test_nsx_base.SEC_GROUP_LIST
            },
            None
        )

    def test_create_nsx_object_type_policy_withresult(self):
        """Check nsx object create type: policy exist"""
        self._test_nsx_object_type_common(
            {'nsx_object': {'name': 'name', 'type': 'policy'}},
            {
                'status': 204,
                'body': test_nsx_base.SEC_POLICY_LIST
            },
            'id'
        )

    def test_create_nsx_object_type_policy_withoutresult(self):
        """Check nsx object create type: policy not found"""
        self._test_nsx_object_type_common(
            {'nsx_object': {'name': 'other', 'type': 'policy'}},
            {
                'status': 204,
                'body': test_nsx_base.SEC_POLICY_LIST
            },
            None
        )

    def test_create_nsx_object_type_tag_withresult(self):
        """Check nsx object create type: tag exist"""
        self._test_nsx_object_type_common(
            {'nsx_object': {'name': 'name', 'type': 'tag'}},
            {
                'status': 204,
                'body': test_nsx_base.SEC_TAG_LIST
            },
            'id'
        )

    def test_create_nsx_object_type_tag_withoutresult(self):
        """Check nsx object create type: tag not found"""
        self._test_nsx_object_type_common(
            {'nsx_object': {'name': 'other', 'type': 'tag'}},
            {
                'status': 204,
                'body': test_nsx_base.SEC_TAG_LIST
            },
            None
        )

    def test_create_nsx_object_type_lswitch_withresult(self):
        """Check nsx object create type: lswitch exist"""
        self._test_nsx_object_type_common(
            {'nsx_object': {'name': 'name', 'type': 'lswitch'}},
            None,
            'id',
            test_nsx_base.LSWITCH_LIST
        )

    def test_create_nsx_object_type_lswitch_withoutresult(self):
        """Check nsx object create type: lswitch not found"""
        self._test_nsx_object_type_common(
            {'nsx_object': {'name': 'other', 'type': 'lswitch'}},
            None,
            None,
            test_nsx_base.LSWITCH_LIST
        )

if __name__ == '__main__':
    unittest.main()
