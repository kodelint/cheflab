#!/usr/bin/env python
import os
import sys
import argparse
import logging
import subprocess
from ConfigParser import ConfigParser, ParsingError, NoOptionError, NoSectionError
from fabric.colors import green as _green, yellow as _yellow, red as _red, blue as _blue, cyan as _cyan, magenta as _magenta, white as _white
import vagrant

def run_gitmodules():
	sendInfo("Getting the corebooks...")
	subprocess.check_call(['git', 'submodule', 'update', '--init', '--recursive'])
	subprocess.check_call(['git', 'submodule', 'foreach', 'git', 'pull', 'origin', 'master'])

def sendError( message, parser = False ):
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format = _magenta('%(asctime)-15s %(levelname)s >>>', bold=True) + '  %(message)s')
	logging.error(_red(message))
	if parser:
		parser.print_help()
	sys.exit(1)

def sendWarning( message, parser = False ):
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format = _cyan('%(asctime)-15s %(levelname)s >>>', bold=True) + '  %(message)s')
	logging.warning(_yellow(message))
	if parser:
		parser.print_help()

def sendInfo( message, parser = False ):
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format = _blue('%(asctime)-15s %(levelname)s >>>', bold=True) + '  %(message)s')
	logging.info(_green(message))
	if parser:
	    parser.print_help()

def read_conf():
	import yaml
	with open("hosts/hosts.yml", 'r') as fp:
		data = yaml.safe_load(fp)
	
	return data

def get_keys(conf):
	from shutil import copy
	for vm in conf:
		sendInfo("Getting Keys for: " + vm["name"])
		src = "boxes/machines/" + vm["name"] + "/virtualbox/private_key"
		dest = "provisioner/conf/keys/" + vm["name"] + ".pem"
		copy(src, dest)

def destory_config(conf):
	import os
	for vm in conf:
		sendWarning("Removing stale Keys for: " + vm["name"])
		dest = "provisioner/conf/keys/" + vm["name"] + ".pem"
		os.remove(dest)
	
	cfg = "provisioner/conf/cache/cheflab-hosts.cfg"
	sendWarning("Removing stale hosts file : " + cfg)
	os.remove(cfg)

def write_file(fp, ip, fqdn, hostname):
	fp = open(fp, 'a')
	fp.write(ip)
	fp.write("\t")
	fp.write(fqdn)
	fp.write("\t")
	fp.write(hostname)
	fp.write("\n")
	fp.close()

def generate_hostsfile(conf):
	import os.path
	cheflabfile = "provisioner/conf/cache/cheflab-hosts.cfg"
	sendInfo("Generating hosts file")
	s = []
	if os.path.isfile(cheflabfile):
		with open(cheflabfile) as f:
			for line in f:
				s.append(line.strip().split("\t"))

		for vm, index in zip(conf, s):
		  fqdn = vm["name"] + ".cheflab.dev"
		  if fqdn == index[1]:
		  	pass
		  else:
		  	sendInfo("Adding host entry for: " + _white(fqdn))
		  	write_file(cheflabfile, vm["ip"], fqdn, vm["name"])
	else:
		for vm in conf:
			fqdn = vm["name"] + ".cheflab.dev"
			sendInfo("Adding host entry for: " + _white(fqdn))
		  	write_file(cheflabfile, vm["ip"], fqdn, vm["name"])


