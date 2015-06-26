#!/usr/bin/env python
# Copyright (c) 2014, Paessler AG <support@paessler.com>
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions
# and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
# and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse
# or promote products derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import sys
import os
import subprocess
import uuid

from setuptools import setup, find_packages
from setuptools.command.install import install as _install

# Input fix for python2/3 compatibility
if sys.version_info > (3, 0):
    raw_input = input

def read(path):
    with open(path, 'r') as f:
        return f.read()

class bcolor:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'

class Configure(_install):
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
    path = './miniprobe/probe.conf'
    #try:
    #    import __builtin__
    #    input = getattr(__builtin__, 'raw_input')
    #except (ImportError, AttributeError):
    #    pass


    def run(self):
        conf_avail = False
        if not os.getuid() == 0:
            print(bcolor.RED + "You must run me as root user!" + bcolor.END)
            print(bcolor.RED + "Rerun me with sudo " + __file__ + bcolor.END)
            sys.exit(2)
        _install.do_egg_install(self)
        print("")
        print(bcolor.CYAN + "Welcome to the Miniprobe (Python) for PRTG installer" + bcolor.END)
        if self.file_check(self.path):
            print("")
            probe_config_exists = "%s" % str(raw_input(bcolor.YELLOW + "A config file was already found. Do you want to reconfigure [y/N]: " + bcolor.END)).rstrip().lstrip()
            if probe_config_exists.lower() == "y":
                config_old = self.read_config(self.path)
                self.get_config(config_old)
            else:
                print("")
                uninstall = "%s" % str(raw_input(bcolor.YELLOW + "Do you want to Uninstall or Restart the service [u/R]: " + bcolor.END)).rstrip().lstrip()
                if uninstall.lower() == "u":
                    self.remove_config()
                    conf_avail = False
                else:
                    conf_avail = True
        else:
            conf_avail = self.get_config(self.config_old)
            if conf_avail:
                print(subprocess.call("update-rc.d prtgprobe defaults", shell=True))
                print(bcolor.GREEN + "Starting Mini Probe" + bcolor.END)
                print(subprocess.call("/etc/init.d/prtgprobe start", shell=True))
                print(bcolor.GREEN + "Done. You now can start/stop the Mini Probe using '/etc/init.d/prtgprobe start' or '/etc/init.d/prtgprobe stop'" + bcolor.END)
            else:
                print("Exiting!")
                sys.exit()
        pass

    def file_check(self, check_path):
    # Check if a give file exists
        return os.path.exists(check_path)

    def file_create(self, create_path):
        # Creates a given file and writes some startup information to it
        with open(create_path, 'w') as f:
            f.write("###Mini Probe Config File\n")
            f.close()

    def write_config(self, config):
        conf = ""
        with open(self.path, 'a') as f:
            for key in config:
                conf += "%s:%s\n" % (key, config[key])
            f.write(conf)
        f.close()
        print(bcolor.GREEN + "Config file successfully written!" + bcolor.END)

    def write_file(self, write_path, content):
        with open(write_path, 'w') as f:
            f.write(content)
        f.close()

    def logrotation(self, rotation_path):
        rotate_tpl = open("./miniprobe/scripts/rotate.tpl")
        return rotate_tpl.read() % rotation_path

    def read_config(self, path):
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
            print(bcolor.RED + "No config found! Error Message: %s Exiting!" + bcolor.END % read_error)
            sys.exit()

    def init_script(self, script_path, user):
        init_script_tpl = open("./miniprobe/scripts/probe.tpl")
        return init_script_tpl.read() % (script_path, user)

    def write_load_list(self, ds18b20_sensors, other_sensors):
        default_sensors = "Ping,HTTP,Port,SNMPCustom,CPULoad,Memory,Diskspace,SNMPTraffic,CPUTemp,Probehealth,ExternalIP,ADNS,APT,NMAP"
        if not (other_sensors == ""):
            default_sensors = default_sensors + "," + other_sensors
        f = open("./miniprobe/sensors/__init__.py","a")
        f.write("# Copyright (c) 2014, Paessler AG <support@paessler.com>\n")
        f.write("# All rights reserved.\n")
        f.write("# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the\n")
        f.write("# following conditions are met:\n")
        f.write("# 1. Redistributions of source code must retain the above copyright notice, this list of conditions\n")
        f.write("# and the following disclaimer.\n")
        f.write("# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions\n")
        f.write("# and the following disclaimer in the documentation and/or other materials provided with the distribution.\n")
        f.write("# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse\n")
        f.write("# or promote products derived from this software without specific prior written permission.\n")
        f.write("\n")
        f.write("# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\" AND ANY EXPRESS OR IMPLIED WARRANTIES,\n")
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
        print("__all__ = " + str(default_sensors.split(",")) + "\n")
        if not (ds18b20_sensors == ""):
            f.write("DS18B20_sensors = " + str(ds18b20_sensors.split(",")) + "\n")
        f.close()

    def install_w1_module(self):
        print(bcolor.YELLOW + "Checking the hardware for Raspberry Pi." + bcolor.END)
        if os.uname()[4][:3] == 'arm':
            print(bcolor.GREEN + "Found hardware matching " + os.uname()[4][:3] + bcolor.END)
            tmpUseRaspberry = "%s" % str(raw_input(bcolor.GREEN + "Do you want to enable the Raspberry Pi temperature sensor [y/N]: " + bcolor.END)).rstrip().lstrip()
            if tmpUseRaspberry.lower() == "y":
                try:
                    self.install_kernel_module()
                    return True
                except Exception as e:
                    print("%s.Please install the same" % e)
                    print("Exiting")
                    sys.exit(1)
            else:
                return False
        else:
            print(bcolor.RED + "Found hardware matching " + os.uname()[4][:3] + bcolor.END)
            return False

    def install_kernel_module(self):
        print(bcolor.GREEN + "Checking for w1-gpio line in /boot/config.txt" + bcolor.END)
        found = False
        f = open('/boot/config.txt','r')
        for line in f.readlines():
            if line.strip() == 'dtoverlay=w1-gpio':
                print(bcolor.GREEN + "Found dtoverlay line. Skipping install of w1-gpio" + bcolor.END)
                found = True
        f.close()
        if not found:
            print(bcolor.GREEN + "Line not found. Now adding the dtoverlay line to /boot/config.txt" + bcolor.END)
            f = open('/boot/config.txt','a')
            f.write('\n#w1-gpio added by PRTG MiniProbe install script\n')
            f.write('dtoverlay=w1-gpio')
            f.close()
            print(bcolor.GREEN + "Please restart the installscript after the Raspberry Pi has been rebooted!" + bcolor.END)
            print(bcolor.GREEN + "Now rebooting..." + bcolor.END)
            print(subprocess.call("reboot", shell=True))
            sys.exit(2)

    def get_w1_sensors(self):
        sensors = ""
        tmpSens = ""
        print(bcolor.GREEN + "Finding all W1 sensors" + bcolor.END)
        f = open('/sys/devices/w1_bus_master1/w1_master_slaves','r')
        for line in f.readlines():
            print(bcolor.GREEN + "Found: " + bcolor.YELLOW + line[3:].strip() + bcolor.END)
            sensors = sensors + "," + line[3:].strip()
        f.close()
        sens = "%s" % str(raw_input(bcolor.GREEN + "Please enter the id's of the temperature sensors you want to use from the list above, seperated with a , [" + sensors[1:] + "]: " + bcolor.END)).rstrip().lstrip()
        if not sens == "":
            return sens
        else:
            return sensors[1:]

    def get_config_user(self, default="root"):
        tmpUser = "%s" % str(raw_input(bcolor.GREEN + "Please provide the username the script should run under [" + default + "]: " + bcolor.END)).rstrip().lstrip()
        if not tmpUser == "":
            return tmpUser
        else:
            return default

    def get_config_name(self, default):
        tmpName = "%s" % str(raw_input(bcolor.GREEN + "Please provide the desired name of your Mini Probe [" + default + "]: " + bcolor.END)).rstrip().lstrip()
        if not tmpName == "":
            return tmpName
        else:
            return default

    def get_config_gid(self, default):
        tmpGid = "%s" % str(raw_input(bcolor.GREEN + "Please provide the Probe GID [" + default + "]: " + bcolor.END)).rstrip().lstrip()
        if not tmpGid == "":
            return tmpGid
        else:
            return default

    def get_config_ip(self, default):
        tmpIP = "%s" % str(raw_input(bcolor.GREEN + "Please provide the IP/DNS name of the PRTG Core Server [" + default + "]: " + bcolor.END)).rstrip().lstrip()
        if not (tmpIP == "") or not (default == ""):
            if (tmpIP == "") and not (default == ""):
                tmpIP = default
            response = os.system("ping -c 1 " + tmpIP + " > /dev/null")
            if not response == 0:
                print(bcolor.YELLOW + "PRTG Server can not be reached. Please make sure the server is reachable." + bcolor.END)
                go_on = "%s" % str(raw_input(bcolor.YELLOW + "Do you still want to continue using this server [y/N]: " + bcolor.END)).rstrip().lstrip()
                if not go_on.lower() == "y":
                    return self.get_config_ip()
            else:
                print(bcolor.GREEN + "PRTG Server can be reached. Continuing..." + bcolor.END)
                return tmpIP
        else:
            print(bcolor.YELLOW + "You have not provided an IP/DNS name of the PRTG Core Server." + bcolor.END)
            return self.get_config_ip()

    def get_config_port(self, default):
        tmpPort = "%s" % str(raw_input(bcolor.GREEN + "Please provide the port the PRTG web server is listening to (IMPORTANT: Only SSL is supported)[" + default + "]: " + bcolor.END)).rstrip().lstrip()
        if not tmpPort == "":
            return tmpPort
        else:
            return default

    def get_config_base_interval(self, default):
        tmpInterval = "%s" % str(raw_input(bcolor.GREEN + "Please provide the base interval for your sensors [" + default + "]: " + bcolor.END)).rstrip().lstrip()
        if not tmpInterval == "":
            return tmpInterval
        else:
            return default

    def get_config_access_key(self, default):
        tmpAccessKey = "%s" % str(raw_input(bcolor.GREEN + "Please provide the Probe Access Key as defined on the PRTG Core [" + default + "]: " + bcolor.END)).rstrip().lstrip()
        if (tmpAccessKey == "") and not (default == ""):
            tmpAccessKey = default
        else:
            if (tmpAccessKey == ""):
                print(bcolor.YELLOW + "You have not provided the Probe Access Key as defined on the PRTG Core." + bcolor.END)
                return self.get_config_access_key(default)
            else:
                return tmpAccessKey

    def get_config_path(self, default=os.path.dirname(os.path.abspath(__file__))):
        default += "/miniprobe"
        tmpPath = "%s" % str(raw_input(bcolor.GREEN + "Please provide the path where the probe files are located [" + default + "]: " + bcolor.END)).rstrip().lstrip()
        if not tmpPath == "":
            return tmpPath
        else:
            return default

    def get_config_clean_memory(self, default=""):
        tmpCleanMem = "%s" % str(raw_input(bcolor.GREEN + "Do you want the mini probe flushing buffered and cached memory [y/N]: " + bcolor.END)).rstrip().lstrip()
        if tmpCleanMem.lower() == "y":
            return "True"
        else:
            return "False"

    def get_config_subprocs(self, default="10"):
        tmpSubprocs = "%s" % str(raw_input(bcolor.GREEN + "How much subprocesses should be spawned for scanning [" + default +"]: " + bcolor.END)).rstrip().lstrip()
        if not tmpSubprocs == "":
            return tmpSubprocs
        else:
            return default

    #For future use
    def get_config_announced(self, default):
        return "0"

    #For future use
    def get_config_protocol(self, default):
        return "1"

    def get_config_debug(self, default):
        tmpDebug = "%s" % str(raw_input(bcolor.GREEN + "Do you want to enable debug logging (" + bcolor.YELLOW + "can create massive logfiles!" + bcolor.GREEN + ") [y/N]: " + bcolor.END)).rstrip().lstrip()
        if tmpDebug.lower() == "y":
            tmpDebug1 = "%s" % str(raw_input(bcolor.YELLOW + "Are you sure you want to enable debug logging? This will create massive logfiles [y/N]: " + bcolor.END)).rstrip().lstrip()
            if tmpDebug1.lower() == "y":
                return "True"
            else:
                return "False"
        else:
            return "False"

    def get_config(self, config_old):
        print("")
        print(bcolor.YELLOW + "Checking for necessary modules and Python Version" + bcolor.END)
        try:
            import hashlib
            import string
            import json
            import socket
            import importlib
            import requests
            import pyasn1
            import pysnmp
        except Exception as e:
            print("%s.Please install the same" % e)
            print("Exiting")
            sys.exit(1)
        print(bcolor.GREEN + "Successfully imported modules." + bcolor.END)
        print("")
        if self.install_w1_module():
            sensors = self.get_w1_sensors()
            if not sensors == "":
                print(bcolor.GREEN + "Adding DS18B20.py and selected sensors to /miniprobe/sensors/__init__.py" + bcolor.END)
                self.write_load_list(sensors, "DS18B20")
            else:
                self.write_load_list("", "")
        else:
            self.write_load_list("", "")
        print("")
        try:
            probe_user = self.get_config_user()
            self.probe_conf['name'] = self.get_config_name(config_old['name'])
            self.probe_conf['gid'] = self.get_config_gid(config_old['gid'])
            self.probe_conf['server'] = self.get_config_ip(config_old['server'])
            self.probe_conf['port'] = self.get_config_port(config_old['port'])
            self.probe_conf['baseinterval'] = self.get_config_base_interval(config_old['baseinterval'])
            self.probe_conf['key'] = self.get_config_access_key(config_old['key'])
            probe_path = self.get_config_path()
            self.probe_conf['cleanmem'] = self.get_config_clean_memory(config_old['cleanmem'])
            self.probe_conf['announced'] = self.get_config_announced(config_old['announced'])
            self.probe_conf['protocol'] = self.get_config_protocol(config_old['protocol'])
            self.probe_conf['debug'] = self.get_config_debug(config_old['debug'])
            self.probe_conf['subprocs'] = self.get_config_subprocs(config_old['subprocs'])
            print("")
            print(self.path)
            self.file_create(self.path)
            self.write_config(self.probe_conf)
            logpath = "%s/logs" % probe_path
            if not (self.file_check(logpath)):
                os.makedirs(logpath)
            path_rotate = "/etc/logrotate.d/prtgprobe"
            path_init = "/etc/init.d/prtgprobe"
            print(bcolor.GREEN + "Creating Logrotation Config" + bcolor.END)
            self.write_file(path_rotate, self.logrotation(probe_path))
            print(bcolor.GREEN + "Setting up runlevel" + bcolor.END)
            self.write_file(path_init, self.init_script(probe_path, probe_user))
            print(bcolor.GREEN + "Changing File Permissions" + bcolor.END)
            os.chmod('%s/probe.py' % probe_path, 0o0755)
            os.chmod(path_init, 0o0755)
            return True
        except Exception as e:
            print(bcolor.RED + "%s. Exiting!" % e + bcolor.END)
            return False

    def remove_config(self):
        try:
            print(subprocess.call("/etc/init.d/prtgprobe stop", shell=True))
            os.remove('/etc/init.d/prtgprobe')
            os.remove('/etc/logrotate.d/prtgprobe')
            os.remove('./miniprobe/probe.conf')
        except Exception as e:
            print("%s. Exiting!" % e)
            return False

with open('requirements.txt') as f:
    requires = f.read().splitlines()

packages = [
    "miniprobe"
]

setup(
    name='Python Mini Probe',
    version=read('VERSION.txt'),
    author='Paessler AG',
    author_email='support@paessler.com',
    license='BSD 3.0',
    description='Python MiniProbe for PRTG',
    long_description=read('README.md'),
    packages=find_packages(),
    install_requires=requires,
    url='https://github.com/PaesslerAG/PythonMiniProbe',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
    ],
    cmdclass={'configure': Configure}
)


