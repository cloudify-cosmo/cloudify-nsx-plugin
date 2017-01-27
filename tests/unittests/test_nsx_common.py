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
import cloudify_nsx.library.nsx_common as common


class NsxCommonTest(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
