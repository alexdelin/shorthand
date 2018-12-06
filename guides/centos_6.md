# CentOS 6 VM Setup Instructions

## (IF NEEDED) Wipe the interface config

## Create a non-root user if necessary
Issue the useradd command to create a locked user account:
```bash
$ useradd <username>
```
Unlock the account by issuing the passwd command to assign a password and set password aging guidelines:
```bash
$ passwd <username>
```

## Make interface work on boot
Edit `/etc/sysconfig/network-scripts/ifcfg-eth0`
Set `ONBOOT=yes`

## Open all needed ports
`vi /etc/sysconfig/iptables`
Set:
```
-A INPUT -m state --state NEW -m tcp -p tcp --dport 22 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 81 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 443 -j ACCEPT
```

## Disable ipv6 completely at kernel level
`vi /etc/sysctl.conf`
Set:
```
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.all.disable_ipv6 = 1
```

## Disable SELinix
`vi /etc/selinux/config`
Set:
```
SELINUX=disabled
```

## Copy your SSH Keys onto the VM
```bash
ssh-copy-id -i <identity-file> <user>@<host>
```

## Add a new SSH Config entry for the new VM
```sshconfig
Host centos
  Hostname 172.16.32.128
  User centos
  IdentitiesOnly yes
  IdentityFile ~/.ssh/id_rsa
  RemoteForward 127.0.0.1:52698 127.0.0.1:52698
```

## Force using an SSH key instead of password auth
`vi /etc/ssh/sshd_config`
Set:
```
PasswordAuthentication no
PermitRootLogin no
```

## Alow root login without  p/w for users in the group `wheel`
`$ Visudo`
Uncomment:
```
%wheel  ALL=(ALL)    NOPASSWD: ALL
```

## Add your user to wheel
```bash
$ sudo usermod -a -G wheel <user>
```

## Allow for remote text editor usage
Create file `/usr/bin/subl` with `775` permissions
Past contents of rmate bash version into file
```bash
sudo wget -O /usr/bin/subl https://raw.githubusercontent.com/aurora/rmate/master/rmate
chmod 775 /usr/bin/subl
```

## Install clean Python version
```bash
sudo yum update # update yum
sudo yum install centos-release-scl # install SCL
sudo yum install python27 # install Python 2.7
scl enable python27 bash # Activate
```

