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
import copy
from cloudify import mocks as cfy_mocks
from cloudify import exceptions as cfy_exc
from cloudify.state import current_ctx


SUCCESS_RESPONSE = {
    'status': 204,
    'body': {}
}

SUCCESS_RESPONSE_ID = {
    'status': 204,
    'body': {},
    'objectId': 'id'
}

SEC_GROUP_LIST = {
    'list': {
        'securitygroup': {
            'name': 'name',
            'objectId': 'id'
        }
    }
}

SEC_GROUP_EXCLUDE_BEFORE = {
    'securitygroup': {
        'excludeMember': [{
            "objectId": "other_objectId",
        }],
        'name': 'some_name'
    }
}

SEC_GROUP_EXCLUDE_AFTER = {
    'securitygroup': {
        'excludeMember': [{
            'objectId': 'other_objectId'
        }, {
            'objectId': 'member_id'
        }],
        'name': 'some_name'
    }
}

SEC_GROUP_POLICY_BIND_BEFORE = {
    'securityPolicy': {
        'securityGroupBinding': [{
            'objectId': 'other'
        }],
        'name': 'name'
    }
}

SEC_GROUP_POLICY_BIND_AFTER = {
    'securityPolicy': {
        'securityGroupBinding': [{
            'objectId': 'other'
        }, {
            'objectId': 'security_group_id'
        }],
        'name': 'name'
    }
}

SEC_POLICY_LIST = {
    'securityPolicies': {
        'securityPolicy': {
            'name': 'name',
            'objectId': 'id',
            'description': 'description',
            'precedence': 'precedence',
            'parent': None,
            'securityGroupBinding': None,
            'actionsByCategory': None
        }
    }
}

SEC_POLICY_SECTION_BEFORE = {
    'securityPolicy': {
        'actionsByCategory': [{
            "category": "other_category",
            "action": "other_action"
        }]
    }
}

SEC_POLICY_SECTION_AFTER = {
    'securityPolicy': {
        'actionsByCategory': [{
            "category": "other_category",
            "action": "other_action"
        }, {
            "category": "category",
            "action": "action"
        }]
    }
}

SEC_POLICY_SECTION_OVERWRITE = {
    'securityPolicy': {
        'actionsByCategory': [{
            "category": "other_category",
            "action": "action"
        }]
    }
}

SEC_TAG_LIST = {
    'securityTags': {
        'securityTag': {
            'name': 'name',
            'objectId': 'id'
        }
    }
}

LSWITCH = {
    'virtualWire': {
        'name': 'name',
        'objectId': 'id',
        'vdsContextWithBacking': {
            'backingValue': "some_port_id"
        }
    }
}

LSWITCH_LIST = [{
    'name': 'name',
    'objectId': 'id',
    'vdsContextWithBacking': {
        'backingValue': "some_port_id"
    }
}]

EDGE_LIST = [{
    'name': 'name',
    'objectId': 'id'
}]


