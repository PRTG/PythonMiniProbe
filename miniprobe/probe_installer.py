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
config_old = {}
config_old['name'] = "Python MiniProbe"
config_old['gid'] = str(uuid.uuid4())
config_old['server'] = ""
config_old['port'] = "443"
config_old['baseinterval'] = "60"
config_old['key'] = ""
config_old['cleanmem'] = ""
config_old['announced'] = "0"
config_old['protocol'] = "1"
config_old['debug'] = ""
config_old['subprocs'] = "10"

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


def read_config(path):
    """
    read configuration file and write data to dict
    """
    config = {}
    try:
        conf_file = open(path)
        for line in conf_file:
            if not (line == '\n'):
                if not (line.startswith('#')):
                    config[line.split(':')[0]] = line.split(':')[1].rstrip()
        conf_file.close()
        return config
    except Exception as read_error:
        print bcolor.RED + "No config found! Error Message: %s Exiting!" + bcolor.END % read_error 
        sys.exit()

def init_script(script_path, user):
    init_script_tpl = open("./scripts/probe.tpl")
    return init_script_tpl.read() % (script_path, user)

def write_load_list(ds18b20_sensors, other_sensors):
    default_sensors = "Ping,HTTP,Port,SNMPCustom,CPULoad,Memory,Diskspace,SNMPTraffic,CPUTemp,Probehealth,External_IP,aDNS,APT,NMAP"
    if not (other_sensors == ""):
        default_sensors = default_sensors + "," + other_sensors
    f=open("./sensors/__init__.py","a")
    f.write("#Copyright (c) 2014, Paessler AG <support@paessler.com>\n")
    f.write("#All rights reserved.\n")
    f.write("#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the\n")
    f.write("# following conditions are met:\n")
    f.write("#1. Redistributions of source code must retain the above copyright notice, this list of conditions\n")
    f.write("# and the following disclaimer.\n")
    f.write("#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions\n")
    f.write("# and the following disclaimer in the documentation and/or other materials provided with the distribution.\n")
    f.write("#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse\n")
    f.write("# or promote products derived from this software without specific prior written permission.\n")
    f.write("\n")
    f.write("#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES,\n")
    f.write("# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR\n")
    f.write("# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,\n")
    f.write("# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,\n")
    f.write("# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)\n")
    f.write("# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,\n")
    f.write("# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,\n")
    f.write("# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.\n")
    f.write("\n")
    f.write("# Announce modules available in this package\n")
    f.write("# Just extend this list for your modules and they will be automatically imported during runtime and\n")
    f.write("# are announced to the PRTG Core\n")
    f.write("__all__ = " + str(default_sensors.split(",")) + "\n")
    if not (ds18b20_sensors == ""):
        f.write("DS18B20_sensors = " + str(ds18b20_sensors.split(",")) + "\n")
    f.close()

def install_w1_module():
    print bcolor.YELLOW + "Checking the hardware for Raspberry Pi." + bcolor.END
    if os.uname()[4][:3] == 'arm':
        print bcolor.GREEN + "Found hardware matching " + os.uname()[4][:3] + bcolor.END
        tmpUseRaspberry = "%s" % str(raw_input(bcolor.GREEN + "Do you want to enable the Raspberry Pi temperature sensor [y/N]: " + bcolor.END)).rstrip().lstrip()
        if tmpUseRaspberry.lower() == "y":
            try:
                install_kernel_module()
                return True
            except Exception, e:
                print "%s.Please install the same" % e
                print "Exiting"
                sys.exit(1)
        else:
            return False
    else:
        print bcolor.RED + "Found hardware matching " + os.uname()[4][:3] + bcolor.END
        return False

def install_kernel_module():
    print bcolor.GREEN + "Checking for w1-gpio line in /boot/config.txt" + bcolor.END
    found = False
    f = open('/boot/config.txt','r')
    for line in f.readlines():
        if line.strip() == 'dtoverlay=w1-gpio':
            print bcolor.GREEN + "Found dtoverlay line. Skipping install of w1-gpio" + bcolor.END
            found = True
    f.close()
    if not found:
        print bcolor.GREEN + "Line not found. Now adding the dtoverlay line to /boot/config.txt" + bcolor.END
        f = open('/boot/config.txt','a')
        f.write('\n#w1-gpio added by PRTG MiniProbe install script\n')
        f.write('dtoverlay=w1-gpio')
        f.close()
        print bcolor.GREEN + "Please restart the installscript after the Raspberry Pi has been rebooted!" + bcolor.END
        print bcolor.GREEN + "Now rebooting..." + bcolor.END
        print subprocess.call("reboot", shell=True)
        sys.exit(2)

