# Summary
This is an Ansible dynamic inventory script for libvirt environment.

The script creates Ansible groups such as

- `VM_NAME` % `NETWORK_NAME`
- `VM_NAME` % `BRIDGE_NAME`
- `VM_NAME` % `VM_INTERFACE_NAME`

each group has only 1 IPv4 address which belongs to the VM on the libvirt network.

I assume some use cases like "Hey, I've just created a VM using virt-intall. I know the name of the VM, the name of the network to which the VM connects, but it's too much hassle to know the IP address of the VM."
If you are in the case, run ansible like this!
```
$ ansible -i libvirt_dynamic_inventory.py osp13-undercloud%default -m debug -a 'msg={{ ipv4addr }} -k'
SSH password:
192.168.122.223 | SUCCESS => {
    "msg": "192.168.122.223"
}
```

# Group Examples
## Case 1
```
$ ansible -i libvirt_dynamic_inventory.py vm01%default -m ping
```
connects to an IPv4 address of `vm01` on `default` network.

## Case 2
```
$ ansible -i libvirt_dynamic_inventory.py vm01%virbr0 -m ping
```
connects to an IPv4 address of `vm01` on `virbr0` bridge.

## Case 3
```
$ ansible -i libvirt_dynamic_inventory.py vm01%eth0 -m ping
```
connects to an IPv4 address of `eth0` on `vm01`.

# Notes
On RHEL/CentOS, you should take care of PolKit (a.k.a PolicyKit) to run the script as non-root user.

First, create a rule file as follows (replace `"ori"` to your user name).
```
polkit.addRule(function(action, subject) {
        if (action.id == "org.libvirt.unix.manage" &&
            subject.user == "ori") {
                return polkit.Result.YES;
                polkit.log("action=" + action);
                polkit.log("subject=" + subject);
        }
});
```
Then place the rule file in `/etc/polkit-1/rules.d/`.
The rule file must have '.rules' suffix for its file name.
You might fix SELinux label for the rule file.
```
$ sudo restorecon -R /etc/polkit-1/rules.d/
```
