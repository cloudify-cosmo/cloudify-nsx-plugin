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

```yaml
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

```yaml
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

```yaml
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

```yaml
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

* `group` might have a `resource_id` such as `securitygroup-426`.
* `policy` might have a `resource_id` such as `policy-108`.
* `tag` might have a `resource_id` such as `securitytag-143`.
* `vCenter VM` might have a `vsphere_server_id` such as `vm-438`.
* `dlr`/`esg` might have a `resource_id` such as `edge-75`.
* `lswitch` might have a `resource_id` such as `virtualwire-136`.
* `vCenter Cluster` might have a `vsphere_cluster_id` such as `domain-c123`.
* `vCenter DataCenter` might have a `vsphere_datacenter_id` such as `datacenter-2`.
* `vCenter DataStore` might have a `vsphere_datastore_id` such as `datastore-10`.

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
* `use_external_resource`: (optional) Use external object. The default is `false`.
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
* `resource_id`: Merged copy of `resource_id` if `use_external_resource` or [ID](README.md#resource_id) of newly-created object.
* `group`: Merged copy of `group`.

**Examples:**

* [Simple example](tests/platformtests/resources/security_groups.yaml#L86) with one static child:
```yaml
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
* For a more complex example, see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

------

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

**Relationships:**

* `cloudify.nsx.relationships.contained_in`: Provided ability for set `security_group_id` from parent node.
  Derived from: `cloudify.relationships.contained_in`

**Examples:**

* [Simple example](tests/platformtests/resources/security_groups.yaml):
```yaml
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
* With relationship reuse:
```yaml
  security_group:
    type: cloudify.nsx.security_group
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            group:
              name: <some name>

  update_dynamic_members:
    type: cloudify.nsx.security_group_dynamic_member
    properties:
      nsx_auth: <authentication credentials for nsx>
    relationships:
      - type: cloudify.nsx.relationships.contained_in
        target: security_group
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            dynamic_member:
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

* For a more complex example see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

------

### cloudify.nsx.security_group_member

Attach a member to [Security Group](README.md#cloudifynsxsecurity_group).

**Derived From:** cloudify.nodes.ApplicationModule

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `group_member`:
    * `objectId`: Member ID. Can be another security group or [VM](README.md#resource_id).
    * `security_group_id`: `resource_id` from parent [security group](README.md#cloudifynsxsecurity_group).

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal ID used in the plugin for working with `group_member`.
* `group_member`: Merged copy of `group_member`.

**Relationships**

* `cloudify.nsx.relationships.contained_in`: Set `security_group_id` from parent node.
  Derived from: `cloudify.relationships.contained_in`.

**Examples:**

* [Simple example](tests/platformtests/resources/security_groups.yaml):
```yaml
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
* With relationship reuse:
```yaml
  security_group:
    type: cloudify.nsx.security_group
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            group:
              name: <some name>

  slave_master_security_group_bind:
    type: cloudify.nsx.security_group_member
    properties:
      nsx_auth: <authentication credentials for nsx>
    relationships:
      - type: cloudify.nsx.relationships.contained_in
        target: security_group
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            group_member:
              objectId: <object Id>
```

* For a more complex example, see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

------

### cloudify.nsx.security_group_exclude_member

Set an object as explicitly excluded from [Security Group](README.md#cloudifynsxsecurity_group).

**Derived From:** cloudify.nodes.ApplicationModule

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `group_exclude_member`:
    * `objectId`: Member ID. Can be another security group or [VM](README.md#resource_id).
    * `security_group_id`: `resource_id` from parent [security group](README.md#cloudifynsxsecurity_group).

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal ID used in the plugin for working with `group_exclude_member`.
* `group_exclude_member`: Merged copy of `group_exclude_member`.

**Relationships**

* `cloudify.nsx.relationships.contained_in`: Set `security_group_id` from parent node.
  Derived from `cloudify.relationships.contained_in`.

**Examples:**

* [Simple example](tests/platformtests/resources/security_groups.yaml):
```yaml
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
* With relationship reuse:
```yaml
  security_group:
    type: cloudify.nsx.security_group
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            group:
              name: <some name>

  slave_master_security_group_bind:
    type: cloudify.nsx.security_group_exclude_member
    properties:
      nsx_auth: <authentication credentials for nsx>
    relationships:
      - type: cloudify.nsx.relationships.contained_in
        target: security_group
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            group_exclude_member:
              objectId: <object Id>

```
* For a more complex example, see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

------

### cloudify.nsx.security_policy

A [security policy](README.md#cloudifynsxsecurity_policy) is a set of endpoint, firewall
and network introspection services that can be applied to a [security group](README.md#cloudifynsxsecurity_group).
When creating a security policy, a parent security policy can be specified if required. The security policy inherits
services from the parent security policy. [Security group](README.md#cloudifynsxsecurity_group) bindings and actions
can also be specified while creating the policy. Note that execution order of actions in a category
is implied by their order in the list.

If a virtual machine belongs to more than one security group, the services that are applied to the virtual
machine depends on the precedence of the security policy mapped to the security groups.

**Derived From:** cloudify.nodes.ApplicationServer

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is `true`.
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
* `resource_id`: Merged copy of `resource_id` if `use_external_resource` or [ID](README.md#resource_id) of newly created object.
* `policy`: Merged copy of `policy`.

**Relationships**

* `cloudify.nsx.relationships.is_applied_to`: You can use `is_applied_to` for apply policy to [security group](README.md#cloudifynsxsecurity_group)
  without [separate node](README.md#cloudifynsxsecurity_policy_group_bind). Derived from: `cloudify.relationships.connected_to`.

**Examples:**

* [Simple example](tests/platformtests/resources/security_policy.yaml):
```yaml
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
* With relationship reuse:
```yaml
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
* For a more complex example, see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

------

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

* [Simple example](tests/platformtests/resources/bind_policy_group.yaml):
```yaml
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
* For a more complex example see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

------

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

**Relationships**

* `cloudify.nsx.relationships.contained_in`: `Set security_policy_id` from parent node.
  Derived from: `cloudify.relationships.contained_in`.

**Examples:**

* [Simple example](tests/platformtests/resources/security_policy.yaml):
```yaml
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
* With relationship reuse:
```yaml
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
* For a more complex example see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

------

### cloudify.nsx.security_tag

Security Tag.

**Derived From:** cloudify.nodes.ApplicationServer

**Properties:**
* `nsx_auth`: The NSX authentication, look [above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is `true`.
* `tag`:
    * `name`: Security tag name.
    * `description`: Security tag description.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Merged copy of `resource_id` if `use_external_resource` or [ID](README.md#resource_id) of newly-created object.
* `tag`: Merged copy of `tag`.

**Relationships**
* `cloudify.nsx.relationships.is_tagged_by`: You can use `is_tagged_by` for attach tag to several `VM`'s without separate
  node for [each](README.md#cloudifynsxsecurity_tag_vm). Derived from `cloudify.relationships.connected_to`.

**Examples:**

* [Simple example](tests/platformtests/resources/security_tag.yaml):
```yaml
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
* With relationship reuse:
```yaml
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
* For a more complex example, see [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

------

### cloudify.nsx.security_tag_vm

Apply [security tag](README.md#cloudifynsxsecurity_tag) to VM.

**Derived From:** cloudify.nodes.ApplicationModule

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `vm_tag`:
    * `tag_id`: Security tag ID.
    * `vm_id`: vCenter/vSphere [VM ID](README.md#resource_id).

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: Internal ID used in the plugin for working with `vm_tag`.
* `vm_tag`: Merged copy of `vm_tag`.

**Examples:**

* Simple example:
```yaml
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
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is `true`.
* `switch`:
  * `transport_zone`: The name of the Scope (Transport Zone).
  * `name`: The name that will be assigned to the new logical switch.
  * `mode`: (optional) Control Plane Mode. Uses the Transport Zone default if not specified.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Merged copy of `resource_id` if `use_external_resource` or [ID](README.md#resource_id) of newly-created object.
* `name`: lswitch name.
* `switch`: Merged copy of `switch`.
* `vsphere_network_id`: [Network ID](README.md#resource_id) in vSphere.

**Examples:**

* Simple example:
```yaml
  slave_lswitch:
    type: cloudify.nsx.lswitch
    properties:
      nsx_auth: <authentication credentials for nsx>
      switch:
        name: <switch name>
        transport_zone: Main_Zone
        # UNICAST_MODE, MULTYCAST_MODE, HYBRID_MODE
        mode: UNICAST_MODE
```

------

### cloudify.nsx.dlr

Distributed Logical Router. The NSX Edge logical router provides East‐West distributed routing with tenant `IP` address space and data
path isolation. Virtual machines or workloads that reside on the same host on different subnets can
communicate with one another without having to traverse a traditional routing interface.
A logical router can have eight uplink interfaces and up to a thousand internal interfaces.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is `true`.
* `router`:
  * `name`: The name that will be assigned to the new [DLR](README.md#cloudifynsxdlr).
  * `dlr_pwd`: The admin password of new [DLR](README.md#cloudifynsxdlr).
  * `dlr_size`: The [DLR](README.md#cloudifynsxdlr) Control `VM` size, possible values: `compact`, `large`, `quadlarge`, `xlarge`.
  * `datacentermoid`: The [vCenter DataCenter ID](README.md#resource_id) where the [DLR](README.md#cloudifynsxdlr) control `VM` will be deployed.
  * `datastoremoid`: The [vCenter DataStore ID](README.md#resource_id) where the [DLR](README.md#cloudifynsxdlr) control `VM` will be deployed.
  * `resourcepoolid`: The [vCenter Cluster ID](README.md#resource_id) where the [DLR](README.md#cloudifynsxdlr) control `VM` will be deployed.
  * `ha_ls_id`: New [DLR](README.md#cloudifynsxdlr) HA [logical switch](README.md#cloudifynsxlswitch) [ID](README.md#resource_id) or vds port group.
  * `uplink_ls_id`: New [DLR](README.md#cloudifynsxdlr) uplink [logical switch](README.md#cloudifynsxlswitch) [ID](README.md#resource_id) or vds port group.
  * `uplink_ip`: New [DLR](README.md#cloudifynsxdlr) uplink `IP`.
  * `uplink_subnet`: New [DLR](README.md#cloudifynsxdlr) uplink subnet.
  * `uplink_dgw`: New [DLR](README.md#cloudifynsxdlr) default gateway.
* `firewall`:
  * `action`: The default action for firewall, possible: `accept` or `deny`. The default is `accept`.
  * `logging`: Log packages. The default is `false`.
* `dhcp`:
  * `enabled`: The required state of the [DHCP](README.md#cloudifynsxdlr_dhcp_relay) Server, possible `true` or `false`. The default is `true`.
  * `syslog_enabled`: The required logging state of the [DHCP](README.md#cloudifynsxdlr_dhcp_relay) Server, possible `true` or `false`. The default is `false`.
  * `syslog_level`: The logging level for [DHCP](README.md#cloudifynsxdlr_dhcp_relay) on this Edge (`INFO`/`WARNING`/etc.). The default is `INFO`.
* `routing`:
  * `enabled`: The required state of the routing on device, possible `true` or `false`. The default is `true`.
  * `staticRouting`:
    * `defaultRoute`: (optional, if no default routes needs to be configured).
      * `gatewayAddress`: static `IP`.
      * `vnic`: uplink `NIC`.
      * `mtu`: (optional) Valid value is smaller than the `MTU` set on the interface. Default will be the `MTU` of the interface on which this route is configured.
  * `routingGlobalConfig`:
    * `routerId`: Required when dynamic routing protocols like [OSPF](README.md#cloudifynsxospf_areas), or [BGP](README.md#cloudifynsxdlrbgpneighbour) are configured.
    * `logging`: (optional) When absent, `enable`=`false` and `logLevel`=`INFO`.
      * `logLevel`: The logging level for routing on this Edge (`INFO`/`WARNING`/etc.). The default is `INFO`.
      * `enabled`: The required state of the routing logging, possible `true` or `false`. The default is `false`.
    * `ecmp`: (optional) The default is `false`.
* `ospf`: Only one of [OSPF](README.md#cloudifynsxospf_areas)/[BGP](README.md#cloudifynsxdlrbgpneighbour) can be configured as the dynamic routing protocol for Logical Router.
  * `enabled`: The default is `false`. When `false`, it will delete the existing config.
  * `defaultOriginate`: The default is `false`. User can configure edge router to publish default route by setting it to `true`.
  * `gracefulRestart`: (optional) The default is `false`. User can enable graceful restart by setting it to `true`.
  * `redistribution`: (optional) The default is `false`.
  * `protocolAddress`: `IP` address on one of the uplink interfaces, only for enabled and use logical switch as [OSPF](README.md#cloudifynsxospf_areas).
  * `forwardingAddress`: `IP` address on the same subnet as the `forwardingAddress`, only for enabled and use logical switch as [OSPF](README.md#cloudifynsxospf_areas).
* `bgp`: Only one of [OSPF](README.md#cloudifynsxospf_areas)/[BGP](README.md#cloudifynsxdlrbgpneighbour) can be configured as the dynamic routing protocol for Logical Router.
  * `enabled`: When not specified, it will be treated as `false`, When `false`, it will delete the existing config.
  * `defaultOriginate`: The default is `false`. User can configure edge router to publish default route by setting it to `true`.
  * `gracefulRestart`: (optional) The default is `false`. User can enable graceful restart by setting it to `true`.
  * `redistribution`: (optional) The default is `false`.
  * `localAS`: Valid values are : 1-65534. To be disabled, a number must be specified.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Merged copy of `resource_id` if `use_external_resource` or [ID](README.md#resource_id) of newly-created object.
* `name`: DLR name.
* `vsphere_server_id`: [VM ID](README.md#resource_id) in vSphere.
* `router`: Merged copy of `router`.
* `firewall`: Merged copy of `firewall`.
* `dhcp`: Merged copy of `dhcp`.
* `routing`: Merged copy of `routing`.
* `ospf`: Merged copy of `ospf`.
* `bgp`: Merged copy of `bgp`.
* `uplink_vnic`: `VNIC ID` for uplink.

**Relationships**
* `cloudify.nsx.relationships.deployed_on_datacenter`: Fill `datacentermoid` from `cloudify.vsphere.nodes.Datacenter` node type.
  Derived from `cloudify.relationships.connected_to`.
* `cloudify.nsx.relationships.deployed_on_datastore`: Fill `datastoremoid` from `cloudify.vsphere.nodes.Datastore` node type.
  Derived from `cloudify.relationships.connected_to`.
* `cloudify.nsx.relationships.deployed_on_cluster`: Fill `resourcepoolid` from `cloudify.vsphere.nodes.Cluster` node type.
  Derived from `cloudify.relationships.connected_to`.

**Examples:**

* Simple example:
```yaml
  datacenter:
    type: cloudify.vsphere.nodes.Datacenter
    properties:
      use_existing_resource: true
      name: <vcenter_datacenter name>
      connection_config: <vcenter connection config>

  datastore:
    type: cloudify.vsphere.nodes.Datastore
    properties:
      use_existing_resource: true
      name: <vcenter_datastore name>
      connection_config: <vcenter connection config>

  cluster:
    type: cloudify.vsphere.nodes.Cluster
    properties:
      use_existing_resource: true
      name: <vcenter cluster name>
      connection_config: <vcenter connection config>

  slave_lswitch:
    type: cloudify.nsx.lswitch
    properties:
      nsx_auth: <authentication credentials for nsx>
      switch:
        name: slave_switch
        transport_zone: Main_Zone
        # UNICAST_MODE, MULTYCAST_MODE, HYBRID_MODE
        mode: UNICAST_MODE

  nsx_dlr:
    type: cloudify.nsx.dlr
    properties:
      nsx_auth: <authentication credentials for nsx>
      router:
        name: <router_name>
        dlr_pwd: SeCrEt010203!
        dlr_size: compact
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            router:
              ha_ls_id: { get_attribute: [ slave_lswitch, resource_id ] }
              uplink_ls_id: { get_attribute: [ slave_lswitch, resource_id ] }
              uplink_ip: 192.168.1.11
              uplink_subnet: 255.255.255.0
              uplink_dgw: 192.168.1.1
    relationships:
      - type: cloudify.relationships.connected_to
        target: master_lswitch
      - type: cloudify.nsx.relationships.deployed_on_datacenter
        target: datacenter
      - type: cloudify.nsx.relationships.deployed_on_datastore
        target: datastore
      - type: cloudify.nsx.relationships.deployed_on_cluster
        target: cluster

```
* For a more complex example see [dlr_functionality.yaml](tests/integration/resources/dlr_functionality.yaml)
* For a more complex example with [BGP](README.md#cloudifynsxdlrbgpneighbour) see [dlr_with_bgp_functionality.yaml](tests/integration/resources/dlr_with_bgp_functionality.yaml)

------

### cloudify.nsx.ospf_areas

Distributed Logical Routers interface OSPF areas.
Use only after all [DLR](README.md#cloudifynsxdlrinterface) or [ESG](README.md#cloudifynsxesginterface)
interfaces creation, in other case can be cleanuped.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `area`:
  * `dlr_id`: `resource_id` from [DLR](README.md#cloudifynsxdlr) or [ESG](README.md#cloudifynsxesg).
  * `areaId`: Mandatory and unique. Valid values are 0-4294967295.
  * `type`: (optional) The default is `normal`. Valid inputs are `normal`, `nssa`.
  * `authentication`: (optional) When not specified, the default is `none` and authentication is not performed.
    * `type`: Valid values are `none`, `password`, `md5`.
    * `value`: Value for authentication.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `ospf_areas`.
* `area`: Merged copy of `area`.

**Examples:**

* Simple example:
```yaml
  ospf_areas:
    type: cloudify.nsx.ospf_areas
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            area:
              dlr_id: <dlr resource_id>
              areaId: 1000
              type: nssa
              authentication:
                type: none
```
* For a more complex example with [DLR](README.md#cloudifynsxdlr) see [dlr_functionality.yaml](tests/integration/resources/dlr_functionality.yaml)
* For a more complex example with [ESG](README.md#cloudifynsxesg) see [esg_with_ospf_functionality.yaml](tests/integration/resources/esg_with_ospf_functionality.yaml)

------

### cloudify.nsx.ospf_interfaces

Distributed Logical Routers interface [OSPF](README.md#cloudifynsxospf_areas) interfaces.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `interface`:
  * `dlr_id`: `resource_id` from [DLR](README.md#cloudifynsxdlr) or [ESG](README.md#cloudifynsxesg).
  * `areaId`: Mandatory and unique. Valid values are 0-4294967295.
  * `vnic`: `NIC ID` in [DLR](README.md#cloudifynsxdlr)/[ESG](README.md#cloudifynsxesg).
  * `helloInterval`: (optional) Valid values are 1-255. The default is 10 sec.
  * `deadInterval`: (optional) Valid values are 1-65535. The default is 40 sec.
  * `priority`: (optional) Valid values are 0-255. The default is 128.
  * `cost`: (optional) Auto based on interface speed. Valid values are 1-65535.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `ospf_interfaces`.
* `interface`: Merged copy of `interface`.

**Examples:**

* Simple example:
```yaml
  ospf_interface:
    type: cloudify.nsx.ospf_interfaces
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            interface:
              dlr_id: <dlr resource_id>
              vnic: <dlr vnic>
              areaId: <area id>
              helloInterval: 10
              priority: 128
              cost: 1
              deadInterval: 40
              mtuIgnore: false
```
* For a more complex example with [DLR](README.md#cloudifynsxdlr) see [dlr_functionality.yaml](tests/integration/resources/dlr_functionality.yaml)
* For a more complex example with [ESG](README.md#cloudifynsxesg) see [esg_with_ospf_functionality.yaml](tests/integration/resources/esg_with_ospf_functionality.yaml)

------

### cloudify.nsx.dlrBGPNeighbour

BGP Neighbour.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `neighbour`:
  * `dlr_id`: `resource_id` from [DLR](README.md#cloudifynsxdlr).
  * `ipAddress`: `IPv4` only. `IPv6` is not supported.
  * `remoteAS`: Valid values are 0-65535.
  * `weight`: (optional) Valid values are 0-65535. The default is 60.
  * `holdDownTimer`: (optional) Valid values are : 2-65535. The default is 180 seconds.
  * `keepAliveTimer`: (optional) Valid values are : 1-65534. The default is 60 seconds.
  * `password`: (optional) [BGP](README.md#cloudifynsxdlrbgpneighbour) neighbour password.
  * `protocolAddress`: `IP` address on one of the uplink interfaces for use with [OSPF](README.md#cloudifynsxospf_areas) protocol on [logical switch](README.md#cloudifynsxlswitch).
  * `forwardingAddress`: `IP` address on the same subnet as the `forwardingAddress` for use with [OSPF](README.md#cloudifynsxospf_areas) protocol on [logical switch](README.md#cloudifynsxlswitch).

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `dlrBGPNeighbour`.
* `neighbour`: Merged copy of `neighbour`.

**Examples:**

* Simple example:
```yaml
  bgp_neighbour:
    type: cloudify.nsx.dlrBGPNeighbour
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            neighbour:
              dlr_id: <dlr resource_id>
              ipAddress: 192.168.2.1
              remoteAS: 64521
              protocolAddress: 192.168.1.20
              forwardingAddress: 192.168.1.11
```
* For a more complex example see [dlr_with_bgp_functionality.yaml](tests/integration/resources/dlr_with_bgp_functionality.yaml)

------

### cloudify.nsx.esgBGPNeighbourFilter

[BGP Neighbour](README.md#cloudifynsxesgbgpneighbour) Filter.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `filter`:
  * `neighbour_id`: `resource_id` from [BGP Neighbour](README.md#cloudifynsxdlrbgpneighbour).
  * `action`: Valid values are `permit`/`deny`.
  * `ipPrefixGe`: (optional) "Greater than or equal to" & used for filtering based on prefix length. Valid values are only `IPv4` prefixes.
  * `ipPrefixLe`: (optional) "Less than or equal to" & used for filtering based on prefix length. Valid values are only `IPv4` prefixes.
  * `direction`: Valid values are `in`/`out`
  * `network`: Valid values are `CIDR` networks. `IPv4` only. `IPv6` is not supported.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `esgBGPNeighbourFilter`.
* `filter`: Merged copy of `filter`.

**Examples:**
* Simple example:
```yaml
  bgp_neighbour_filter:
    type: cloudify.nsx.esgBGPNeighbourFilter
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            filter:
              neighbour_id: <BGP Neighbour resource id>
              action: deny
              ipPrefixGe: 30
              ipPrefixLe: 32
              direction: in
              network: 192.169.1.0/24
```
* For a more complex example see [dlr_with_bgp_functionality.yaml](tests/integration/resources/dlr_with_bgp_functionality.yaml)

------

### cloudify.nsx.dlr_routing_ip_prefix

Distributed logical routers interface routing ip prefixes.

Required only if user wants to define redistribution rules in dynamic routing protocols like [OSPF](README.md#cloudifynsxospf_areas) or [BGP](README.md#cloudifynsxdlrbgpneighbour).

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `prifix`:
  * `dlr_id`: `resource_id` from [DLR](README.md#cloudifynsxdlr).
  * `name`: All the defined `IP` prefixes must have unique names.
  * `ipAddress`: `IP` address like 10.112.196.160/24

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `dlr_routing_ip_prefix`.
* `prefix`: Merged copy of `prefix`.

**Examples:**

* Simple example:
```yaml
  dlr_ip_prefix:
    type: cloudify.nsx.dlr_routing_ip_prefix
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            prefix:
              dlr_id: <dlr resource_id>
              name: <routing prefix name>
              ipAddress: 10.112.196.160/24
```
* For a more complex example see [dlr_with_bgp_functionality.yaml](tests/integration/resources/dlr_with_bgp_functionality.yaml)

------

### cloudify.nsx.routing_redistribution_rule

Distributed Logical Routers interface [OSPF](README.md#cloudifynsxospf_areas) redistribution rule.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `rule`:
  * `dlr_id`: `resource_id` from [DLR](README.md#cloudifynsxdlr).
  * `type`: resdistribute section can be `ospf`/`bgp`.
  * `prefixName`: (optional) [Prefix name](README.md#cloudifynsxdlr_routing_ip_prefix) used here should be defined in the routingGlobalConfig->ipPrefixes. The default is `any`.
  * `from`:
    * `isis`: (optional) The default is `false`.
    * `ospf`: (optional) The default is `false`.
    * `bgp`: (optional) The default is `false`.
    * `static`: (optional) The default is `false`.
    * `connected`: (optional) The default is `false`.
  * `action`: Mandatory. Valid values are `deny`/`permit`.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `routing_redistribution_rule`.
* `rule`: Merged copy of `rule`.

**Examples:**

* Simple example:
```yaml
  dlr_bgp_redistribute:
    type: cloudify.nsx.routing_redistribution_rule
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            rule:
              dlr_id: <dlr resource_id>
              prefixName: <prefix name>
              type: bgp
              from:
                ospf: true
                static: true
              action: deny
```
* For a more complex example see [dlr_with_bgp_functionality.yaml](tests/integration/resources/dlr_with_bgp_functionality.yaml)

------

### cloudify.nsx.dlr_interface

Distributed Logical Router interface.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `interface`:
  * `dlr_id`: `resource_id` from [DLR](README.md#cloudifynsxdlr).
  * `interface_ls_id`: [logical switch](README.md#cloudifynsxlswitch) [ID](README.md#resource_id)
  * `interface_ip`: interface `IP` address.
  * `interface_subnet`: interface subnet.
  * `name`: name for interface
  * `vnic`: (optional) `VNIC` for interface

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `dlr_interface`.
* `interface`: Merged copy of `interface`.
* `ifindex`: `VNIC ID` of interface in DLR.

**Examples:**

* Simple example:
```yaml
  interface:
    type: cloudify.nsx.dlr_interface
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            interface:
              dlr_id: <dlr resource_id>
              interface_ls_id: <lswitch resource_id>
              interface_ip: 192.168.2.11
              interface_subnet: 255.255.255.0
              name: <interface name>
```
* For a more complex example see [dlr_functionality.yaml](tests/integration/resources/dlr_functionality.yaml)

------

### cloudify.nsx.dlr_dhcp_relay

Distributed Router dhcp relay, we need separate type because we can
change it only after set all settings for interfaces.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `relay`:
  * `dlr_id`: `resource_id` from [DLR](README.md#cloudifynsxdlr).
  * `relayServer`: Relay servers settings.
  * `relayAgents`: Relay agents settings.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `dlr_dhcp_relay`.
* `relay`: Merged copy of `relay`.

**Examples:**

* Simple example:
```yaml
  dhcp_relay:
    type: cloudify.nsx.dlr_dhcp_relay
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            relay:
              dlr_id: <dlr resource_id>
              relayServer:
                ipAddress: 8.8.8.8
              relayAgents:
                relayAgent:
                  vnicIndex: <vnic id>
                  giAddress: <interface ip>
```
* For a more complex example see [dlr_functionality.yaml](tests/integration/resources/dlr_functionality.yaml)

------

### cloudify.nsx.dlr_dgw

Distributed Logical Router gateway.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `gateway`:
  * `dlr_id`: `resource_id` from [DLR](README.md#cloudifynsxdlr).
  * `address`: Default gateway `IP` address.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `dlr_dgw`.
* `gateway`: Merged copy of `gateway`.

**Examples:**

* Simple example:
```yaml
  dlr_static_gateway:
    type: cloudify.nsx.dlr_dgw
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            gateway:
              dlr_id: <dlr resource_id>
              address: 192.168.1.12
```
* For a more complex example see [dlr_functionality.yaml](tests/integration/resources/dlr_functionality.yaml)

------

### cloudify.nsx.esg

Edge Services Gateway. The services gateway gives you access to all `NSX Edge` services such as [firewall](README.md#cloudifynsxesg_firewall),
[NAT](README.md#cloudifynsxesg_nat), [DHCP](README.md#cloudifynsxdhcp_pool), `VPN`, load balancing, and high availability. You can install multiple NSX Edge services gateway virtual appliances in a
datacenter. Each NSX Edge virtual appliance can have a total of ten uplink and internal network interfaces.The
internal interfaces connect to secured port groups and act as the gateway for all protected virtual machines in
the port group. The subnet assigned to the internal interface can be a publicly routed `IP` space or a
NATed/routed RFC 1918 private space. [Firewall](README.md#cloudifynsxesg_firewall) rules and other NSX Edge services are enforced on traffic
between network interfaces.

Uplink interfaces of NSX Edge connect to uplink port groups that have access to a shared corporate network
or a service that provides access layer networking. Multiple external `IP` addresses can be configured for load
balancer, site‐to‐site VPN, and NAT services.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is `true`.
* `edge`:
  * `name`: The name of the [ESG](README.md#cloudifynsxesg) to be created.
  * `esg_pwd`: The CLI password of the [ESG](README.md#cloudifynsxesg).
  * `esg_size`: The size of the [ESG](README.md#cloudifynsxesg), possible values: `compact`, `large`, `quadlarge`, `xlarge`.
  * `datacentermoid`: The [vCenter DataCenter ID](README.md#resource_id) where the [DLR](README.md#cloudifynsxdlr) control `VM` will be deployed.
  * `datastoremoid`: The [vCenter DataStore ID](README.md#resource_id) where the [DLR](README.md#cloudifynsxdlr) control `VM` will be deployed.
  * `resourcepoolid`: The [vCenter Cluster ID](README.md#resource_id) where the [DLR](README.md#cloudifynsxdlr) control `VM` will be deployed.
  * `default_pg`: The managed object [ID](README.md#resource_id) of the port group for the first `VNIC`(on creation the first `VNIC` must be connected to a valid portgroup in NSX).
  * `esg_username`: The Username for the CLI and SSH access. The default is `admin`.
  * `esg_remote_access`: Enables / Disables SSH access to the Edge Host. The default is `false`.
* `firewall`:
  * `action`: Default action for [firewall](README.md#cloudifynsxesg_firewall), possible: `accept` or `deny`. The default is `accept`.
  * `logging`: Log packages. The default is `false`.
* `dhcp`:
  * `enabled`: The required state of the [DHCP](README.md#cloudifynsxdhcp_pool) Server, possible `true` or `false`. The default is `true`.
  * `syslog_enabled`: The required logging state of the [DHCP](README.md#cloudifynsxdhcp_pool) Server, possible `true` or `false`. The default is `false`.
  * `syslog_level`: The logging level for [DHCP](README.md#cloudifynsxdhcp_pool) on this Edge (`INFO`/`WARNING`/etc.). The default is `INFO`.
* `nat`:
  * `enabled`: The required state of the [NAT](README.md#cloudifynsxesg_nat) service, possible `true` or `false`. The default is `true`.
* `routing`:
  * `enabled`: The required state of the routing on device, possible `true` or `false`. The default is `true`.
  * `staticRouting`:
    * `defaultRoute`: (optional, if no default routes needs to be configured).
      * `gatewayAddress`: static `IP`.
      * `vnic`: uplink `NIC`.
      * `mtu`: (optional) Valid value is smaller than the `MTU` set on the interface. Default will be the `MTU` of the interface on which this route is configured.
  * `routingGlobalConfig`:
    * `routerId`: Required when dynamic routing protocols like [OSPF](README.md#cloudifynsxospf_areas), or [BGP](README.md#cloudifynsxesgbgpneighbour) is configured.
    * `logging`: (optional) When absent, `enable`=`false` and `logLevel`=`INFO`.
      * `logLevel`: The logging level for routing on this Edge (`INFO`/`WARNING`/etc.). The default is `INFO`.
      * `enabled`: The required state of the routing logging, possible `true` or `false`. The default is `false`.
    * `ecmp`: (optional) The default is `false`.
* `ospf`: Only one of [OSPF](README.md#cloudifynsxospf_areas)/[BGP](README.md#cloudifynsxdesesgbgpneighbour) can be configured as the dynamic routing protocol for Logical Router.
  * `enabled`: When not specified, it will be treated as `false`, When `false`, it will delete the existing config.
  * `defaultOriginate`: The default is `false`. User can configure edge router to publish default route by setting it to `true`.
  * `gracefulRestart`: (optional) The default is `false`, user can enable graceful restart by setting it to `true`.
  * `redistribution`: (optional) The default is `false`.
* `bgp`: Only one of [OSPF](README.md#cloudifynsxospf_areas)/[BGP](README.md#cloudifynsxesgbgpneighbour) can be configured as the dynamic routing protocol for Logical Router.
  * `enabled`: When not specified, it will be treated as `false`, When `false`, it will delete the existing config.
  * `defaultOriginate`: The default is `false`. User can configure edge router to publish default route by setting it to `true`.
  * `gracefulRestart`: (optional) The default is `false`. User can enable graceful restart by setting it to `true`.
  * `redistribution`: (optional) The default is `false`.
  * `localAS`: Valid values are : 1-65534, For disabled it must to have some number.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Merged copy of `resource_id` if `use_external_resource` or [ID](README.md#resource_id) of newly-created object.
* `name`: [ESG](README.md#cloudifynsxesg) name.
* `vsphere_server_id`: [VM ID](README.md#resource_id) in vCenter.
* `edge`: Merged copy of `edge`.
* `firewall`: Merged copy of `firewall`.
* `dhcp`: Merged copy of `dhcp`.
* `nat`: Merged copy of `nat`.
* `routing`: Merged copy of `routing`.
* `ospf`: Merged copy of `ospf`.
* `bgp`: Merged copy of `bgp`.

**Relationships**
* `cloudify.nsx.relationships.deployed_on_datacenter`: Fill `datacentermoid` from `cloudify.vsphere.nodes.Datacenter` node type.
  Derived from `cloudify.relationships.connected_to`.
* `cloudify.nsx.relationships.deployed_on_datastore`: Fill `datastoremoid` from `cloudify.vsphere.nodes.Datastore` node type.
  Derived from `cloudify.relationships.connected_to`.
* `cloudify.nsx.relationships.deployed_on_cluster`: Fill `resourcepoolid` from `cloudify.vsphere.nodes.Cluster` node type.
  Derived from `cloudify.relationships.connected_to`.

**Examples:**

* Simple example:
```yaml
  datacenter:
    type: cloudify.vsphere.nodes.Datacenter
    properties:
      use_existing_resource: true
      name: <vcenter_datacenter name>
      connection_config: <vcenter connection config>

  datastore:
    type: cloudify.vsphere.nodes.Datastore
    properties:
      use_existing_resource: true
      name: <vcenter_datastore name>
      connection_config: <vcenter connection config>

  cluster:
    type: cloudify.vsphere.nodes.Cluster
    properties:
      use_existing_resource: true
      name: <vcenter cluster name>
      connection_config: <vcenter connection config>

  slave_lswitch:
    type: cloudify.nsx.lswitch
    properties:
      nsx_auth: <authentication credentials for nsx>
      switch:
        name: slave_switch
        transport_zone: Main_Zone
        # UNICAST_MODE, MULTYCAST_MODE, HYBRID_MODE
        mode: UNICAST_MODE

  esg:
    type: cloudify.nsx.esg
    properties:
      nsx_auth: <authentication credentials for nsx>
      edge:
        name: name: <edge_name>
        esg_pwd: SeCrEt010203!
        esg_remote_access: true
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            edge:
              default_pg: { get_attribute: [ master_lswitch, vsphere_network_id ] }
    relationships:
      - type: cloudify.relationships.connected_to
        target: master_lswitch
      - type: cloudify.nsx.relationships.deployed_on_datacenter
        target: datacenter
      - type: cloudify.nsx.relationships.deployed_on_datastore
        target: datastore
      - type: cloudify.nsx.relationships.deployed_on_cluster
        target: cluster
```
* For a more complex example see [esg_functionality.yaml](tests/integration/resources/esg_functionality.yaml)
* For a more complex example with [OSPF](README.md#cloudifynsxospf_areas) see [esg_with_ospf_functionality.yaml](tests/integration/resources/esg_with_ospf_functionality.yaml)

------

### cloudify.nsx.esgBGPNeighbour

[ESG](README.md#cloudifynsxesg) BGP Neighbour.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `neighbour`:
  * `dlr_id`: `resource_id` from [ESG](README.md#cloudifynsxesg).
  * `ipAddress`: `IPv4` only. `IPv6` is not supported.
  * `remoteAS`: Valid values are 0-65535.
  * `weight`: (optional) Valid values are 0-65535. The default is 60.
  * `holdDownTimer`: (optional) Valid values are : 2-65535. The default is 180 seconds.
  * `keepAliveTimer`: (optional) Valid values are : 1-65534. The default is 60 seconds.
  * `password`: (optional) BGP neighbour password.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `dlrBGPNeighbour`.
* `neighbour`: Merged copy of `neighbour`.

**Examples:**

* Simple example:
```yaml
  bgp_neighbour:
    type: cloudify.nsx.esgBGPNeighbour
    properties:
      nsx_auth: <authentication credentials for nsx>
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            neighbour:
              dlr_id: <esg resource_id>
              ipAddress: 192.168.2.1
              remoteAS: 64521
```
* For a more complex example see [esg_with_bgp_functionality.yaml](tests/integration/resources/esg_with_bgp_functionality.yaml)

------

### cloudify.nsx.esg_nat

Edge Services Gateway NAT.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `rule`:
  * `esg_id`: `resource_id` from [ESG](README.md#cloudifynsxesg).
  * `action`: Actuon type: `dnat`/`snat`.
  * `originalAddress`: Original address.
  * `translatedAddress`: Translated address.
  * `vnic`: (optional) `VNIC`.
  * `ruleTag`: (optional) Can be used to specify user-controlled ids on VSE. Valid inputs 65537-131072. If not specified, vShield manager will generate ruleId.
  * `loggingEnabled`: (optional) Default is `false`.
  * `enabled`: (optional) The default is `true`.
  * `description`: (optional) NAT rule description.
  * `protocol`: (optional) The default is `any`. This tag is not supported for `SNAT` rule.
  * `translatedPort`: (optional) The default is `any`. This tag is not supported for `SNAT` rule.
  * `originalPort`: (optional) The default is `any`. This tag is not supported for `SNAT` rule.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `esg_nat`.
* `rule`: Merged copy of `rule`.

**Examples:**

* Simple example:
```yaml
  nat_rule:
    type: cloudify.nsx.esg_nat
    properties:
      nsx_auth: <authentication credentials for nsx>
      rule:
        action: dnat
        translatedAddress: 192.168.10.1
        originalAddress: 192.168.1.2
        vnic: 3
        ruleTag: 65538
        loggingEnabled: false
        enabled: true
        description: some nat rule
        protocol: any
        translatedPort: any
        originalPort: any
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            rule:
              esg_id: <esg resource_id>
```
* For a more complex example see [esg_functionality.yaml](tests/integration/resources/esg_functionality.yaml)

------

### cloudify.nsx.esg_firewall

Edge Services Gateways firewall.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `rule`:
  * `esg_id`: `resource_id` from [ESG](README.md#cloudifynsxesg).
  * `ruleTag`: (optional) This can be used to specify user controlled ids on VSE. The inputs here should be 1-65536. If not specified, VSM will generate ruleId.
  * `name`: (optional) firewall rule name.
  * `source`: (optional) Default behaviour is like `any`. `IPSetID` or predefined-vnicGroupIds can be used.
  * `destination`: (optional) Default behaviour is like `any`. `IPSetID` or predefined-vnicGroupIds can be used.
  * `application`: (optional) Default behaviour is like `any`. `ApplicationSetId` or applicationgroupId can be used
  * `matchTranslated`: (optional) Default behaviour is like `false`.
  * `direction`: (optional) Default behaviour is like `any`. Possible values are `in` and `out`.
  * `action`: (mandatory) Possible values are `accept`|`deny`|`reject`.
  * `enabled`: (optional) The default is `true`.
  * `loggingEnabled`: (optional) The default is `false`.
  * `description`: (optional) Rule description.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `esg_firewall`.
* `rule`: Merged copy of `rule`.
* `rule_id`: firewall rule ID.

**Examples:**

* Simple example:
```yaml
  firewall_rule:
    type: cloudify.nsx.esg_firewall
    properties:
      nsx_auth: <authentication credentials for nsx>
      rule:
        name: http
        loggingEnabled: false
        matchTranslated: false
        enabled: true
        source: any
        action: accept
        description: Some Firewall Rule
        direction: in
        application: any
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            rule:
              esg_id: <esg resource_id>
              destination:
                groupingObjectId: <cluster vsphere_cluster_id>
```
* For a more complex example see [esg_functionality.yaml](tests/integration/resources/esg_functionality.yaml)

------

### cloudify.nsx.esg_interface

Edge Services Gateway interface.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `interface`:
  * `esg_id`: `resource_id` from [ESG](README.md#cloudifynsxesg).
  * `ifindex`: The `VNIC` index, e.g. vnic3 and the index 3
  * `ipaddr`: (optional) The primary IP Address to be configured for this interface.
  * `netmask`: (optional) The netmask in the x.x.x.x format.
  * `prefixlen`: (optional) The prefix length, this takes precedence over the netmask.
  * `name`: (optional) The name assigned to the `VNIC`.
  * `mtu`: (optional) The `VNIC` `MTU`.
  * `is_connected`: (optional) The `VNIC` connection state (`true`/`false`).
  * `portgroup_id`: (optional) The portgroup id of logical switch id to connenct this `VNIC` to.
  * `vnic_type`: (optional) The `VNIC` type (`uplink`/`internal`).
  * `enable_send_redirects`: (optional) Whether the interface will send `ICMP` redirects (`true`/`false`).
  * `enable_proxy_arp`: (optional) Whether the interface will do proxy arp (`true`/`false`).
  * `secondary_ips`: (optional) A list of additional secondary IP addresses in the primary IP's Subnet.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `esg_interface`.
* `interface`: Merged copy of `interface`.
* `ifindex`: `VNIC` id of interface in [ESG](README.md#cloudifynsxesg).

**Examples:**

* Simple example:
```yaml
  esg_interface:
    type: cloudify.nsx.esg_interface
    properties:
      nsx_auth: <authentication credentials for nsx>
      interface:
        ifindex: 3
        ipaddr: 192.168.3.1
        netmask: 255.255.255.0
        prefixlen: 24
        name: <router interface name>
        mtu: 1500
        is_connected: "true"
        vnic_type: internal
        enable_send_redirects: "true"
        enable_proxy_arp: "true"
        secondary_ips: 192.168.3.128
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            interface:
              esg_id: <esg resource_id>
              portgroup_id: <lswitch resource_id>
```
* For a more complex example see [esg_functionality.yaml](tests/integration/resources/esg_functionality.yaml)
* For a more complex example with [OSPF](README.md#cloudifynsxospf_areas) see [esg_with_ospf_functionality.yaml](tests/integration/resources/esg_with_ospf_functionality.yaml)

------

### cloudify.nsx.esg_gateway

Edge Services Gateway settings.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `gateway`:
  * `esg_id`: `resource_id` from [ESG](README.md#cloudifynsxesg).
  * `dgw_ip`: The default gateway `IP` (next hop).
  * `vnic`: (optional) The `VNIC` index of were the default gateway is reachable on.
  * `mtu`: (optional) The `MTU` of the default gateway. The default is `1500`.
  * `admin_distance`: (optional) Admin distance of the default route. The default is `1`.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `esg_gateway`.
* `gateway`: Merged copy of `gateway`.

**Examples:**

* Simple example:
```yaml
  esg_gateway:
    type: cloudify.nsx.esg_gateway
    properties:
      nsx_auth: <authentication credentials for nsx>
      gateway:
        dgw_ip: 192.168.3.11
        vnic: 3
        mtu: 1500
        admin_distance: 1
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            gateway:
              esg_id: <esg resource_id>
```
* For a more complex example see [esg_functionality.yaml](tests/integration/resources/esg_functionality.yaml)
* For a more complex example with [OSPF](README.md#cloudifynsxospf_areas) see [esg_with_ospf_functionality.yaml](tests/integration/resources/esg_with_ospf_functionality.yaml)

------

### cloudify.nsx.esg_route

Edge Services Gateways route.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `route`:
  * `esg_id`: `resource_id` from [ESG](README.md#cloudifynsxesg).
  * `network`: The routes network in the `x.x.x.x/yy` format, e.g. `192.168.1.0/24`.
  * `next_hop`: The next hop `IP`.
  * `vnic`: (optional) The `VNIC` index of were this route is reachable on.
  * `mtu`: (optional) The `MTU` of the route. The default is `1500`.
  * `admin_distance`: (optional) Admin distance of the default route. The default is `1`.
  * `description`: (optional) A description for this route.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `esg_route`.
* `route`: Merged copy of `route`.

**Examples:**

* Simple example:
```yaml
  esg_route:
    type: cloudify.nsx.esg_route
    properties:
      nsx_auth: <authentication credentials for nsx>
      route:
          network: 192.168.10.0/24
          next_hop: 192.168.3.10
          vnic: 3
          mtu: 1500
          admin_distance: 1
          description: Some cool route
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            route:
              esg_id: <esg resource_id>
```
* For a more complex example see [esg_functionality.yaml](tests/integration/resources/esg_functionality.yaml)

------

### cloudify.nsx.dhcp_pool

Edge DHCP pool.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `pool`:
  * `esg_id`: `resource_id` from [ESG](README.md#cloudifynsxesg).
  * `ip_range`: An IP range, e.g. 192.168.178.10-192.168.178.100 for this `IP` Pool.
  * `default_gateway`: (optional) The default gateway for the specified subnet.
  * `subnet_mask`: (optional) The subnet mask (e.g. 255.255.255.0) for the specified subnet.
  * `domain_name`: (optional) The DNS domain name (e.g. vmware.com) for the specified subnet.
  * `dns_server_1`: (optional) The primary DNS Server.
  * `dns_server_2`: (optional) The secondary DNS Server.
  * `lease_time`: (optional) The lease time in seconds, use 'infinite' to disable expiry of DHCP leases.
  * `auto_dns`: (optional) If set to `true`, the DNS servers and domain name set for NSX-Manager will be used.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `dhcp_pool`.
* `pool`: Merged copy of `pool`.

**Examples:**

* Simple example:
```yaml
  esg_pool:
    type: cloudify.nsx.dhcp_pool
    properties:
      nsx_auth: <authentication credentials for nsx>
      pool:
        ip_range: 192.168.5.128-192.168.5.250
        default_gateway: 192.168.5.1
        subnet_mask: 255.255.255.0
        domain_name: internal.test
        dns_server_1: 8.8.8.8
        dns_server_2: 192.168.5.1
        lease_time: infinite
        auto_dns: true
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            pool:
              esg_id: <esg resource_id>
```
* For a more complex example see [esg_functionality.yaml](tests/integration/resources/esg_functionality.yaml)

------

### cloudify.nsx.dhcp_binding

Edge DHCP binding.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) Internal ID used in the plugin for working with the object when `use_external_resource` is `true`.
* `bind`:
  * `esg_id`: `resource_id` from [ESG](README.md#cloudifynsxesg).
  * `vm_id`: (optional, case `vm_id`/`vnic_id`) The `VM` managed object Id in vCenter for the `VM` to be attached to this binding entry.
  * `vnic_id`: (optional, case `vm_id`/`vnic_id`) The `VNIC` index for the `VM` interface attached to this binding entry (e.g. vnic0 has index 0).
  * `mac`: (optional, case without `vm_id`/`vnic_id`) The MAC Address of the static binding.
  * `hostname`: The hostname for this static binding.
  * `ip`: The `IP` Address for this static binding.
  * `default_gateway`: (optional) The default gateway for the specified binding.
  * `subnet_mask`: (optional) The subnet mask (e.g. 255.255.255.0) for the specified binding.
  * `domain_name`: (optional) The DNS domain name (e.g. vmware.com) for the specified binding.
  * `dns_server_1`: (optional) The primary DNS Server.
  * `dns_server_2`: (optional) The secondary DNS Server.
  * `lease_time`: (optional) The lease time in seconds, use 'infinite' to disable expiry of DHCP leases.
  * `auto_dns`: (optional) If set to `true`, the DNS servers and domain name set for NSX-Manager will be used.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Internal ID used in the plugin for working with `dhcp_binding`.
* `bind`: Merged copy of `bind`.

**Examples:**

* Simple example:
```yaml
  esg_pool_bind:
    type: cloudify.nsx.dhcp_binding
    properties:
      nsx_auth: <authentication credentials for nsx>
      bind:
        mac: 11:22:33:44:55:66
        hostname: secret.server
        ip: 192.168.5.251
        default_gateway: 192.168.5.1
        subnet_mask: 255.255.255.0
        domain_name: secret.internal.test
        dns_server_1: 8.8.8.8
        dns_server_2: 192.168.5.1
        lease_time: infinite
        auto_dns: true
    interfaces:
      cloudify.interfaces.lifecycle:
        create:
          inputs:
            bind:
              esg_id: <esg resource_id>
```
* For a more complex example see [esg_functionality.yaml](tests/integration/resources/esg_functionality.yaml)

## Common/supplementary functionality

### cloudify.nsx.nsx_object

NSX object check. Search NSX object and set `resource_id` in runtime properties for the object, and `use_external_resource` if the object can be used as an external resource.

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `nsx_object`:
    * `name`: Name of NSX object to check exists.
    * `type`: Type of object. Can be: [tag](README.md#cloudifynsxsecurity_tag), [policy](README.md#cloudifynsxsecurity_policy) and [group](README.md#cloudifynsxsecurity_group) and [lswitch](README.md#cloudifynsxlswitch) or [router](README.md#cloudifynsxdlr).
    * `scopeId`: (optional) Object scope, useful for group search. The default is `globalroot-0`.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `resource_id`: External resource ID if object can be used as external, otherwise `None`.
* `use_external_resource`: `True`, if object can be reused.

**Examples:**

Create tag only in the event that it doesn't exist.

```yaml
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

* For a more complex example, see [esg_with_ospf_functionality.yaml](tests/integration/resources/esg_with_ospf_functionality.yaml).

# Infrastructure tests before deployments
## Check platform example
### Linux example

#### get plugin codebase

```shell
git clone https://github.com/cloudify-cosmo/cloudify-nsx-plugin.git
```

#### Install plugin locally

```shell
pip install -e cloudify-nsx-plugin/
pip install -r cloudify-nsx-plugin/test-requirements.txt
```

#### Inputs for platform tests

```shell
export NSX_IP="<nsx_ip>"
export NSX_USER="<nsx_user>"
export NSX_PASSWORD="<nsx_password>"
export NODE_NAME_PREFIX="<some_free_prefix_for_objects>"
```

#### Cleanup previous results

```shell
rm .coverage -rf
```

#### Check state

```shell
nosetests -v --with-coverage --cover-package=cloudify_nsx cloudify-nsx-plugin/tests/platformtests/ cloudify-nsx-plugin/tests/unittests/
```

### Windows example
Before running the test script, the following applications and components must be installed:
 * Python 2.7.9
 * VCForPython27.msi (```http://aka.ms/vcpython27```)

An example of the test script is located in the ```tests/platformtests/windows_example.ps1``` folder.

## Check total coverage and full functionality
### Get plugin codebase

```shell
git clone https://github.com/cloudify-cosmo/cloudify-nsx-plugin.git
git clone https://github.com/cloudify-cosmo/cloudify-vsphere-plugin.git
```

### Install plugin locally

```shell
pip install -e cloudify-nsx-plugin/
pip install -r cloudify-nsx-plugin/test-requirements.txt

cd cloudify-vsphere-plugin/ && git checkout 2.3.0-m1 && cd ..
pip install -e cloudify-vsphere-plugin/
pip install -r cloudify-vsphere-plugin/test-requirements.txt
```

### Inputs for platform tests
#### NSX

```shell
export NSX_IP="<nsx_ip>"
export NSX_USER="<nsx_user>"
export NSX_PASSWORD="<nsx_password>"
```

#### VCENTER

```shell
export VCENTER_IP="<vcenter_ip>"
export VCENTER_USER="<vcenter_user>"
export VCENTER_PASSWORD="<vcenter_password>"
```

#### Optional vCenter for network checks support

```shell
export VCENTER_DATASTORE="<vcenter_datastore>"
export VCENTER_DATACENTER="<vcenter_datacenter>"
export VCENTER_TEMPLATE="<vcenter_linux_template>"
export VCENTER_CLUSTER="<vcenter_cluster>"
export VCENTER_RESOURCE_POOL="<vcenter_resource_pool>"
```

#### Prefixes

```shell
export NODE_NAME_PREFIX="<some_free_prefix_for_objects>"
```

### Cleanup previous results

```shell
rm .coverage -rf
```

### Check state

```shell
nosetests -v --with-coverage --cover-package=cloudify_nsx cloudify-nsx-plugin/tests/
```

## Examples
For official blueprint examples using this Cloudify plugin, please see [Cloudify Community Blueprints Examples](https://github.com/cloudify-community/blueprint-examples/).

