#!/usr/bin/env python
import os
import sys
import argparse
import logging
import subprocess
from tabulate import tabulate
from ConfigParser import ConfigParser, ParsingError, NoOptionError, NoSectionError
from fabric.colors import green as _green, yellow as _yellow, red as _red
import vagrant

def run_gitmodules():
	sendInfo("Getting the corebooks...")
	subprocess.check_call(['git', 'submodule', 'update', '--init', '--recursive'])

def sendError( message, parser = False ):
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format = _red('%(asctime)-15s %(levelname)s >>>') + '  %(message)s')
	logging.error(_yellow(message))
	if parser:
		parser.print_help()
	sys.exit(1)

def sendInfo( message, parser = False ):
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format = '%(asctime)-15s %(levelname)s >>>  %(message)s')
	logging.info(_green(message))
	if parser:
	    parser.print_help()


def vagrant_command(action):
	config = ConfigParser()
	config.read([os.path.abspath('lib/cheflab.ini')])
	try: 
		vcwd = config.get('default','VAGRANT_CWD')
		vconf = config.get('default','VAGRANT_VAGRANTFILE')
		vdot = config.get('default','VAGRANT_DOTFILE_PATH')
	except (NoSectionError, NoOptionError, ParsingError):
		sendError('Error parsing config file, check "cheflab.ini" under lib' )
		raise 

	values = [["VAGRANT_CWD", vcwd], ["VAGRANT_VAGRANTFILE", vconf], ["VAGRANT_DOTFILE_PATH", vdot]]
	headers=["VAGRANT_ENV", "VALUES"]
	print tabulate(values, headers, tablefmt="fancy_grid", stralign="center")
	print "\n"
	cheflab = vagrant.Vagrant(quiet_stdout=False, quiet_stderr=False)
	os_env = os.environ.copy()
	os_env['VAGRANT_CWD'] = vcwd
	os_env['VAGRANT_VAGRANTFILE'] = vconf
	os_env['VAGRANT_DOTFILE_PATH'] = vdot
	# os_env = os.environ.copy()
	cheflab.env = os_env
	if action == "up":
		run_gitmodules()
		cheflab.up(provision=True)
	elif action == "destroy":
	    cheflab.destroy()
	elif action == "start":
		run_gitmodules()
		cheflab.up()
	elif action == "reload":
		run_gitmodules()
		cheflab.reload()
	elif action == "stop":
		cheflab.halt()
	elif action == "status":
		cheflab.status()
		

def main():
	parser = argparse.ArgumentParser( description='Cheflab CLI', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument( '--loglevel', default='INFO', action='store', help='Loglevel' )
	cheflabopts = parser.add_mutually_exclusive_group(required=True)
	cheflabopts.add_argument('--setup', action='store_true', help='Brings up the Cheflab Server and Cheflab Workstation')
	cheflabopts.add_argument('--start', action='store_true', help='Start the Cheflab Server and Cheflab Workstation')
	cheflabopts.add_argument('--killall', action='store_true', help='Destorys the Cheflab setup')
	cheflabopts.add_argument('--restart', action='store_true', help='Stops the Cheflab Setup')
	cheflabopts.add_argument('--stop', action='store_true', help='Reload the Cheflab Environment')
	cheflabopts.add_argument('--status', action='store_true', help='Status of Cheflab Environment')
	args = parser.parse_args()

	if args.setup:
		print"\n"
		print (_green("Bringing up the Cheflab Environment")) 
		print"\n"
		# run_gitmodules()
		vagrant_command(action="up")
	elif args.killall:
		print"\n"
		print (_red("Destorying the Cheflab Setup"))
		print"\n"
		vagrant_command(action="destroy")
	elif args.start:
		print"\n"
		print (_green("Starting the Cheflab Environment"))
		print"\n"
		vagrant_command(action="start")
	elif args.restart:
		print"\n"
		print (_yellow("Reloading the Cheflab kitchen"))
		print"\n"
		vagrant_command(action="reload")
	elif args.stop:
		print"\n"
		print (_red("Stoping Cheflab Environment"))
		print"\n"
		vagrant_command(action="stop")
	elif args.status:
		print"\n"
		print (_yellow("Status of Cheflab Environment"))
		print"\n"
		vagrant_command(action="status")
	else:
		sendError("Please use the appropiate subcommands")

if __name__ == '__main__':
    # What to do.
    main()
    sys.exit(0)
