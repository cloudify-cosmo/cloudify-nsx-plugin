# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
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
import cloudify_nsx.library.nsx_common as common
from cloudify import exceptions as cfy_exc
from cloudify import mocks as cfy_mocks
from cloudify.state import current_ctx


class NsxCommonTest(unittest.TestCase):

    def setUp(self):
        super(NsxCommonTest, self).setUp()

    def _regen_ctx(self):
        self.fake_ctx = cfy_mocks.MockCloudifyContext()
        instance = mock.Mock()
        instance.runtime_properties = {}
        self.fake_ctx._instance = instance
        node = mock.Mock()
        self.fake_ctx._node = node
        node.properties = {}
        node.runtime_properties = {}
        current_ctx.set(self.fake_ctx)

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
    def test_validate(self):
        """Check nsx_common._validate func"""
        # empty
        self.assertEqual(
            common._validate({}, {}, False),
            {}
        )
        # default
        self.assertEqual(
            common._validate({}, {'a': {'default': 'd'}}, False),
            {'a': 'd'}
        )

        self.assertEqual(
            common._validate({'a': 'c'}, {'a': {'default': 'd'}}, False),
            {'a': 'c'}
        )

        # external
        with self.assertRaises(cfy_exc.NonRecoverableError):
            common._validate({}, {'a': {'external_use': True}}, True)

        self.assertEqual(
            common._validate({}, {'a': {'external_use': False}}, True),
            {'a': None}
        )

        # required
        with self.assertRaises(cfy_exc.NonRecoverableError):
            common._validate({}, {'a': {'required': True}}, False)

        # caseinsensitive
        self.assertEqual(
            common._validate(
                {'a': 'AbC'}, {'a': {'caseinsensitive': True}}, False
            ),
            {'a': 'abc'}
        )

        # values
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

        # set None
        self.assertEqual(
            common._validate(
                {}, {'a': {'set_none': True}}, False
            ),
            {'a': None}
        )

        # sub checks
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

        # boolean type
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

        # string type
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

        with self.assertRaises(cfy_exc.NonRecoverableError):
            common.check_raw_result({'status': 199})

        with self.assertRaises(cfy_exc.NonRecoverableError):
            common.check_raw_result({'status': 300})

    @pytest.mark.internal
    @pytest.mark.unit
    def test_remove_properties(self):
        """Check nsx_common.remove_properties func"""
        self._regen_ctx()
        self.fake_ctx.instance.runtime_properties['resource_id'] = '1'
        self.fake_ctx.instance.runtime_properties['resource'] = '2'
        self.fake_ctx.instance.runtime_properties['not_resource'] = '3'
        self.fake_ctx.instance.runtime_properties['nsx_auth'] = '4'
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
                raise need_error

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
    def test_nsx_login(self):
        """Check nsx_common.attempt_with_rerun func"""
        self._regen_ctx()

        fake_client = mock.MagicMock()
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            # no credentials
            with self.assertRaises(cfy_exc.NonRecoverableError):
                common.nsx_login({})
            fake_client.assert_not_called()

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
    def test_delete_object(self):
        """Check nsx_common.attempt_with_rerun func"""
        self._regen_ctx()

        # not fully created
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

        # check use existed
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

        # call with exception
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

        # good case
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


if __name__ == '__main__':
    unittest.main()