class NSXBaseTest(unittest.TestCase):

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

    def _regen_relationship_ctx(self):
        # source
        source_instance = mock.Mock()
        source_instance.runtime_properties = {}
        source = cfy_mocks.MockCloudifyContext()
        source._instance = source_instance
        # target
        target_instance = mock.Mock()
        target_instance.runtime_properties = {}
        target = cfy_mocks.MockCloudifyContext()
        target._instance = target_instance
        # create context
        self.fake_ctx = cfy_mocks.MockCloudifyContext(
            target=target,
            source=source
        )
        current_ctx.set(self.fake_ctx)

    def _kwargs_regen(self, func_kwargs, node_context=True):
        if node_context:
            self._regen_ctx()
        else:
            self._regen_relationship_ctx()
        kwargs = {v: func_kwargs[v] for v in func_kwargs}
        kwargs['ctx'] = self.fake_ctx
        return kwargs

    def _common_uninstall_external_and_unintialized(
        self, resource_id, func_call, func_kwargs, additional_params=None
    ):
        """common function with any call from clint_session"""
        # not fully created
        kwargs = self._kwargs_regen(func_kwargs)
        self.fake_ctx.instance.runtime_properties['resource_id'] = None
        if additional_params:
            for i in additional_params:
                self.fake_ctx.instance.runtime_properties[i] = i
        func_call(**kwargs)
        self.assertEqual(self.fake_ctx.instance.runtime_properties, {})

        # check use existed
        kwargs = self._kwargs_regen(func_kwargs)
        self.fake_ctx.instance.runtime_properties['resource_id'] = resource_id
        self.fake_ctx.node.properties['use_external_resource'] = True
        if additional_params:
            for i in additional_params:
                self.fake_ctx.instance.runtime_properties[i] = i
        func_call(**kwargs)
        self.assertEqual(self.fake_ctx.instance.runtime_properties, {})

        # wrong count of | in resource_id
        if resource_id.find('|') >= 0:
            new_resource_id = resource_id + "|_"
            fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
                new_resource_id, func_kwargs
            )
            with mock.patch(
                'cloudify_nsx.library.nsx_common.NsxClient',
                fake_client
            ):
                with self.assertRaises(cfy_exc.NonRecoverableError) as error:
                    func_call(**kwargs)

                self.assertTrue(str(error.exception).find(
                    'Unexpected error retrieving resource ID'
                ) == 0)

        # delete check with exeption
        fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
            resource_id, func_kwargs
        )
        if additional_params:
            for i in additional_params:
                self.fake_ctx.instance.runtime_properties[i] = i
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):

            with self.assertRaises(cfy_exc.NonRecoverableError):
                func_call(**kwargs)

            fake_client.assert_called_with(
                'raml', 'host', 'username', 'password'
            )
            runtime = self.fake_ctx.instance.runtime_properties
            self.assertEqual(runtime['resource_id'], resource_id)
            self.assertEqual(
                runtime['nsx_auth'], {
                    'username': 'username',
                    'password': 'password',
                    'host': 'host',
                    'raml': 'raml'
                }
            )
            if additional_params:
                for i in additional_params:
                    self.assertEqual(runtime.get(i), i)

    def _kwargs_regen_client(self, resource_id, func_kwargs,
                             node_context=True):
        kwargs = self._kwargs_regen(func_kwargs, node_context)
        if node_context:
            runtime = self.fake_ctx.instance.runtime_properties
        else:
            runtime = self.fake_ctx.target.instance.runtime_properties

        if resource_id:
            runtime['resource_id'] = resource_id

        kwargs['nsx_auth'] = {
            'username': 'username',
            'password': 'password',
            'host': 'host',
            'raml': 'raml'
        }

        fake_cs_result = mock.Mock()
        fake_client = mock.MagicMock(return_value=fake_cs_result)

        fake_cs_result.create = mock.Mock(
            side_effect=cfy_exc.NonRecoverableError()
        )

        fake_cs_result.delete = mock.Mock(
            side_effect=cfy_exc.NonRecoverableError()
        )

        fake_cs_result.read = mock.Mock(
            side_effect=cfy_exc.NonRecoverableError()
        )

        fake_cs_result.read_all_pages = mock.Mock(
            side_effect=cfy_exc.NonRecoverableError()
        )

        fake_cs_result.update = mock.Mock(
            side_effect=cfy_exc.NonRecoverableError()
        )

        fake_cs_result.extract_resource_body_example = mock.Mock(
            side_effect=cfy_exc.NonRecoverableError()
        )

        return fake_client, fake_cs_result, kwargs

    def _common_run_relationship(self, func):
        """check that we have RecoverableError with empty properties"""
        fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
            None, {}, False
        )
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            with self.assertRaises(cfy_exc.RecoverableError):
                func(**kwargs)

    def _common_run_relationship_read_update(
        self, func, source_properties=None, target_properties=None,
        read_args=None, read_kwargs=None, read_response=None,
        update_args=None, update_kwargs=None, update_response=None
    ):

        self._common_run_relationship(func)

        # regen
        fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
            None, {}, False
        )

        # properties
        if source_properties:
            self.fake_ctx.source.instance.runtime_properties.update(
                source_properties
            )

        if target_properties:
            self.fake_ctx.target.instance.runtime_properties.update(
                target_properties
            )

        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            self._update_fake_cs_result(
                fake_cs_result,
                # read
                read_response=read_response,
                # update
                update_response=update_response
            )

            func(**kwargs)

            self._check_fake_cs_result(
                fake_cs_result,
                # read
                read_response=read_response,
                read_args=read_args, read_kwargs=read_kwargs,
                # update
                update_response=update_response,
                update_args=update_args, update_kwargs=update_kwargs
            )

    def _common_install(self, resource_id, func_call, func_kwargs):
        """Check skip install logic if we have resource_id
           or have issues with session"""
        # check already existed
        kwargs = self._kwargs_regen(func_kwargs)
        self.fake_ctx.instance.runtime_properties['resource_id'] = resource_id
        func_call(**kwargs)

        # try to create but have issue with session connection
        fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
            None, func_kwargs
        )
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):

            with self.assertRaises(cfy_exc.NonRecoverableError):
                func_call(**kwargs)

            fake_client.assert_called_with(
                'raml', 'host', 'username', 'password'
            )
            runtime = self.fake_ctx.instance.runtime_properties
            self.assertFalse('resource_id' in runtime)
            self.assertEqual(
                runtime['nsx_auth'], {
                    'username': 'username',
                    'password': 'password',
                    'host': 'host',
                    'raml': 'raml'
                }
            )

    def _update_fake_cs_result(
        self, fake_cs_result,
        extract_response=None, read_response=None, update_response=None
    ):
        """Set correct responses to calls"""
        if extract_response:
            fake_cs_result.extract_resource_body_example = mock.Mock(
                return_value=copy.deepcopy(extract_response)
            )

        if read_response:
            fake_cs_result.read = mock.Mock(
                return_value=copy.deepcopy(read_response)
            )

        if update_response:
            fake_cs_result.update = mock.Mock(
                return_value=copy.deepcopy(update_response)
            )

    def _check_fake_cs_result(
        self, fake_cs_result,
        extract_response=None, extract_args=None, extract_kwargs=None,
        read_response=None, read_args=None, read_kwargs=None,
        update_response=None, update_args=None, update_kwargs=None
    ):
        """Check that correct calls called"""
        if not extract_response:
            # doesn't need extract at all
            fake_cs_result.extract_resource_body_example.\
                assert_not_called()
        else:
            fake_cs_result.extract_resource_body_example.\
                assert_called_with(
                    *extract_args, **extract_kwargs
                )

        if not read_response:
            # doesn't need read at all
            fake_cs_result.read.assert_not_called()
        else:
            fake_cs_result.read.assert_called_with(
                *read_args, **read_kwargs
            )

        if not update_response:
            # doesn't need update at all
            fake_cs_result.update.assert_not_called()
        else:
            fake_cs_result.update.assert_called_with(
                *update_args, **update_kwargs
            )

    def _common_install_extract_or_read_and_update(
        self, resource_id, func_call, func_kwargs,
        extract_args=None, extract_kwargs=None, extract_response=None,
        read_args=None, read_kwargs=None, read_response=None,
        update_args=None, update_kwargs=None, update_response=None
    ):
        """check install logic that read/extract current state and than send
           update request"""
        self._common_install(resource_id, func_call, func_kwargs)

        fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
            None, func_kwargs
        )
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            self._update_fake_cs_result(
                fake_cs_result,
                extract_response=extract_response,
                read_response=read_response,
                update_response=update_response
            )

            func_call(**kwargs)

            self._check_fake_cs_result(
                fake_cs_result,
                # extract
                extract_response=extract_response,
                extract_args=extract_args, extract_kwargs=extract_kwargs,
                # read
                read_response=read_response,
                read_args=read_args, read_kwargs=read_kwargs,
                # update
                update_response=update_response,
                update_args=update_args, update_kwargs=update_kwargs
            )

            runtime = self.fake_ctx.instance.runtime_properties
            self.assertEqual(
                runtime['resource_id'],
                resource_id
            )

    def _common_install_read_and_create(
        self, resource_id, func_call, func_kwargs, read_args, read_kwargs,
        read_response, create_args, create_kwargs, create_response,
        recheck_runtime=None
    ):
        """check install logic that check 'existing' by read
           and than run create"""
        self._common_install(resource_id, func_call, func_kwargs)

        # use custom response
        if read_response:
            # use existed
            fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
                None, func_kwargs
            )
            self.fake_ctx.node.properties['use_external_resource'] = True
            with mock.patch(
                'cloudify_nsx.library.nsx_common.NsxClient',
                fake_client
            ):

                fake_cs_result.read = mock.Mock(
                    return_value=copy.deepcopy(read_response)
                )
                func_call(**kwargs)

                fake_cs_result.read.assert_called_with(
                    *read_args, **read_kwargs
                )
                runtime = self.fake_ctx.instance.runtime_properties
                self.assertEqual(
                    runtime['resource_id'], resource_id
                )
                if recheck_runtime:
                    for field in recheck_runtime:
                        self.assertEqual(
                            runtime[field],
                            recheck_runtime[field]
                        )

            # use existed, but empty response
            fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
                None, func_kwargs
            )
            self.fake_ctx.node.properties['use_external_resource'] = True
            with mock.patch(
                'cloudify_nsx.library.nsx_common.NsxClient',
                fake_client
            ):

                fake_cs_result.read = mock.Mock(
                    return_value=copy.deepcopy(SUCCESS_RESPONSE)
                )
                with self.assertRaises(cfy_exc.NonRecoverableError):
                    func_call(**kwargs)

                fake_cs_result.create.assert_not_called()

                fake_cs_result.read.assert_called_with(
                    *read_args, **read_kwargs
                )
                self.assertFalse(
                    'resource_id' in self.fake_ctx.instance.runtime_properties
                )

            # preexist (use_external_resource=False)
            fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
                None, func_kwargs
            )
            with mock.patch(
                'cloudify_nsx.library.nsx_common.NsxClient',
                fake_client
            ):
                fake_cs_result.read = mock.Mock(
                    return_value=copy.deepcopy(read_response)
                )

                with self.assertRaises(cfy_exc.NonRecoverableError):
                    func_call(**kwargs)

                fake_cs_result.read.assert_called_with(
                    *read_args, **read_kwargs
                )
                self.assertFalse(
                    'resource_id' in self.fake_ctx.instance.runtime_properties
                )

        # create use_external_resource=False
        fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
            None, func_kwargs
        )
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            fake_cs_result.read = mock.Mock(
                return_value=copy.deepcopy(SUCCESS_RESPONSE)
            )
            fake_cs_result.create = mock.Mock(
                return_value=copy.deepcopy(create_response)
            )
            func_call(**kwargs)

            fake_cs_result.read.assert_called_with(
                *read_args, **read_kwargs
            )
            fake_cs_result.create.assert_called_with(
                *create_args, **create_kwargs
            )
            runtime = self.fake_ctx.instance.runtime_properties
            self.assertEqual(
                runtime['resource_id'],
                resource_id
            )

    def _common_uninstall_delete(
        self, resource_id, func_call, func_kwargs, delete_args, delete_kwargs,
        additional_params=None, read_args=None, read_kwargs=None,
        read_response=None
    ):
        """for functions when we only run delete directly"""
        self._common_uninstall_external_and_unintialized(
            resource_id, func_call, func_kwargs,
            additional_params=additional_params
        )

        # delete without exeption
        fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
            resource_id, func_kwargs
        )
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            if read_response:
                fake_cs_result.read = mock.Mock(
                    return_value=copy.deepcopy(read_response)
                )

            fake_cs_result.delete = mock.Mock(
                return_value=copy.deepcopy(SUCCESS_RESPONSE)
            )
            func_call(**kwargs)

            fake_cs_result.delete.assert_called_with(
                *delete_args, **delete_kwargs
            )

            if not read_response:
                # doesn't need read at all
                fake_cs_result.read.assert_not_called()
            else:
                fake_cs_result.read.assert_called_with(
                    *read_args, **read_kwargs
                )

            self.assertEqual(self.fake_ctx.instance.runtime_properties, {})

    def _common_uninstall_read_update(
        self, resource_id, func_call, func_kwargs, read_args, read_kwargs,
        read_response, update_args, update_kwargs, additional_params=None
    ):
        """delete when read/update enought"""
        self._common_uninstall_external_and_unintialized(
            resource_id, func_call, func_kwargs,
            additional_params=additional_params
        )

        # delete without exeption
        fake_client, fake_cs_result, kwargs = self._kwargs_regen_client(
            resource_id, func_kwargs
        )
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            fake_client
        ):
            # use custom response
            if read_response:
                fake_cs_result.read = mock.Mock(
                    return_value=copy.deepcopy(read_response)
                )

            fake_cs_result.update = mock.Mock(
                return_value=copy.deepcopy(SUCCESS_RESPONSE)
            )
            func_call(**kwargs)
            fake_cs_result.read.assert_called_with(
                *read_args, **read_kwargs
            )
            fake_cs_result.update.assert_called_with(
                *update_args, **update_kwargs
            )
            self.assertEqual(self.fake_ctx.instance.runtime_properties, {})

    def _prepare_check(self, read_response=None, update_response=None):
        "prepare responses for read and update"
        client_session = mock.Mock()
        if read_response:
            client_session.read = mock.Mock(
                return_value=copy.deepcopy(read_response)
            )
        else:
            client_session.read = mock.Mock(
                return_value=copy.deepcopy(SUCCESS_RESPONSE)
            )

        if update_response:
            client_session.update = mock.Mock(
                return_value=copy.deepcopy(update_response)
            )
        else:
            client_session.update = mock.Mock(
                return_value=copy.deepcopy(SUCCESS_RESPONSE)
            )

        return client_session
