# cloudify-nsx-plugin
Cloudify Network Virtualization with VMware (NSX) plugin

# Common Documentation

# Description

The VMware NSX plugin enables users to use a vCenter NSX-based infrastructure for deploying services (both network and security) and applications.

# Plugin Requirements

* Python versions:
    * 2.7.x
* VMware versions:
    * NSX >= 6.2.3
    * vSphere >= 6.0.0

## NSX Environment

* You require a working vSphere and vCenter environment with NSX installed. The plugin has been tested with NSX v.6.2.3.
To use network functionality you also require the vSphere v.2.3.0+ plugin.

# Types

Each type has an `nsx_auth` property that can be used to pass parameters for authentication.

## nsx_auth:

Provides structure with credentials for authentication in NSX.

* `username`: User name for NSX
* `password`: User password for NSX
* `host`: NSX host
* `raml`: (optional) Path to raml file. If not defined will, an embedded version from the plugin is used.

You can also provide all the properties described in the node also as inputs for a workflow action.
For example, if you do not have nsx_auth as static properties values or cannot provide it as inputs of blueprint,
you can also use the get_attributes call in place of a value in a workflow input.

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

For security reason - You can provide all the properties described in the node as static file `/etc/cloudify/nsx_plugin/connection_config.yaml` in yaml format:

```
username: <nsx username>
password: <nsx password>
host: <nsx host>
raml: <raml file>
```

Credentials have provided by static file will be never available by properties in nodes.

**General rules for properties**

The plugin always merges properties and inputs,
and will be overwritten by any existing runtime properties.

The following structure:

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

produces the following in runtime properties and will be used for login to NSX:

```
    runtime_properties:
      nsx_auth:
        username: nsx_user
        password: nsx_secret
        host: nsx_host
```

So, you can provide nsx_auth only in create and the action values will be reused in a delete action, without being explicitly specified there.

