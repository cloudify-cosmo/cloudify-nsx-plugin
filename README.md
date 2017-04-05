# cloudify-nsx-plugin
Cloudify Network Virtualization with VMware (NSX) plugin

# Common Documentation

# Description

The VMWare NSX plugin allows users to use a vCenter NSX based infrastructure for deploying services (both network and security) and applications.

# Plugin Requirements

* Python versions:
    * 2.7.x
* VMWare versions:
    * NSX >= 6.2.3
    * vSphere >= 6.0.0

## NSX Environment

* You will require a working vSphere and vCenter environment with installed NSX. The plugin was tested with version NSX 6.2.3.
If you want to use network functionality - also required to use vSphere plugin 2.3.0+ version.

# Types

Each type has property `nsx_auth`. It can be used to pass parameters for authenticating.

## nsx_auth:

Provides structure with credentials for authenticating in NSX.

* `username`: user name for NSX
* `password`: user password for nsx
* `host`: nsx host
* `raml`: optional, path to raml file, if not defined will be used embedded version from plugin.

You can provide all properties described in node also as inputs for workflow action.
E.g. if you don’t have nsx_auth as static properties values or can't provide it as inputs of blueprint,
you also can use get_attributes call in place value in workflow input.

```
    node_templates:
      security_policy:
        type: cloudify.nsx.security_policy
        properties:
          nsx_auth: <authentication credentials for nsx>
             ....
        interfaces:
          cloudify.interfaces.lifecycle:
            create:
              inputs:
                nsx_auth: <place for optional overwrite nsx_auth>
                  ...
```

General rules for properties - the plugin always merges properties and inputs,
and will be overwritten by any existing runtime properties.

Such structure:

```
    node_templates:
      security_policy:
        type: cloudify.nsx.security_policy
        properties:
          nsx_auth:
             username: nsx_user
        interfaces:
          cloudify.interfaces.lifecycle:
            create:
              inputs:
                nsx_auth:
                  password: nsx_secret
                  host: nsx_host
```

will produce such in runtime properties and will be used for login to NSX:

```
    runtime_properties:
      nsx_auth:
        username: nsx_user
        password: nsx_secret
        host: nsx_host
```

As result in you can provide nsx_auth only once in create and in delete action values will be reused without explicit provide such.

