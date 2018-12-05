# CentOS 7
https://lintut.com/how-to-setup-network-after-rhelcentos-7-minimal-installation/

Set up networking
List Devices with "nmcli d"
Find your Device ID (left col)
run "ifup <device-id>"
Edit /etc/sysconfig/network-scripts/ifcfg-<device-id>
Set ONBOOT=yes

Set up SSH
Get your IP Address with "ip a"
Add entry in SSH config file for the centos7 server
Copy SSH key onto machine
Force using an SSH key instead of password auth
Vi /etc/ssh/sshd_config
PasswordAuthentication no
PermitRootLogin no

Allow for remote sublime usage
Create file /usr/bin/subl with 775 permissions
Past contents of rmate bash version into file

Alow root login without  p/w for users in sudoers file
Visudo
Uncomment "%wheel  ALL=(ALL)    NOPASSWD: ALL"
Add your user to wheel with:
"sudo usermod -a -G wheel <user>"