Advanced properties are defined in [nsx pdf](https://pubs.vmware.com/NSX-62/topic/com.vmware.ICbase/PDF/nsx_62_api.pdf).

## resource_id

Each node type that has a direct mapping to NSX objects, has a `resource_id` property
(in node properties as input and in runtime_properties as a store of such)
and contains an NSX internal ID. Note that this is not the `name` of an object.

**Examples:**

* `group` might have a `resource_id` such as `securitygroup-426`
* `policy` might have a `resource_id` such as `policy-108`
* `tag` might have a `resource_id` such as `securitytag-143`
* `vcenter vm id` might have a `resource_id` such as `vm-438`

## use_external_resource

Each node type that has direct mapping to NSX objects, has `use_external_resource` property
(in node properties as input and in runtime_properties as store of such) and
save as flag that plugin has reused external resource.

## Security-related functionality
### cloudify.nsx.security_group

A security group is a collection of assets or objects group from your vSphere inventory.

**Derived From:** cloudify.nodes.ApplicationServer

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object, default is false.
* `resource_id`: (optional) [NSX object ID](README.md#resource_id) Used to identify the object when `use_external_resource` is true.
* `group`: Properties for group.
    * `scopeId`: Scope ID (by default: `globalroot‐0`) or datacenterId or portgroupId in upgrade use cases.
    * `name`: Object name.
    * `member`: (optional) List of members. Also can be updated as [cloudify.nsx.security_group_member](README.md#cloudifynsxsecurity_group_member) node.
    * `excludeMember`: (optional) List of excluded members. Also can be updated as [cloudify.nsx.security_group_exclude_member](README.md#cloudifynsxsecurity_group_exclude_member) node.
    * `dynamicMemberDefinition`: (optional) List of rules for attaching new members. Also can be updated as [cloudify.nsx.security_group_dynamic_member](README.md#cloudifynsxsecurity_group_dynamic_member) node.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Merged copy of `resource_id` if use_external_resource or [id](README.md#resource_id) of newly-created object.
* `group`: Merged copy of `group`.

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
    * `dynamic_set`: Represents a rule set as displayed on the UI. There can be multiple dynamic sets inside a dynamic member definition.
    * `security_group_id`: `resource_id` from parent [security group](README.md#cloudifynsxsecurity_group).

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal ID used in the plugin for working with `dynamic_set`.
* `dynamic_member`: Merged copy of `dynamic_member`.

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
* For a more complex example see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

### cloudify.nsx.security_group_member

Attach a member to [Security Group](README.md#cloudifynsxsecurity_group).

**Derived From:** cloudify.nodes.ApplicationModule
**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `group_member`:
    * `objectId`: Member ID. Can be another security group or [vm](README.md#resource_id).
    * `security_group_id`: `resource_id` from parent [security group](README.md#cloudifynsxsecurity_group).

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal ID used in the plugin for working with `group_member`.
* `group_member`: Merged copy of `group_member`.

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
* For a more complex example, see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

### cloudify.nsx.security_group_exclude_member

Set an object as explicitly excluded from [Security Group](README.md#cloudifynsxsecurity_group).

**Derived From:** cloudify.nodes.ApplicationModule
**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `group_exclude_member`:
    * `objectId`: Member ID. Can be another security group or [vm](README.md#resource_id).
    * `security_group_id`: `resource_id` from parent [security group](README.md#cloudifynsxsecurity_group).

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal ID used in the plugin for working with `group_exclude_member`.
* `group_exclude_member`: Merged copy of `group_exclude_member`.

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
* For a more complex example, see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

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
* `use_external_resource`: (optional) Use external object. Default is false.
* `resource_id`: (optional) [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is true.
* `policy`:
    * `name`: Name of security policy.
    * `description`: (optional) Short description for the policy.
    * `precedence`: Sort order, place in list.
    * `parent`: (optional) Parent security policy.
    * `securityGroupBinding`: List of security groups. Can also be updated as [separate node](README.md#cloudifynsxsecurity_policy_group_bind).
    * `actionsByCategory` : List of actions by category. Can also be updated as [separate node](README.md#cloudifynsxsecurity_policy_section).

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Merged copy of `resource_id` if use_external_resource or [id](README.md#resource_id) of newly created object.
* `policy`: Merged copy of `policy`.

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
* For a more complex example, see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

**Relationships**

#### cloudify.nsx.relationships.is_applied_to

You can use `is_applied_to` for apply policy to security group without [separate node](README.md#cloudifynsxsecurity_policy_group_bind).

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

  empty_policy:
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
    relationships:
      - type: cloudify.nsx.relationships.is_applied_to
        target: security_group

```

### cloudify.nsx.security_policy_group_bind

Bind [security group](README.md#cloudifynsxsecurity_group) to [security policy](README.md#cloudifynsxsecurity_policy).

**Derived From:** cloudify.nodes.ApplicationModule

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `policy_group_bind`:
    * `security_policy_id`: `resource_id` from [security policy](README.md#cloudifynsxsecurity_policy).
    * `security_group_id`: `resource_id` from [security group](README.md#cloudifynsxsecurity_group).

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal ID used in the plugin for working with `policy_group_bind`.
* `policy_group_bind`: Merged copy of `policy_group_bind`.

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
* For a more complex example see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

### cloudify.nsx.security_policy_section

Update section in [security policy](README.md#cloudifynsxsecurity_policy).
If such a section already exists, it will be replaced, otherwise it will be inserted.

**Derived From:** cloudify.nodes.ApplicationModule

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `policy_section`:
    * `security_policy_id`: `resource_id` from [security policy](README.md#cloudifynsxsecurity_policy).
    * `category`: Category name.
    * `action`: Action structure. The list of fields depends on the category, see [nsx pdf](https://pubs.vmware.com/NSX-62/topic/com.vmware.ICbase/PDF/nsx_62_api.pdf) for the full list.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal ID used in the plugin for working with `policy_section`.
* `policy_section`: Merged copy of `policy_section`.

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
* For a more complex example see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

**Relationships**

#### cloudify.nsx.relationships.contained_in

Set security_policy_id from parent node:

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

  update_security_policy:
    type: cloudify.nsx.security_policy_section
    relationships:
      - type: cloudify.nsx.relationships.contained_in
        target: security_policy
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            policy_section:
              category: endpoint
              action:
                ....
```

### cloudify.nsx.security_tag

Security Tag.

**Derived From:** cloudify.nodes.ApplicationServer

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is false.
* `resource_id`: (optional) [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is true.
* `tag`:
    * `name`: Security tag name.
    * `description`: Security tag description.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Merged copy of `resource_id` if use_external_resource or [id](README.md#resource_id) of newly-created object.
* `tag`: Merged copy of `tag`.

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
* For a more complex example, see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

**Relationships**

#### cloudify.nsx.relationships.is_tagged_by

You can use `is_tagged_by` for attach tag to several vm's without separate node for [each](README.md#cloudifynsxsecurity_tag_vm).

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
    # can be used only with 'is_tagged_by' relationship
    instances:
      deploy: 2
    relationships:
      - type: cloudify.nsx.relationships.is_tagged_by
        target: security_tag

```

### cloudify.nsx.security_tag_vm

Apply [security tag](README.md#cloudifynsxsecurity_tag) to VM.

**Derived From:** cloudify.nodes.ApplicationModule

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `vm_tag`:
    * `tag_id`: Security tag ID.
    * `vm_id`: vCenter/vSphere VM ID.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal ID used in the plugin for working with `vm_tag`.
* `vm_tag`: Merged copy of `vm_tag`.

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

* For a more complex example, see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

## Network-related functionality

### cloudify.nsx.lswitch

Logical switches

**Derived From:** cloudify.nodes.Network

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. False by default.
* `resource_id`: (optional) [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is true.
* `switch`:
  * `transport_zone`: The name of the Scope (Transport Zone).
  * `name`: The name that will be assigned to the new logical switch.
  * `mode`: (optional) Control Plane Mode. Uses the Transport Zone default if not specified.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Merged copy of `resource_id` if use_external_resource or [id](README.md#resource_id) of newly-created object.
* `switch`: Merged copy of `switch`.
* `vsphere_network_id`: Network ID in vSphere.

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

NSX object check. Search NSX object and set `resource_id` in runtime properties for the object, and `use_external_resource` if the object can be used as an external resource.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `nsx_object`:
    * `name`: Name of NSX object to check exists.
    * `type`: Type of object. Can be: [tag](README.md#cloudifynsxsecurity_tag), [policy](README.md#cloudifynsxsecurity_policy) and [group](README.md#cloudifynsxsecurity_group) or [lswitch](README.md#cloudifynsxlswitch).
    * `scopeId`: (optional) Object scope, useful for group search. Default: `globalroot-0`.


**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: External resource ID if object can be used as external, otherwise `None`.
* `use_external_resource`: `True`, if object can be reused.

**Examples:**

Create tag only in the event that it doesn't exist.

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
Before running the test script, the following applications and components must be installed:
 * Python 2.7.9
 * VCForPython27.msi (```http://aka.ms/vcpython27```)

An example of the test script is located in the ```tests/platformtests/windows_example.ps1``` folder.

## Check total coverage and full functionality
### Get plugin codebase

```
git clone https://github.com/cloudify-cosmo/cloudify-nsx-plugin.git
git clone https://github.com/cloudify-cosmo/cloudify-vsphere-plugin.git
```

### Install plugin locally

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