Advanced properties are defined in [nsx pdf](https://pubs.vmware.com/NSX-62/topic/com.vmware.ICbase/PDF/nsx_62_api.pdf).

## resource_id

Each node type that has direct mapping to NSX objects, has `resource_id` property
(in node properties as input and in runtime_properties as store of such)
and contain NSX internal id. Please, be careful its not `name` of object.

E.g:
* `group` has something like: `securitygroup-426`.
* `policy` has something like: `policy-108`.
* `tag` has something like: `securitytag-143`.
* `vcenter vm id` has something like: `vm-438`.

### use_external_resource

Each node type that has direct mapping to NSX objects, has `use_external_resource` property
(in node properties as input and in runtime_properties as store of such) and
save as flag that plugin has reused external resource.

## Security related functionality
### cloudify.nsx.security_group

A security group is a collection of assets or grouping objects from your vSphere inventory.

**Derived From:** cloudify.nodes.ApplicationServer

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `use_external_resource`: optional, use external object, by default false.
* `resource_id`: optional, [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is true.
* `group`: properties for group.
    * `scopeId`: Scope ID (by default: `globalroot‐0`) or datacenterId or portgroupId in upgrade use cases.
    * `name`: Object name.
    * `member`: optional, list of members, also can be updated as [cloudify.nsx.security_group_member](README.md#cloudifynsxsecurity_group_member) node.
    * `excludeMember`: optional, list of excluded members, , also can be updated as [cloudify.nsx.security_group_exclude_member](README.md#cloudifynsxsecurity_group_exclude_member) node.
    * `dynamicMemberDefinition`: optional, list of rules for attach new members, , also can be updated as [cloudify.nsx.security_group_dynamic_member](README.md#cloudifynsxsecurity_group_dynamic_member) node.

**Runtime properties:**
* `nsx_auth`: merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: merged copy of `use_external_resource`.
* `resource_id`: merged copy of `resource_id` if use_external_resource or [id](README.md#resource_id) of newly created object.
* `group`: merged copy of `group`.

**Examples:**

```
  master_security_group:
    type: cloudify.nsx.security_group
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            group:
              name: <some name>
              member:
                objectId: <child id>
```

* [Simple example](tests/platformtests/resources/security_groups.yaml#L86) with one static child:

* For more complicated example look to [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

### cloudify.nsx.security_group_dynamic_member

Partially update [Security Group](README.md#cloudifynsxsecurity_group) with new dynamic members rules.

**Derived From:** cloudify.nodes.ApplicationModule

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `dynamic_member`:
    * `dynamic_set`: represents a rule set as represented on the UI. There can be multiple dynamic sets inside dynamic member definition.
    * `security_group_id`: `resource_id` from parent [security group](README.md#cloudifynsxsecurity_group).

**Runtime properties:**
* `nsx_auth`: merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal id used in plugin for work with `dynamic_set`.
* `dynamic_member`: merged copy of `dynamic_member`.

**Examples:**

```
  update_dynamic_members:
    type: cloudify.nsx.security_group_dynamic_member
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            dynamic_member:
              security_group_id: <security group id>
              dynamic_set:
                - operator: OR
                  dynamicCriteria:
                    operator: AND
                    isValid: true
                    key: VM.GUEST_OS_FULL_NAME
                    value: Server
                    criteria: contains
                - operator: OR
                  dynamicCriteria:
                    operator: AND
                    isValid: true
                    key: VM.GUEST_OS_FULL_NAME
                    value: Teapot
                    criteria: contains
```
* [Simple example](tests/platformtests/resources/security_groups.yaml):
* For more complicated example look to [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

### cloudify.nsx.security_group_member

Attach member to [Security Group](README.md#cloudifynsxsecurity_group).

**Derived From:** cloudify.nodes.ApplicationModule
**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `group_member`:
    * `objectId`: member id, can be other security group or [vm](README.md#resource_id).
    * `security_group_id`: `resource_id` from parent [security group](README.md#cloudifynsxsecurity_group).

**Runtime properties:**
* `nsx_auth`: merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal id used in plugin for work with `group_member`.
* `group_member`: merged copy of `group_member`.

**Examples:**

```
  slave_master_security_group_bind:
    type: cloudify.nsx.security_group_member
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            group_member:
              security_group_id: <security group id>
              objectId: <object Id>
```

* [Simple example](tests/platformtests/resources/security_groups.yaml):
* For more complicated example look to [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

### cloudify.nsx.security_group_exclude_member

Set some object as explicitly excluded from [Security Group](README.md#cloudifynsxsecurity_group).

**Derived From:** cloudify.nodes.ApplicationModule
**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `group_exclude_member`:
    * `objectId`: member id, can be other security group or [vm](README.md#resource_id).
    * `security_group_id`: `resource_id` from parent [security group](README.md#cloudifynsxsecurity_group).

**Runtime properties:**
* `nsx_auth`: merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal id used in plugin for work with `group_exclude_member`.
* `group_exclude_member`: merged copy of `group_exclude_member`.

**Examples:**

```
  slave_master_security_group_bind:
    type: cloudify.nsx.security_group_exclude_member
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            group_exclude_member:
              security_group_id: <security group id>
              objectId: <object Id>
```

* [Simple example](tests/platformtests/resources/security_groups.yaml):
* For more complicated example look to [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

### cloudify.nsx.security_policy

A [security policy](README.md#cloudifynsxsecurity_policy) is a set of endpoint, firewall
and network introspection services that can be applied to a [security group](README.md#cloudifynsxsecurity_group).
When creating a security policy, a parent security policy can be specified if required. The security policy inherits
services from the parent security policy. [Security group](README.md#cloudifynsxsecurity_group) bindings and actions
can also be specified while creating the policy. Note that execution order of actions in a category
is implied by their order in the list.

**Derived From:** cloudify.nodes.ApplicationServer

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `use_external_resource`: optional, use external object, by default false.
* `resource_id`: optional, [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is true.
* `policy`:
    * `name`: name of security policy.
    * `description`: optional, short description for policy.
    * `precedence`: Sort order, place in list.
    * `parent`: optional, parent security policy.
    * `securityGroupBinding`: List of security groups, also can be updated as [separate node](README.md#cloudifynsxsecurity_policy_group_bind).
    * `actionsByCategory` : list of actions by category, also can be updated as [separate node](README.md#cloudifynsxsecurity_policy_section).

**Runtime properties:**
* `nsx_auth`: merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: merged copy of `use_external_resource`.
* `resource_id`: merged copy of `resource_id` if use_external_resource or [id](README.md#resource_id) of newly created object.
* `policy`: merged copy of `policy`.

**Examples:**

```
  security_policy:
    type: cloudify.nsx.security_policy
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            policy:
              name: <policy name>
              description: "Policy description"
              precedence: 6301
              actionsByCategory:
                category: firewall
                action:
                  '@class': firewallSecurityAction
                  name: "Reject all"
                  description: "Reject all description"
                  category: firewall
                  action: reject
                  direction: inbound
                  isEnabled: "true" # Boolean should be in quotes, type: string

```

* [Simple example](tests/platformtests/resources/security_policy.yaml):
* For more complicated example look to [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

### cloudify.nsx.security_policy_group_bind

Bind [security group](README.md#cloudifynsxsecurity_group) to [security policy](README.md#cloudifynsxsecurity_policy).

**Derived From:** cloudify.nodes.ApplicationModule

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `policy_group_bind`:
    * `security_policy_id`: `resource_id` from [security policy](README.md#cloudifynsxsecurity_policy).
    * `security_group_id`: `resource_id` from [security group](README.md#cloudifynsxsecurity_group).

**Runtime properties:**
* `nsx_auth`: merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal id used in plugin for work with `policy_group_bind`.
* `policy_group_bind`: merged copy of `policy_group_bind`.

**Examples:**

```

  master_security_policy_bind:
    type: cloudify.nsx.security_policy_group_bind
    properties:
      nsx_auth:  <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            policy_group_bind:
              security_policy_id: <Security policy id>
              security_group_id: <Security group id>
```

* [Simple example](tests/platformtests/resources/bind_policy_group.yaml):
* For more complicated example look to [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

### cloudify.nsx.security_policy_section

Update section in [security policy](README.md#cloudifynsxsecurity_policy).
If such section already exit - section will be replaced, otherwise inserted.

**Derived From:** cloudify.nodes.ApplicationModule

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `policy_section`:
    * `security_policy_id`: `resource_id` from [security policy](README.md#cloudifynsxsecurity_policy).
    * `category`: category name.
    * `action`: action structure, list of fields depends on category, look to [nsx pdf](https://pubs.vmware.com/NSX-62/topic/com.vmware.ICbase/PDF/nsx_62_api.pdf) for full list.

**Runtime properties:**
* `nsx_auth`: merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal id used in plugin for work with `policy_section`.
* `policy_section`: merged copy of `policy_section`.

**Examples:**

```
  update_security_policy:
    type: cloudify.nsx.security_policy_section
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            policy_section:
              security_policy_id: <Security policy id>
              category: endpoint
              action:
                '@class': endpointSecurityAction
                name: "intro_service"
                description: "Intro description"
                category: endpoint
                actionType: ANTI_VIRUS
                isEnabled: "true"
                isActionEnforced: "false"
```

* [Simple example](tests/platformtests/resources/security_policy.yaml):
* For more complicated example look to [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

### cloudify.nsx.security_tag

Security Tag.

**Derived From:** cloudify.nodes.ApplicationServer

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `use_external_resource`: optional, use external object, by default false.
* `resource_id`: optional, [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is true.
* `tag`:
    * `name`: security tag name.
    * `description`: security tag description.

**Runtime properties:**
* `nsx_auth`: merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: merged copy of `use_external_resource`.
* `resource_id`: merged copy of `resource_id` if use_external_resource or [id](README.md#resource_id) of newly created object.
* `tag`: merged copy of `tag`.

**Examples:**

```
  security_tag:
    type: cloudify.nsx.security_tag
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            tag:
              name: Secret tag name
              description: What can i say?

```

* [Simple example](tests/platformtests/resources/security_tag.yaml):
* For more complicated example look to [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

**Relationships**

#### cloudify.nsx.relationships.attach_tag

You can use `attach_tag` for attach tag to several vm's without separate node for [each](README.md#cloudifynsxsecurity_tag_vm).

```

  security_tag:
    type: cloudify.nsx.security_tag
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            tag:
              name: Secret tag name
              description: What can i say?

  vsphere_vm_link:
    type: cloudify.vsphere.nodes.Server
    properties:
      connection_config: *connection_config
      server:
        name: several_servers
        template: <template_name>
        cpus: 1
        memory: 256
      agent_config:
        install_method: none
    # can be used only with 'attach_tag' relationship
    instances:
      deploy: 2
    relationships:
      - type: cloudify.nsx.relationships.attach_tag
        target: security_tag

```

### cloudify.nsx.security_tag_vm

Apply [security tag](README.md#cloudifynsxsecurity_tag) to vm.

**Derived From:** cloudify.nodes.ApplicationModule

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `vm_tag`:
    * `tag_id`: security tag id.
    * `vm_id`: vCenter/vSphere vm id.

**Runtime properties:**
* `nsx_auth`: merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal id used in plugin for work with `vm_tag`.
* `vm_tag`: merged copy of `vm_tag`.

**Examples:**

```
  tag_vm:
    type: cloudify.nsx.security_tag_vm
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            vm_tag:
              tag_id: <security tag id>
              vm_id: <vsphere server id>
```

* For more complicated example look to [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

## Network related functionality

### cloudify.nsx.lswitch

Logical switches

**Derived From:** cloudify.nodes.Network

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `use_external_resource`: optional, use external object, by default false.
* `resource_id`: optional, [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is true.
* `switch`:
  * `transport_zone`: The name of the Scope (Transport Zone).
  * `name`: The name that will be assigned to the new logical switch.
  * `mode`: Optional, control Plane Mode, uses the Transport Zone default if not specified.

**Runtime properties:**
* `nsx_auth`: merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: merged copy of `use_external_resource`.
* `resource_id`: merged copy of `resource_id` if use_external_resource or [id](README.md#resource_id) of newly created object.
* `switch`: merged copy of `switch`.
* `vsphere_network_id`: Network id in vSphere.

**Examples:**

```
  slave_lswitch:
    type: cloudify.nsx.lswitch
    properties:
      nsx_auth: <authentication credentials for nsx>
      switch:
        name:slave_switch
        transport_zone: Main_Zone
        # UNICAST_MODE, MULTYCAST_MODE, HYBRID_MODE
        mode: UNICAST_MODE
```

## Common/supplementary functionality

### cloudify.nsx.nsx_object

NSX object check. Search nsx object and set in runtime properties `resource_id` for such object and `use_external_resource` if object can be used as external resource.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `nsx_object`:
    * `name`: name of nsx object to existing check.
    * `type`: type of object, can be: [tag](README.md#cloudifynsxsecurity_tag), [policy](README.md#cloudifynsxsecurity_policy) and [group](README.md#cloudifynsxsecurity_group) or [lswitch](README.md#cloudifynsxlswitch).
    * `scopeId`: optional, object scope, make sense for group search, be default: `globalroot-0`.


**Runtime properties:**
* `nsx_auth`: merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Exteranl resource id if object can be used as external, otherwise `None`.
* `use_external_resource`: `True`, if we can reuse object.

**Examples:**

Create tag only in case when we don't have such.

```
  tag_check:
    type: cloudify.nsx.nsx_object
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            nsx_object:
              name: Secret tag name
              type: tag

  security_tag:
    type: cloudify.nsx.security_tag
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            use_external_resource: { get_attribute: [ tag_check, use_external_resource ] }
            resource_id: { get_attribute: [ tag_check, resource_id ] }
            tag:
              name: Secret tag name
              description: What can i say?
    relationships:
      - type: cloudify.relationships.depends_on
        target: tag_check
```

* For more complicated example look to [esg_with_ospf_functionality.yaml](tests/integration/resources/esg_with_ospf_functionality.yaml).

# Infrastructure tests before deployments
## Check platform example
### Linux example

#### get plugin codebase

```
git clone https://github.com/cloudify-cosmo/cloudify-nsx-plugin.git
```

#### Install plugin locally

```
pip install -e cloudify-nsx-plugin/
pip install -r cloudify-nsx-plugin/test-requirements.txt
```

#### Inputs for platform tests

```
export NSX_IP="<nsx_ip>"
export NSX_USER="<nsx_user>"
export NSX_PASSWORD="<nsx_password>"
export NODE_NAME_PREFIX="<some_free_prefix_for_objects>"
```

#### Cleanup previous results

```
rm .coverage -rf
```

#### Check state

```
nosetests -v --with-coverage --cover-package=cloudify_nsx cloudify-nsx-plugin/tests/platformtests/ cloudify-nsx-plugin/tests/unittests/
```

### Windows example
Before run the test script next programs and components should be installed:
 * Python 2.7.9
 * VCForPython27.msi (```http://aka.ms/vcpython27```)

Example of test script is located in folder: ```tests/platformtests/windows_example.ps1```

## Check total coverage and full functionality
### Get plugin codebase

```
git clone https://github.com/cloudify-cosmo/cloudify-nsx-plugin.git
git clone https://github.com/cloudify-cosmo/cloudify-vsphere-plugin.git
```

### Install plugin localy

```
pip install -e cloudify-nsx-plugin/
pip install -r cloudify-nsx-plugin/test-requirements.txt

cd cloudify-vsphere-plugin/ && git checkout 2.3.0-m1 && cd ..
pip install -e cloudify-vsphere-plugin/
pip install -r cloudify-vsphere-plugin/test-requirements.txt
```

### Inputs for platform tests
#### NSX

```
export NSX_IP="<nsx_ip>"
export NSX_USER="<nsx_user>"
export NSX_PASSWORD="<nsx_password>"
```

#### VCENTER

```
export VCENTER_IP="<vcenter_ip>"
export VCENTER_USER="<vcenter_user>"
export VCENTER_PASSWORD="<vcenter_password>"
```

#### Optional vCenter for network checks support

```
export VCENTER_DATASTORE="<vcenter_datastore>"
export VCENTER_DATACENTER="<vcenter_datacenter>"
export VCENTER_TEMPLATE="<vcenter_linux_template>"
export VCENTER_CLUSTER="<vcenter_cluster>"
export VCENTER_RESOURCE_POOL="<vcenter_resource_pool>"
```

#### Prefixes

```
export NODE_NAME_PREFIX="<some_free_prefix_for_objects>"
```

### Cleanup previous results

```
rm .coverage -rf
```

### Check state

```
nosetests -v --with-coverage --cover-package=cloudify_nsx cloudify-nsx-plugin/tests/
```