def vagrant_command(action, vm_name):
	config = ConfigParser()
	config.read([os.path.abspath('lib/cheflab.ini')])
	try: 
		vcwd = config.get('default','VAGRANT_CWD')
		vconf = config.get('default','VAGRANT_VAGRANTFILE')
		vdot = config.get('default','VAGRANT_DOTFILE_PATH')
	except (NoSectionError, NoOptionError, ParsingError):
		sendError('Error parsing config file, check "cheflab.ini" under lib' )
		raise 


	cheflab = vagrant.Vagrant(quiet_stdout=False, quiet_stderr=False)
	os_env = os.environ.copy()
	os_env['VAGRANT_CWD'] = vcwd
	os_env['VAGRANT_VAGRANTFILE'] = vconf
	os_env['VAGRANT_DOTFILE_PATH'] = vdot
	# os_env = os.environ.copy()
	cheflab.env = os_env
	conf = read_conf()
	if action == "up":
		run_gitmodules()
		cheflab.up(provision=True, vm_name=vm_name)
		get_keys(conf)
		sys.exit(0)
	elif action == "destroy":
	    cheflab.destroy(vm_name=vm_name)
	    destory_config(conf)
	    sys.exit(0)
	elif action == "start":
		run_gitmodules()
		cheflab.up(vm_name=vm_name)
		sys.exit(0)
	elif action == "reload":
		run_gitmodules()
		cheflab.reload(vm_name=vm_name)
		sys.exit(0)
	elif action == "stop":
		cheflab.halt(vm_name=vm_name)
		sys.exit(0)
	elif action == "ssh":
		cheflab.ssh(vm_name=vm_name)
		sys.exit(0)
	elif action == "status":
		servers = cheflab.status(vm_name=vm_name)
		for server in servers:
			sendInfo ("Server Name: " + _yellow(server.name) + " Server Status: " + _yellow(server.state))

		sys.exit(0)
	elif action == "validate_vms":
		grabinfo = []
		servers = cheflab.status(vm_name=vm_name)
		for server in servers:
			grabinfo.append(server.name)
        
        return grabinfo
		

def main():
	os.environ['COLUMNS'] = '120'
	vms = vagrant_command(action="validate_vms", vm_name=None)
	parser = argparse.ArgumentParser( description='Cheflab CLI', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	cheflabopts = parser.add_mutually_exclusive_group(required=True)
	cheflabopts.add_argument('--setup', action='store_true', help='Brings up the Cheflab Server and Cheflab Workstation')
	cheflabopts.add_argument('--start', action='store_true', help='Start the Cheflab Server and Cheflab Workstation')
	cheflabopts.add_argument('--kill', action='store_true', help='Destorys the Cheflab setup')
	cheflabopts.add_argument('--restart', action='store_true', help='Stops the Cheflab Setup')
	cheflabopts.add_argument('--stop', action='store_true', help='Reload the Cheflab Environment')
	cheflabopts.add_argument('--status', action='store_true', help='Status of Cheflab Environment')
	cheflabopts.add_argument('--ssh', action='store_true', help='Status of Cheflab Environment')
	vmopts = parser.add_argument_group('Vagrant VM Options')
	vmopts.add_argument('--vm', choices=vms, default=None, action='store', required=False, help='Vagrant VM Name')
	args = parser.parse_args()
	vm_name=args.vm

	if args.setup:
		sendInfo("Bringing up Cheflab Environment ")
		conf = read_conf()
		generate_hostsfile(conf)
		vagrant_command(action="up", vm_name=vm_name)
	elif args.kill:
		sendWarning("Destorying Cheflab Setup ")
		vagrant_command(action="destroy", vm_name=vm_name)
	elif args.start:
		sendInfo("Starting Cheflab Environment ")
		vagrant_command(action="start", vm_name=vm_name)
	elif args.restart:
		sendWarning(_yellow("Reloading Cheflab kitchen"))
		vagrant_command(action="reload", vm_name=vm_name)
	elif args.stop:
		sendWarning("Stoping Cheflab Environment")
		vagrant_command(action="stop", vm_name=vm_name)
	elif args.status:
		sendInfo(_yellow("Status of Cheflab Environment"))
		vagrant_command(action="status", vm_name=vm_name)
	elif args.ssh:
		sendInfo(_yellow("Login to Cheflab Environments"))
		vagrant_command(action="ssh", vm_name=vm_name)
	else:
		sendError("Please use the appropiate subcommands")

if __name__ == '__main__':
    # What to do.
    main()
    sys.exit(0)
