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


if __name__ == '__main__':
    unittest.main()