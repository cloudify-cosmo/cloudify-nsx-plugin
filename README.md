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
* `resource_id`: Merged copy of `resource_id` if `use_external_resource` or [id](README.md#resource_id) of newly-created object.
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
* For more complicated example look to [security_functionality.yaml](tests/integration/resources/security_functionality.yaml)

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
    * `objectId`: Member ID. Can be another security group or [vm](README.md#resource_id).
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
    * `objectId`: Member ID. Can be another security group or [vm](README.md#resource_id).
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
* `resource_id`: Merged copy of `resource_id` if `use_external_resource` or [id](README.md#resource_id) of newly created object.
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
* `resource_id`: Merged copy of `resource_id` if `use_external_resource` or [id](README.md#resource_id) of newly-created object.
* `tag`: Merged copy of `tag`.

**Relationships**
* `cloudify.nsx.relationships.is_tagged_by`: You can use `is_tagged_by` for attach tag to several vm's without separate
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
    * `vm_id`: vCenter/vSphere VM ID.

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
* `resource_id`: Merged copy of `resource_id` if `use_external_resource` or [id](README.md#resource_id) of newly-created object.
* `switch`: Merged copy of `switch`.
* `vsphere_network_id`: Network ID in vSphere.

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

Distributed Logical Routers

**Derived From:** cloudify.nodes.Root

**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is `true`.
* `router`:
  * `name`: The name that will be assigned to the new dlr.
  * `dlr_pwd`: The admin password of new dlr.
  * `dlr_size`: The DLR Control VM size, possible values: `compact`, `large`, `quadlarge`, `xlarge`.
  * `datacentermoid`: The [vCenter DataCenter ID](README.md#resource_id) where dlr control vm will be deployed.
  * `datastoremoid`: The [vCenter DataStore ID](README.md#resource_id) where dlr control vm will be deployed.
  * `resourcepoolid`: The [vCenter Cluster ID](README.md#resource_id) where dlr control vm will be deployed.
  * `ha_ls_id`: New dlr ha [logical switch](README.md#cloudifynsxlswitch) [id](README.md#resource_id) or vds port group.
  * `uplink_ls_id`: New dlr uplink [logical switch](README.md#cloudifynsxlswitch) [id](README.md#resource_id) or vds port group.
  * `uplink_ip`: New dlr uplink ip.
  * `uplink_subnet`: New dlr uplink subnet.
  * `uplink_dgw`: New dlr default gateway.
* `firewall`:
  * `action`: Default action for firewall, possible: `accept` or `deny`. The default is `accept`.
  * `logging`: Log packages, default `false`.
* `dhcp`:
  * `enabled`: The desired state of the DHCP Server, possible `true` or `false`. The default is `true`.
  * `syslog_enabled`: The desired logging state of the DHCP Server, possible `true` or `false`. The default is `false`.
  * `syslog_level`: The logging level for DHCP on this Edge (`INFO`/`WARNING`/etc.). The default is `INFO`.
* `routing`:
  * `enabled`: The desired state of the routing on device, possible `true` or `false`. The default is `true`.
  * `staticRouting`:
    * `defaultRoute`: (optional, if no default routes needs to be configured).
      * `gatewayAddress`: static ip.
      * `vnic`: uplink nic.
      * `mtu`: (optional) Valid value is smaller than the MTU set on the interface. Default will be the MTU of the interface on which this route is configured.
  * `routingGlobalConfig`:
    * `routerId`: Required when dynamic routing protocols like `OSPF`, or `BGP` is configured.
    * `logging`: (optional) When absent, `enable`=`false` and `logLevel`=`INFO`.
      * `logLevel`: The logging level for routing on this Edge (`INFO`/`WARNING`/etc.). The default is `INFO`.
      * `enabled`: The desired state of the routing logging, possible `true` or `false`. The default is `false`.
      * `ecmp`: (optional) The default is `false`.
* `ospf`: Only one of `OSPF`/`BGP` can be configured as the dynamic routing protocol for Logical Router.
  * `enabled`: When not specified, it will be treated as `false`, When false, it will delete the existing config.
  * `defaultOriginate`: The default is `false`, user can configure edge router to publish default route by setting it to `true`.
  * `gracefulRestart`: (optional) The default is `false`, user can enable graceful restart by setting it to `true`.
  * `redistribution`: (optional) The default is `false`.
  * `protocolAddress`: ipAddress on one of the uplink interfaces, only for enabled and use logical switch as `OSPF`.
  * `forwardingAddress`: ipAddress on the same subnet as the `forwardingAddress`, only for enabled and use logical switch as `OSPF`.
* `bgp`: Only one of `OSPF`/`BGP` can be configured as the dynamic routing protocol for Logical Router.
  * `enabled`: When not specified, it will be treated as `false`, When `false`, it will delete the existing config.
  * `defaultOriginate`: The default is `false`, user can configure edge router to publish default route by setting it to `true`.
  * `gracefulRestart`: (optional) The default is `false`, user can enable graceful restart by setting it to true.
  * `redistribution`: (optional) The default is `false`.
  * `localAS`: Valid values are : 1-65534, For disabled it must to have some number.

**Runtime properties:**
* `nsx_auth`: Merged copy of [nsx_auth](README.md#nsx_auth).
* `use_external_resource`: Merged copy of `use_external_resource`.
* `resource_id`: Merged copy of `resource_id` if `use_external_resource` or [id](README.md#resource_id) of newly-created object.
* `router`: Merged copy of `router`.
* `firewall`: Merged copy of `firewall`.
* `dhcp`: Merged copy of `dhcp`.
* `routing`: Merged copy of `routing`.
* `ospf`: Merged copy of `ospf`.
* `bgp`: Merged copy of `bgp`.
* `uplink_vnic`: vnic id for uplink.

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
* For a more complex example with `BGP` see [dlr_with_bgp_functionality.yaml](tests/integration/resources/dlr_with_bgp_functionality.yaml)

------

### cloudify.nsx.ospf_areas

Distributed Logical Routers interface OSPF areas. Use only after all interfaces creation!

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.ospf_interfaces

Distributed Logical Routers interface OSPF interfaces.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.dlrBGPNeighbour

BGP Neighbour.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.esgBGPNeighbourFilter

BGP Neighbour Filter.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.dlr_routing_ip_prefix

Distributed logical routers interface routing ip prefixes.

Optional. Required only if user wants to define redistribution rules in
dynamic routing protocols like ospf, bgp.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.routing_redistribution_rule

Distributed Logical Routers interface ospf redistribution rule.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.dlr_interface

Distributed Logical Router interface.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.dlr_dhcp_relay

Distributed Router dhcp relay, we need separate type because we can
change it only after set all settings for interfaces.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.dlr_dgw

Distributed Logical Router gateway.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.esg

Edge Services Gateway.

**Derived From:** cloudify.nodes.Root


**Properties:**
* `nsx_auth`: The NSX authentication, [see above](README.md#nsx_auth) for information.
* `use_external_resource`: (optional) Use external object. The default is `false`.
* `resource_id`: (optional) [NSX object ID](README.md#resource_id), used to identify the object when `use_external_resource` is `true`.
* `edge`:
  * `name`: The name of the ESG to be created.
  * `esg_pwd`: The CLI password of the ESG.
  * `esg_size`: The size of the ESG, possible values: `compact`, `large`, `quadlarge`, `xlarge`.
  * `datacentermoid`: The [vCenter DataCenter ID](README.md#resource_id) where dlr control vm will be deployed.
  * `datastoremoid`: The [vCenter DataStore ID](README.md#resource_id) where dlr control vm will be deployed.
  * `resourcepoolid`: The [vCenter Cluster ID](README.md#resource_id) where dlr control vm will be deployed.
  * `default_pg`: The managed object id of the port group for the first vnic (on creation the first vnic must be connected to a valid portgroup in NSX).
  * `esg_username`: The Username for the CLI and SSH access. The default is `admin`.
  * `esg_remote_access`: Enables / Disables SSH access to the Edge Host. The default is `false`.
* `firewall`:
  * `action`: Default action for firewall, possible: `accept` or `deny`. The default is `accept`.
  * `logging`: Log packages, default `false`.
* `dhcp`:
  * `enabled`: The desired state of the DHCP Server, possible `true` or `false`. The default is `true`.
  * `syslog_enabled`: The desired logging state of the DHCP Server, possible `true` or `false`. The default is `false`.
  * `syslog_level`: The logging level for DHCP on this Edge (`INFO`/`WARNING`/etc.). The default is `INFO`.
* `nat`:
  * `enabled`: The desired state of the NAT service, possible `true` or `false`. The default is `true`.

```
      routing:
        default:
          enabled: true
          staticRouting:
            # Optional, if no default routes needs to be configured
            defaultRoute:
              gatewayAddress: ''
              # uplink nic
              vnic: ''
              # Optional. Valid value:smaller than the MTU set on the
              # interface. Default will be the MTU of the interface on
              # which this route is configured
              mtu: ''
          routingGlobalConfig:
            # Required when dynamic routing protocols like OSPF,
            # or BGP is configured
            routerId: ''
            # Optional. When absent, enable=false and logLevel=INFO
            logging:
              logLevel: INFO
              enable: false
            # Optional. Defaults to false.
            ecmp: false
      ospf:
        default:
          # When not specified, it will be treated as false, When false,
          # it will delete the existing config
          enabled: false
          # default is false, user can configure edge router to publish
          # default route by setting it to true.
          defaultOriginate: false
          # default is false, user can enable graceful restart by
          # setting it to true. Its a newly added optional field.
          gracefulRestart: false
          # Optional. Defaults to false.
          redistribution: false
          # ForwardingAddress and protocolAddress are not usable for edge
      # Only one of (OSPF/BGP) can be configured as the dynamic routing
      # protocol for Logical Router.
      bgp:
        default:
          # When not specified, it will be treated as false, When false,
          # it will delete the existing config
          enabled: false
          # default is false, user can configure edge router to publish
          # default route by setting it to true.
          defaultOriginate: false
          # default is false, user can enable graceful restart by
          # setting it to true. Its a newly added optional field.
          gracefulRestart: false
          # Optional. Defaults to false.
          redistribution: false
          # Valid values are : 1-65534
          # For disabled it must be also some number
          localAS: 1
```

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

------

### cloudify.nsx.esgBGPNeighbour

ESG BGP Neighbour.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.esg_nat

Edge Services Gateway NAT.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.esg_firewall

Edge Services Gateways firewall.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.esg_interface

Edge Services Gateway interface.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.esg_gateway

Edge Services Gateway settings.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.esg_route

Edge Services Gateways route.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.dhcp_pool

Edge DHCP pool.

**Derived From:** cloudify.nodes.Root

------

### cloudify.nsx.dhcp_binding

Edge DHCP binding.

**Derived From:** cloudify.nodes.Root

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

* For more complicated example look to [esg_with_ospf_functionality.yaml](tests/integration/resources/esg_with_ospf_functionality.yaml).

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
