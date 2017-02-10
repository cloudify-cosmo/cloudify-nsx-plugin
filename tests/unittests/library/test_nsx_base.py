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


class NSXBaseTest(unittest.TestCase):

    def _prepare_check(self, read=None, update=None):
        "prepare responses for read and update"
        client_session = mock.Mock()
        if read:
            client_session.read = mock.Mock(
                return_value=read
            )
        else:
            client_session.read = mock.Mock(
                return_value={
                    'status': 204
                }
            )

        if update:
            client_session.update = mock.Mock(
                return_value=update
            )
        else:
            client_session.update = mock.Mock(
                return_value={
                    'status': 204
                }
            )

        return client_session
