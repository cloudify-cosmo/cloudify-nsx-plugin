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
from setuptools import setup

setup(
    name='cloudify-nsx-plugin',
    version='1.1',
    description='support vmware nsx',
    author='Denis Pauk',
    author_email='pauk.denis@gmail.com',
    license='LICENSE',
    packages=[
        'cloudify_nsx',
        'cloudify_nsx.library',
        'cloudify_nsx.network',
        'cloudify_nsx.security',
    ],
    package_data={
        'cloudify_nsx': [
            'library/api_spec/nsxvapi.raml',
            'library/api_spec/schemas/*',
            'library/api_spec/templates/documentation/introduction.md',
        ]
    },
    install_requires=[
        'PyYAML>=3.10',
        'cloudify-plugins-common>=3.3',
        'pynsxv==0.4.1',
    ],
)
