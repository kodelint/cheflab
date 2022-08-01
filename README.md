### Cheflab
***

#### Background:

When I started working with [chef](www.chef.io), besides all greatness I was scared of touching the **PROD** environment because of the lack on experience in _chef_. I always thought if there was anything like **lab** which I can use to teach myself and do all sorts of mombo-jambo.

That's what drove me to work on this project.

##### Why [cheflab](https://github.com/kodelint/cheflab) is different from [test-kitchen](http://kitchen.ci):

[test-kitchen](http://kitchen.ci) is great to test recipes and using **chef-solo** or **chef-zero**. As quoted:
>Test Kitchen is an integration tool for developing and testing infrastructure code and software on isolated target platforms.


[cheflab](https://github.com/kodelint/cheflab) give you the opportunity to run full stack chef environment on your _laptop_ and mimic the full deployment life cycle.

##### Dependencies:

- [Vagrant](https://www.vagrantup.com/)
- [chef-core](https://downloads.chef.io/chef-server/)
- [chef-dk](https://downloads.chef.io/chef-dk/)
- [python-vagrant](https://pypi.python.org/pypi/python-vagrant)

##### Components for [cheflab](https://github.com/kodelint/cheflab):

|        Components     |                       Usages                        |
|-------------|-----------------------------------------------|
| `provisioner/Config.cfg`|contains the core configuration for [cheflab](https://github.com/kodelint/cheflab)                           |
| `hosts/hosts.yml` |  host definitions and customizations     |
| `bin/cheflab.py`         | script to _setup/destroy/stop/start/login_ |
| `boxes/**`    | contains the actual `vagrant` machines                        |
| `provisioner/conf/setup.sh` | used for final `cheflab-workstation` setup|
|`corebooks` | contains **chef recipes** [chef_server](https://github.com/kodelint/chef_server.git) and [chef_workstation](https://github.com/kodelint/chef_workstation.git)|

##### How to use [cheflab](https://github.com/kodelint/cheflab):

Everything is drives by `bin/cheflab.py` script

```
python bin/cheflab.py --help
usage: cheflab.py [-h] (--setup | --start | --kill | --restart | --stop | --status | --ssh)
                  [--vm {cheflab-server,cheflab-workstation}]

Cheflab CLI

optional arguments:
  -h, --help            show this help message and exit
  --setup               Brings up the Cheflab Server and Cheflab Workstation (default: False)
  --start               Start the Cheflab Server and Cheflab Workstation (default: False)
  --kill                Destroys the Cheflab setup (default: False)
  --restart             Stops the Cheflab Setup (default: False)
  --stop                Reload the Cheflab Environment (default: False)
  --status              Status of Cheflab Environment (default: False)
  --ssh                 Status of Cheflab Environment (default: False)

Vagrant VM Options:
  --vm {cheflab-server,cheflab-workstation}
                        Vagrant VM Name (default: None)
```
**Note**: [cheflab](https://github.com/kodelint/cheflab) assumes that core nodes will be **cheflab-server** and **cheflab-workstation**.


- if you need to add additional nodes like `cheflab-client`, you can add it to `hosts/hosts.yml`

###### default: `hosts/hosts.yml`

```
---
- name: cheflab-server
  box: bento/ubuntu-14.04
  ram: 1512
  ip: 192.168.38.31
  share: true
  default_share: true
  share_keys: false
  cheflab_shared_conf: "conf"
- name: cheflab-workstation
  box: bento/ubuntu-14.04
  ram: 512
  ip: 192.168.38.32
  share: true
  default_share: true
  cookbooks: "~/Google Drive/Personal/Chef"
  cookbook_share: false
  share_keys: false
  cheflab_shared_conf: "conf"
```
One can add additional node definition to this file and it will be populated.

######Keys Variables:
|        Variables     |    Value                   | Usages  |Required |
|-------------|--------------------|--------------------------|----|
| default_share |`true` or `false`| disable or enables `/vagrant` share on guest|No|
| share_keys |`true` or `false`| disable or enables exposing `vagrant` ssh keys to guest|Yes|
| cheflab_shared_conf |`true` or `false`| disable or enables exposing `cheflab` related configs on guest|Yes|
| cookbooks || make chef recipes on host available on guest `cheflab-workstation`|No|

##### Usage:
###### Setup:
```
$ python bin/cheflab.py --setup

2016-09-21 12:35:05,050 INFO >>>  Bringing up Cheflab Environment
2016-09-21 12:35:05,053 INFO >>>  Generating hosts file
2016-09-21 12:35:05,053 INFO >>>  Adding host entry for: cheflab-server.cheflab.dev
2016-09-21 12:35:05,053 INFO >>>  Adding host entry for: cheflab-workstation.cheflab.dev
2016-09-21 12:35:05,058 INFO >>>  Getting the corebooks...
...
...
Bringing machine 'cheflab-server' up with 'virtualbox' provider...
Bringing machine 'cheflab-workstation' up with 'virtualbox' provider...
...
...
==> cheflab-server: Mounting shared folders...
==>  cheflab-server: /cheflab/conf => cheflab/provisioner/conf
...
...
==> cheflab-server: Running provisioner: chef_solo...
    cheflab-server: Installing Chef (latest)...
==> cheflab-server: Generating chef JSON and uploading...
==> cheflab-server: Running chef-solo...
...
...
==> cheflab-server: Starting Chef Client, version 12.14.77
==> cheflab-server: [2016-09-21T19:36:40+00:00] INFO: *** Chef 12.14.77 ***
==> cheflab-server: [2016-09-21T19:36:40+00:00] INFO: Platform: x86_64-linux
==> cheflab-server: [2016-09-21T19:36:40+00:00] INFO: Chef-client pid: 1813
...
...
==> cheflab-server: Synchronizing Cookbooks:
...
...
README.md in the cache.
==> cheflab-server:
==> cheflab-server: - chef_server (0.1.1)
==> cheflab-server: Installing Cookbook Gems:
==> cheflab-server: Compiling Cookbooks...
==> cheflab-server: Converging 8 resources
==> cheflab-server: Recipe: chef_server::server
==> cheflab-server:
==> cheflab-server: * remote_file[/var/chef/cache/chef-server-core_12.8.0-1_amd64.deb] action create
...
...
==> cheflab-server: Running handlers:
==> cheflab-server: [2016-09-21T20:15:32+00:00] INFO: Running report handlers
==> cheflab-server: Running handlers complete
==> cheflab-server:
==> cheflab-server: [2016-09-21T20:15:32+00:00] INFO: Report handlers complete
==> cheflab-server: Chef Client finished, 8/9 resources updated in 13 minutes 48 seconds
...
...
==> cheflab-workstation: Importing base box 'bento/ubuntu-14.04'...
==> cheflab-workstation: Matching MAC address for NAT networking...
==> cheflab-workstation: Checking if box 'bento/ubuntu-14.04' is up to date...
==> cheflab-workstation: Setting the name of the VM: provisioner_cheflab-workstation_1474488943335_99497
==> cheflab-workstation: Using hostname "cheflab-workstation.cheflab.dev" as node name for Chef...
==> cheflab-workstation: Fixed port collision for 22 => 2222. Now on port 2200.
...
...
==> cheflab-workstation: [2016-09-21T20:19:43+00:00] INFO: Report handlers complete
==> cheflab-workstation: Chef Client finished, 5/5 resources updated in 02 minutes 36 seconds
2016-09-21 13:19:48,149 INFO >>>  Getting Keys for: cheflab-server
2016-09-21 13:19:48,149 INFO >>>  Getting Keys for: cheflab-workstation
```
######Status:
```
$ python bin/cheflab.py --status
2016-09-21 12:43:12,056 INFO >>>  Status of Cheflab Environment
2016-09-21 12:43:24,532 INFO >>>  Server Name: cheflab-server Server Status: running
2016-09-21 12:43:24,532 INFO >>>  Server Name: cheflab-workstation Server Status: running
```


You can perform operation on individual nodes as well with `--vm` options

```
$ python bin/cheflab.py --status --vm cheflab-server
2016-09-21 12:45:35,271 INFO >>>  Status of Cheflab Environment
2016-09-21 12:45:38,494 INFO >>>  Server Name: cheflab-server Server Status: running
```

######login:
```
$ python bin/cheflab.py --ssh --vm cheflab-server
2016-09-21 12:47:15,779 INFO >>>  Login to Cheflab Environments
Welcome to Ubuntu 14.04.4 LTS (GNU/Linux 3.13.0-92-generic x86_64)

* Documentation:  https://help.ubuntu.com/
vagrant@cheflab-server:~$
```
**screenshot**:
###### Setup:
![Alt text](screenshots/cheflab-setup.png?raw=true "cheflab Setup")

###### Chef Run:
![Alt text](screenshots/chefrun.png?raw=true "chef run")

###### Chaflab Status:
![Alt text](screenshots/cheflab-status.png?raw=true "cheflab status")

###### login:
![Alt text](screenshots/cheflab-login.png?raw=true "cheflab status")

###### cheflab-workstation setup:
![Alt text](screenshots/final-setup.png?raw=true "cheflab status")


[cheflab](https://github.com/kodelint/cheflab) is presently on a very early stage of development. There are lot of hacks in place to achieve the target. Here are some todo in the list:

##### To-Do:

1. create `cheflab` modules
2. convert the `cheflab.py` in more modular
3. eliminate one additional step of configuring `cheflab-workstation`
