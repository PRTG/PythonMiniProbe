#!/usr/bin/env python
#Copyright (c) 2014, Paessler AG <support@paessler.com>
#All rights reserved.
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions
# and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
# and the following disclaimer in the documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse
# or promote products derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### Quick and Dirty Setup Script for the Mini Probe
import sys
import os
import time
import subprocess
import uuid

class bcolor:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'

probe_conf = {}
if sys.version_info < (2, 7):
    print bcolor.RED + "Python version too old! Please install at least version 2.7" + bcolor.END
    print "Exiting"
    sys.exit(2)


def file_check(check_path):
    # Check if a give file exists
    return os.path.exists(check_path)


def file_create(create_path):
    # Creates a given file and writes some startup information to it
    with open(create_path, 'w') as f:
        f.write("###Mini Probe Config File\n")
        f.close()


def write_config(config):
    conf = ""
    with open(path, 'a') as f:
        for key in config:
            conf += "%s:%s\n" % (key, config[key])
        f.write(conf)
    f.close()
    print bcolor.GREEN + "Config file successfully written!" + bcolor.END


def write_file(write_path, content):
    with open(write_path, 'w') as f:
        f.write(content)
    f.close()


def logrotation(rotation_path):
    rotate_tpl = open("./scripts/rotate.tpl")
    return rotate_tpl.read() % rotation_path


def init_script(script_path, user):
    init_script_tpl = open("./scripts/probe.tpl")
    return init_script_tpl.read() % (script_path, user)

