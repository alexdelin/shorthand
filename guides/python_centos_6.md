# Setting up Python Envs on CentOS 6

By default, the OS ships with Python Version `2.6.6`, which is too old to be useful for most applications.
We will install arbitrary other versions, and create clean virtualenvs for those new versions.

## Install Proper Parallel Python Versions

This method installs multiple "real" python versions side-by-side,
and you can select which one you use at any point in time via changing
virtualenvs

1. Install GCC and other dependencies
```bash
yum install gcc openssl-devel bzip2-devel
```

2. Download Python Source
```bash
cd /usr/src
wget https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tgz
```

3. Extract Downloaded Source
```bash
tar zxvf Python-2.7.13.tgz
```

4. Install more recent GCC version from devtools 7
```bash
# 1. Install a package with repository for your system:
# On CentOS, install package centos-release-scl available in CentOS repository:
$ sudo yum install centos-release-scl

# On RHEL, enable RHSCL repository for you system:
$ sudo yum-config-manager --enable rhel-server-rhscl-7-rpms

# 2. Install the collection:
$ sudo yum install devtoolset-7

# 3. Start using software collections:
$ scl enable devtoolset-7 bash
```

5. Install from Source
```bash
cd Python-2.7.13
./configure --enable-optimizations
make altinstall

# Test version is accessible
$ python2.7 --version
> Python 2.7.13
```

6. Install Pip into the 2.7 Install
```bash
cd ~
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python2.7 get-pip.py

# In ~/.bash_profile, set:
    export PATH=$PATH:$HOME/bin:$HOME/.local/bin
```

7. Install Virtualenvwrapper into the 2.7 Install
```bash
pip install --user virtualenvwrapper

# In ~/.bash_profile, set:
    export WORKON_HOME=$HOME/.virtualenvs
    export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python2.7
    source $HOME/.local/bin/virtualenvwrapper.sh
```

8. Create a virtualenv using a specific installed Python Version
```bash
mkvirtualenv -p /usr/local/bin/python2.7 fresh27

# To make this env default on login
# In ~/.bash_profile, set:
    workon fresh27
```