def get_w1_sensors():
    sensors = ""
    tmpSens = ""
    print bcolor.GREEN + "Finding all W1 sensors" + bcolor.END
    f = open('/sys/devices/w1_bus_master1/w1_master_slaves','r')
    for line in f.readlines():
        print bcolor.GREEN + "Found: " + bcolor.YELLOW + line[3:].strip() + bcolor.END
        sensors = sensors + "," + line[3:].strip()
    f.close()
    sens = "%s" % str(raw_input(bcolor.GREEN + "Please enter the id's of the temperature sensors you want to use from the list above, seperated with a , [" + sensors[1:] + "]: " + bcolor.END)).rstrip().lstrip()
    if not sens == "":
        return sens
    else:
        return sensors[1:]

def get_config_user(default="root"):
    tmpUser = "%s" % str(raw_input(bcolor.GREEN + "Please provide the username the script should run under [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpUser == "":
        return tmpUser
    else:
        return default

def get_config_name(default):
    tmpName = "%s" % str(raw_input(bcolor.GREEN + "Please provide the desired name of your Mini Probe [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpName == "":
        return tmpName
    else:
        return default

def get_config_gid(default):
    tmpGid = "%s" % str(raw_input(bcolor.GREEN + "Please provide the Probe GID [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpGid == "":
        return tmpGid
    else:
        return default

def get_config_ip(default):
    tmpIP = "%s" % str(raw_input(bcolor.GREEN + "Please provide the IP/DNS name of the PRTG Core Server [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not (tmpIP == "") or not (default == ""):
        if (tmpIP == "") and not (default == ""):
            tmpIP = default
        response = os.system("ping -c 1 " + tmpIP + " > /dev/null")
        if not response == 0:
            print bcolor.YELLOW + "PRTG Server can not be reached. Please make sure the server is reachable." + bcolor.END
            go_on = "%s" % str(raw_input(bcolor.YELLOW + "Do you still want to continue using this server [y/N]: " + bcolor.END)).rstrip().lstrip()
            if not go_on.lower() == "y":
                return get_config_ip()
        else:
            print bcolor.GREEN + "PRTG Server can be reached. Continuing..." + bcolor.END
            return tmpIP
    else:
        print bcolor.YELLOW + "You have not provided an IP/DNS name of the PRTG Core Server." + bcolor.END
        return get_config_ip()

def get_config_port(default):
    tmpPort = "%s" % str(raw_input(bcolor.GREEN + "Please provide the port the PRTG web server is listening to (IMPORTANT: Only SSL is supported)[" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpPort == "":
        return tmpPort 
    else:
        return default

def get_config_base_interval(default):
    tmpInterval = "%s" % str(raw_input(bcolor.GREEN + "Please provide the base interval for your sensors [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if not tmpInterval == "":
        return tmpInterval 
    else:
        return default

def get_config_access_key(default):
    tmpAccessKey = "%s" % str(raw_input(bcolor.GREEN + "Please provide the Probe Access Key as defined on the PRTG Core [" + default + "]: " + bcolor.END)).rstrip().lstrip()
    if (tmpAccessKey == "") and not (default == ""):
        tmpAccessKey = default
    else:
        if (tmpAccessKey == ""):
            print bcolor.YELLOW + "You have not provided the Probe Access Key as defined on the PRTG Core." + bcolor.END
            return get_config_access_key(default)
        else:
            return tmpAccessKey

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

def get_config_subprocs(default="10"):
    tmpSubprocs = "%s" % str(raw_input(bcolor.GREEN + "How much subprocesses should be spawned for scanning [" + default +"]: " + bcolor.END)).rstrip().lstrip()
    if not tmpSubprocs == "":
        return tmpSubprocs
    else:
        return default

#For future use
def get_config_announced(default):
    return "0"

#For future use
def get_config_protocol(default):
    return "1"

def get_config_debug(default):
    tmpDebug = "%s" % str(raw_input(bcolor.GREEN + "Do you want to enable debug logging (" + bcolor.YELLOW + "can create massive logfiles!" + bcolor.GREEN + ") [y/N]: " + bcolor.END)).rstrip().lstrip()
    if tmpDebug.lower() == "y":
        tmpDebug1 = "%s" % str(raw_input(bcolor.YELLOW + "Are you sure you want to enable debug logging? This will create massive logfiles [y/N]: " + bcolor.END)).rstrip().lstrip()
        if tmpDebug1.lower() == "y":
            return "True"
        else:
            return "False"
    else:
        return "False"

def get_config(config_old):
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
    if install_w1_module():
        sensors = get_w1_sensors()
        if not sensors == "":
            print bcolor.GREEN + "Adding DS18B20.py and selected sensors to /sensors/__init__.py" + bcolor.END
            write_load_list(sensors, "DS18B20")
        else:
            write_load_list("", "")
    else:
        write_load_list("", "")
    print ""
    try:
        probe_user = get_config_user()
        probe_conf['name'] = get_config_name(config_old['name'])
        probe_conf['gid'] = get_config_gid(config_old['gid'])
        probe_conf['server'] = get_config_ip(config_old['server'])
        probe_conf['port'] = get_config_port(config_old['port'])
        probe_conf['baseinterval'] = get_config_base_interval(config_old['baseinterval'])
        probe_conf['key'] = get_config_access_key(config_old['key'])
        probe_path = get_config_path()
        probe_conf['cleanmem'] = get_config_clean_memory(config_old['cleanmem'])
        probe_conf['announced'] = get_config_announced(config_old['announced'])
        probe_conf['protocol'] = get_config_protocol(config_old['protocol'])
        probe_conf['debug'] = get_config_debug(config_old['debug'])
        probe_conf['subprocs'] = get_config_subprocs(config_old['subprocs'])
        print ""
        file_create(path)
        write_config(probe_conf)
        logpath = "%s/logs" % probe_path
        if not (file_check(logpath)):
            os.makedirs(logpath)
        path_rotate = "/etc/logrotate.d/prtgprobe"
        path_init = "/etc/init.d/prtgprobe"
        print bcolor.GREEN + "Creating Logrotation Config" + bcolor.END
        write_file(path_rotate, logrotation(probe_path))
        print bcolor.GREEN + "Setting up runlevel" + bcolor.END
        write_file(path_init, init_script(probe_path, probe_user))
        print bcolor.GREEN + "Changing File Permissions" + bcolor.END
        os.chmod('%s/probe.py' % probe_path, 0755)
        os.chmod(path_init, 0755)
        return True
    except Exception, e:
        print bcolor.RED + "%s. Exiting!" % e + bcolor.END
        return False

def remove_config():
    try:
        print subprocess.call("/etc/init.d/prtgprobe stop", shell=True)
        os.remove('/etc/init.d/prtgprobe')
        os.remove('/etc/logrotate.d/prtgprobe')
        os.remove('./probe.conf')
    except Exception, e:
        print "%s. Exiting!" % e
        return False

if __name__ == '__main__':
    conf_avail = False
    if not os.getuid() == 0:
        print bcolor.RED + "You must run me as root user!" + bcolor.END
        print bcolor.RED + "Rerun me with sudo " + __file__ + bcolor.END
        sys.exit(2)
    print ""
    print bcolor.CYAN + "Welcome to the Miniprobe (Python) for PRTG installer" + bcolor.END
    path = './probe.conf'
    if file_check(path):
        print ""
        probe_config_exists = "%s" % str(raw_input(bcolor.YELLOW + "A config file was already found. Do you want to reconfigure [y/N]: " + bcolor.END)).rstrip().lstrip()
        if probe_config_exists.lower() == "y":
            config_old = read_config(path)
            get_config(config_old)
        else:
            print ""
            uninstall = "%s" % str(raw_input(bcolor.YELLOW + "Do you want to Uninstall or Restart the service [u/R]: " + bcolor.END)).rstrip().lstrip()
            if uninstall.lower() == "u":
                remove_config()
                conf_avail = False
            else:
                conf_avail = True
    else:
        conf_avail = get_config(config_old)
        if conf_avail:
            print subprocess.call("update-rc.d prtgprobe defaults", shell=True)
            print bcolor.GREEN + "Starting Mini Probe" + bcolor.END
            print subprocess.call("/etc/init.d/prtgprobe start", shell=True)
            print bcolor.GREEN + "Done. You now can start/stop the Mini Probe using '/etc/init.d/prtgprobe start' or '/etc/init.d/prtgprobe stop'" + bcolor.END
        else:
            print "Exiting!"
            sys.exit()
