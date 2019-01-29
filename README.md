# Summary
This is an Ansible dynamic inventory script for libvirt environment.

This script creates Ansible groups such as

- <VM_NAME>%<NETWORK_NAME>
- <VM_NAME>%<BRIDGE_NAME>
- <VM_NAME>%<VM_INTERFACE_NAME>

each group has only 1 IPv4 address which belongs to the VM on the libvirt network.

For example, when you run a command like
```
ansible -i libvirt_dynamic_inventory.py vm01%default -m ping
```
the script returns an IPv4 address of `vm01` on `default` network.

# Notes
On RHEL/CentOS, you should take care of PolKit (a.k.a PolicyKit) to run the script as non-root user.

First, create a rule file as follows (replace "ori" as your user name):
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
and place the rule file in `/etc/polkit-1/rules.d/`.
The rule file must have '.rules' suffix for its file name.
You might fix SELinux label for the rule file.
```
$ sudo restorecon -R /etc/polkit-1/rules.d/
```