def get_config_user(default="root"):
    tmpUser = "%s" % str(raw_input(bcolor.GREEN + "Please provide the username the script should run under [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpUser == "":
        return tmpUser
    else:
	return default

def get_config_name(default="Python MiniProbe"):
    tmpName = "%s" % str(raw_input(bcolor.GREEN + "Please provide the desired name of your Mini Probe [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpName == "":
        return tmpName
    else:
        return default

def get_config_gid(default=str(uuid.uuid4())):
    tmpGid = "%s" % str(raw_input(bcolor.GREEN + "Please provide the Probe GID [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpGid == "":
        return tmpGid
    else:
        return default

def get_config_ip(default=""):
    tmpIP = "%s" % str(raw_input(bcolor.GREEN + "Please provide the IP/DNS name of the PRTG Core Server [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpIP == "":
	response = os.system("ping -c 1 " + tmpIP  + " > /dev/null")
	if not response == 0:
	    print bcolor.YELLOW + "PRTG Server can not be reached. Please make sure the server is reachable." + bcolor.END
	    go_on = "%s" % str(raw_input(bcolor.YELLOW + "Do you still want to continue using this server [y/N]: " + bcolor.END)).rstrip().lstrip()
            if not go_on == "y":
	        return get_config_ip()
	return tmpIP
    else:
	print bcolor.YELLOW + "You have not provided an IP/DNS name of the PRTG Core Server." + bcolor.END
	return get_config_ip()

def get_config_port(default="443"):
    tmpPort = "%s" % str(raw_input(bcolor.GREEN + "Please provide the port the PRTG web server is listening to (IMPORTANT: Only SSL is supported)[" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpPort == "":
        return tmpPort 
    else:
        return default

def get_config_base_interval(default="60"):
    tmpInterval = "%s" % str(raw_input(bcolor.GREEN + "Please provide the base interval for your sensors [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpInterval == "":
        return tmpInterval 
    else:
        return default

def get_config_access_key(default=""):
    tmpAccessKey = "%s" % str(raw_input(bcolor.GREEN + "Please provide the Probe Access Key as defined on the PRTG Core [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpAccessKey == "":
        return tmpAccessKey
    else:
	print bcolor.YELLOW + "You have not provided the Probe Access Key as defined on the PRTG Core." + bcolor.END
        return get_config_access_key()

def get_config_path(default=os.path.dirname(os.path.abspath(__file__))):
    tmpPath = "%s" % str(raw_input(bcolor.GREEN + "Please provide the path where the probe files are located [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpPath == "":
        return tmpPath
    else:
        return default

def get_config_clean_memory(default=""):
    tmpCleanMem = "%s" % str(raw_input(bcolor.GREEN + "Do you want the mini probe flushing buffered and cached memory [y/N]: " + bcolor.END)).rstrip().lstrip()
    if tmpCleanMem.lower() == "y":
        return "True"
    else:
        return "False"

#For future use
def get_config_announced(default="0"):
    return "0"

#For future use
def get_config_protocol(default="1"):
    return "1"

#For future use
def get_config_debug(default=""):
    tmpDebug = "%s" % str(raw_input(bcolor.GREEN + "Do you want to enable debug logging (" + bcolor.YELLOW + "can create massive logfiles!" + bcolor.GREEN + ") [y/N]: " + bcolor.END)).rstrip().lstrip()
    if tmpDebug.lower() == "y":
	tmpDebug1 = "%s" % str(raw_input(bcolor.YELLOW + "Are you sure you want to enable debug logging? This will create massive logfiles [y/N]: " + bcolor.END)).rstrip().lstrip()
	if tmpDebug1.lower() == "y":
            return "True"
	else:
	    return "False"
    else:
        return "False"

def get_config():
    print ""
    print bcolor.YELLOW + "Checking for necessary modules and Python Version" + bcolor.END
    try:
        sys.path.append('./')
        import hashlib
        import string
        import json
        import socket
        import importlib
        import requests
        import pyasn1
        import pysnmp
    except Exception, e:
        print "%s.Please install the same" % e
        print "Exiting"
        sys.exit(1)
    print bcolor.GREEN + "Successfully imported modules." + bcolor.END
    print ""
    try:
        probe_user = get_config_user()
        probe_conf['name'] = get_config_name()
        probe_conf['gid'] = get_config_gid()
        probe_conf['server'] = get_config_ip()
        probe_conf['port'] = get_config_port()
        probe_conf['baseinterval'] = get_config_base_interval()
        probe_conf['key'] = get_config_access_key()
        probe_path = get_config_path()
        probe_conf['cleanmem'] = get_config_clean_memory()
        probe_conf['announced'] = get_config_announced()
        probe_conf['protocol'] = get_config_protocol()
        probe_conf['debug'] = get_config_debug()
	print ""
        file_create(path)
        write_config(probe_conf)
        logpath = "%s/logs" % probe_path
        if not (file_check(logpath)):
            os.makedirs(logpath)
        path_rotate = "/etc/logrotate.d/MiniProbe"
        path_init = "/etc/init.d/probe.sh"
        print bcolor.GREEN + "Creating Logrotation Config" + bcolor.END
        write_file(path_rotate, logrotation(probe_path))
        print bcolor.GREEN + "Setting up runlevel" + bcolor.END
        write_file(path_init, init_script(probe_path, probe_user))
        print bcolor.GREEN + "Changing File Permissions" + bcolor.END
        os.chmod('%s/probe.py' % probe_path, 0755)
        os.chmod('/etc/init.d/probe.sh', 0755)
	return True
    except Exception, e:
        print bcolor.RED + "%s. Exiting!" % e + bcolor.END
        return False

def remove_config():
    try:
	print subprocess.call("/etc/init.d/probe.sh stop", shell=True)
	os.remove('/etc/init.d/probe.sh')
	os.remove('/etc/logrotate.d/MiniProbe')
	os.remove('./probe.conf')
    except Exception, e:
        print "%s. Exiting!" % e
        return False

if __name__ == '__main__':
    conf_avail = False
    if not os.getuid() == 0:
        print bcolor.RED + "You must run me as root user!" + bcolor.END
        print bcolor.RED + "Rerun me with sudo " + __file__ + bcolor.END
    print ""
    print bcolor.CYAN + "Welcome to the Miniprobe (Python) for PRTG installer" + bcolor.END
    path = './probe.conf'
    if file_check(path):
        print ""
        probe_config_exists = "%s" % str(raw_input(bcolor.YELLOW + "A config file was already found. Do you want to reconfigure [y/N]: " + bcolor.END)).rstrip().lstrip()
        if probe_config_exists == "y":
	    get_config()
	else:
	    print ""
            uninstall = "%s" % str(raw_input(bcolor.YELLOW + "Do you want to Uninstall or Restart the service [u/R]: " + bcolor.END)).rstrip().lstrip()
	    if uninstall == "u":
		remove_config()
		conf_avail = False
	    else:
		conf_avail = True
    else:
	conf_avail = get_config()
    if conf_avail:
        print subprocess.call("update-rc.d probe.sh defaults", shell=True)
        print bcolor.GREEN + "Starting Mini Probe" + bcolor.END
        print subprocess.call("/etc/init.d/probe.sh start", shell=True)
        print bcolor.GREEN + "Done. You now can start/stop the Mini Probe using '/etc/init.d/probe.sh start' or '/etc/init.d/probe.sh stop'" + bcolor.END
    else:
        print "Exiting!"
        sys.exit()