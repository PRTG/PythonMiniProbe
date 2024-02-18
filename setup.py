default_sensors = "Ping,HTTP,Port,SNMPCustom,CPULoad,Memory,Diskspace,SNMPTraffic,CPUTemp,Probehealth,ExternalIP,ADNS,APT,NMAP,MDADM"
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
    with open(path, 'r') as file:
        return file.read()


class Bcolor:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'


class Configure(_install):
    probe_conf = {}
    conf_avail = False
    config_init = {
        'name': "Python MiniProbe",
        'gid': str(uuid.uuid4()),
        'server': "",
        'port': "443",
        'baseinterval': "60",
        'key': "",
        'cleanmem': "",
        'announced': "0",
        'protocol': "1",
        'debug': "",
        'subprocs': "10"
    }
    path = './miniprobe/probe.conf'

    def run(self):
        conf_avail = False
        if not os.getuid() == 0:
            print(Bcolor.RED + "You must run me as root user!" + Bcolor.END)
            print(Bcolor.RED + "Rerun me with sudo " + __file__ + Bcolor.END)
            sys.exit(2)
        _install.do_egg_install(self)
        print("")
        print(Bcolor.CYAN + "Welcome to the Miniprobe (Python) for PRTG installer" + Bcolor.END)
        if self.file_check(self.path):
            print("")
            probe_config_exists = "%s" % str(raw_input(Bcolor.YELLOW + "A config file was already found. "
                                                                       "Do you want to reconfigure [y/N]: " 
                                                       + Bcolor.END)).rstrip().lstrip()
            if probe_config_exists.lower() == "y":
                config_old = self.read_config(self.path)
                self.get_config(config_old)
            else:
                print("")
                uninstall = "%s" % str(raw_input(Bcolor.YELLOW + "Do you want to Uninstall or Restart the "
                                                                 "service [u/R]: " + Bcolor.END)).rstrip().lstrip()
                if uninstall.lower() == "u":
                    self.remove_config()
                    conf_avail = False
                else:
                    conf_avail = True
        else:
            conf_avail = self.get_config(self.config_init)
            if conf_avail:
                print(subprocess.call("update-rc.d prtgprobe defaults", shell=True))
                print(Bcolor.GREEN + "Starting Mini Probe" + Bcolor.END)
                print(subprocess.call("/etc/init.d/prtgprobe start", shell=True))
                print(Bcolor.GREEN + "Done. You now can start/stop the Mini Probe using '/etc/init.d/prtgprobe start' "
                                     "or '/etc/init.d/prtgprobe stop'" + Bcolor.END)
            else:
                print("Exiting!")
                sys.exit()
        pass

    def file_check(self, check_path):
        # Check if a give file exists
        return os.path.exists(check_path)

    def file_create(self, create_path):
        # Creates a given file and writes some startup information to it
        with open(create_path, 'w') as file_create:
            file_create.write("###Mini Probe Config File\n")
            file_create.close()

    def write_config(self, config):
        conf = ""
        with open(self.path, 'a') as config_file:
            for key in config:
                conf += "%s:%s\n" % (key, config[key])
            config_file.write(conf)
        config_file.close()
        print(Bcolor.GREEN + "Config file successfully written!" + Bcolor.END)

    def write_file(self, write_path, content):
        with open(write_path, 'w') as file_write:
            file_write.write(content)
        file_write.close()

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
            print(Bcolor.RED + "No config found! Error Message: %s Exiting!" + Bcolor.END % read_error)
            sys.exit()

    def init_script(self, script_path, user):
        init_script_tpl = open("./miniprobe/scripts/probe.tpl")
        return init_script_tpl.read() % (script_path, user)

    def write_load_list(self, ds18b20_sensors, other_sensors):
        default_sensors = "Ping,HTTP,Port,SNMPCustom,CPULoad,Memory,Diskspace,SNMPTraffic,CPUTemp,Probehealth,ExternalIP,ADNS,APT,NMAP,MDADM"
        if not (other_sensors == ""):
            default_sensors = default_sensors + "," + other_sensors
        file_sensor_init = open("./miniprobe/sensors/__init__.py", "a")
        file_sensor_init.write("# Copyright (c) 2014, Paessler AG <support@paessler.com>\n")
        file_sensor_init.write("# All rights reserved.\n")
        file_sensor_init.write("# Redistribution and use in source and binary forms, with or without modification,"
                               " are permitted provided that the\n")
        file_sensor_init.write("# following conditions are met:\n")
        file_sensor_init.write("# 1. Redistributions of source code must retain the above copyright notice, "
                               "this list of conditions\n")
        file_sensor_init.write("# and the following disclaimer.\n")
        file_sensor_init.write("# 2. Redistributions in binary form must reproduce the above copyright notice, "
                               "this list of conditions\n")
        file_sensor_init.write("# and the following disclaimer in the documentation and/or other materials provided "
                               "with the distribution.\n")
        file_sensor_init.write("# 3. Neither the name of the copyright holder nor the names of its contributors may be"
                               " used to endorse\n")
        file_sensor_init.write("# or promote products derived from this software without specific prior written "
                               "permission.\n")
        file_sensor_init.write("\n")
        file_sensor_init.write("# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \"AS IS\" "
                               "AND ANY EXPRESS OR IMPLIED WARRANTIES,\n")
        file_sensor_init.write("# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND "
                               "FITNESS FOR\n")
        file_sensor_init.write("# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR "
                               "CONTRIBUTORS BE LIABLE FOR ANY DIRECT,\n")
        file_sensor_init.write("# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES "
                               "(INCLUDING, BUT NOT LIMITED TO,\n")
        file_sensor_init.write("# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; "
                               "OR BUSINESS INTERRUPTION)\n")
        file_sensor_init.write("# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, "
                               "STRICT LIABILITY,\n")
        file_sensor_init.write("# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF "
                               "THE USE OF THIS SOFTWARE,\n")
        file_sensor_init.write("# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.\n")
        file_sensor_init.write("\n")
        file_sensor_init.write("# Announce modules available in this package\n")
        file_sensor_init.write("# Just extend this list for your modules and they will be automatically imported "
                               "during runtime and\n")
        file_sensor_init.write("# are announced to the PRTG Core\n")
        file_sensor_init.write("__all__ = " + str(default_sensors.split(",")) + "\n")
        print("__all__ = " + str(default_sensors.split(",")) + "\n")
        if not (ds18b20_sensors == ""):
            file_sensor_init.write("DS18B20_sensors = " + str(ds18b20_sensors.split(",")) + "\n")
        file_sensor_init.close()

    def install_w1_module(self):
        print(Bcolor.YELLOW + "Checking the hardware for Raspberry Pi." + Bcolor.END)
        if os.uname()[4][:3] == 'arm':
            print(Bcolor.GREEN + "Found hardware matching " + os.uname()[4][:3] + Bcolor.END)
            tmp_use_raspberry = "%s" % str(raw_input(Bcolor.GREEN + "Do you want to enable the Raspberry Pi "
                                                                    "temperature sensor [y/N]: "
                                                     + Bcolor.END)).rstrip().lstrip()
            if tmp_use_raspberry.lower() == "y":
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
            print(Bcolor.RED + "Found hardware matching " + os.uname()[4][:3] + Bcolor.END)
            return False

    def install_kernel_module(self):
        print(Bcolor.GREEN + "Checking for w1-gpio line in /boot/config.txt" + Bcolor.END)
        found = False
        file_boot_config = open('/boot/config.txt', 'r')
        for line in file_boot_config.readlines():
            if line.strip() == 'dtoverlay=w1-gpio':
                print(Bcolor.GREEN + "Found dtoverlay line. Skipping install of w1-gpio" + Bcolor.END)
                found = True
        file_boot_config.close()
        if not found:
            print(Bcolor.GREEN + "Line not found. Now adding the dtoverlay line to /boot/config.txt" + Bcolor.END)
            file_boot_config = open('/boot/config.txt', 'a')
            file_boot_config.write('\n#w1-gpio added by PRTG MiniProbe install script\n')
            file_boot_config.write('dtoverlay=w1-gpio')
            file_boot_config.close()
            print(Bcolor.GREEN + "Please restart the installscript after the Raspberry Pi has been rebooted!" 
                  + Bcolor.END)
            print(Bcolor.GREEN + "Now rebooting..." + Bcolor.END)
            print(subprocess.call("reboot", shell=True))
            sys.exit(2)

    def get_w1_sensors(self):
        sensors = ""
        print(Bcolor.GREEN + "Finding all W1 sensors" + Bcolor.END)
        w1_file = open('/sys/devices/w1_bus_master1/w1_master_slaves', 'r')
        for line in w1_file.readlines():
            print(Bcolor.GREEN + "Found: " + Bcolor.YELLOW + line[3:].strip() + Bcolor.END)
            sensors = sensors + "," + line[3:].strip()
        w1_file.close()
        sens = "%s" % str(raw_input(Bcolor.GREEN + "Please enter the id's of the temperature sensors you want to use "
                                                   "from the list above, separated with a , [" + sensors[1:] + "]: "
                                    + Bcolor.END)).rstrip().lstrip()
        if not sens == "":
            return sens
        else:
            return sensors[1:]

    def get_config_user(self, default="root"):
        tmp_user = "%s" % str(raw_input(Bcolor.GREEN + "Please provide the username the script should run under ["
                                        + default + "]: " + Bcolor.END)).rstrip().lstrip()
        if not tmp_user == "":
            return tmp_user
        else:
            return default

    def get_config_name(self, default):
        tmp_name = "%s" % str(raw_input(Bcolor.GREEN + "Please provide the desired name of your Mini Probe [" 
                                        + default + "]: " + Bcolor.END)).rstrip().lstrip()
        if not tmp_name == "":
            return tmp_name
        else:
            return default

    def get_config_gid(self, default):
        tmp_gid = "%s" % str(raw_input(Bcolor.GREEN + "Please provide the Probe GID [" + default + "]: " 
                                       + Bcolor.END)).rstrip().lstrip()
        if not tmp_gid == "":
            return tmp_gid
        else:
            return default

    def get_config_ip(self, default=None):
        tmp_ip = "%s" % str(raw_input(Bcolor.GREEN + "Please provide the IP/DNS name of the PRTG Core Server [" 
                                      + default + "]: " + Bcolor.END)).rstrip().lstrip()
        if not (tmp_ip == "") or not (default == ""):
            if (tmp_ip == "") and not (default == ""):
                tmp_ip = default
            response = os.system("ping -c 1 " + tmp_ip + " > /dev/null")
            if not response == 0:
                print(Bcolor.YELLOW + "PRTG Server can not be reached. Please make sure the server is reachable." 
                      + Bcolor.END)
                go_on = "%s" % str(raw_input(Bcolor.YELLOW + "Do you still want to continue using this server [y/N]: " 
                                             + Bcolor.END)).rstrip().lstrip()
                if not go_on.lower() == "y":
                    return self.get_config_ip()
            else:
                print(Bcolor.GREEN + "PRTG Server can be reached. Continuing..." + Bcolor.END)
                return tmp_ip
        else:
            print(Bcolor.YELLOW + "You have not provided an IP/DNS name of the PRTG Core Server." + Bcolor.END)
            return self.get_config_ip()

    def get_config_port(self, default):
        tmp_port = "%s" % str(raw_input(Bcolor.GREEN + "Please provide the port the PRTG web server is listening to "
                                                       "(IMPORTANT: Only SSL is supported)[" + default + "]: "
                                        + Bcolor.END)).rstrip().lstrip()
        if not tmp_port == "":
            return tmp_port
        else:
            return default

    def get_config_base_interval(self, default):
        tmp_interval = "%s" % str(raw_input(Bcolor.GREEN + "Please provide the base interval for your sensors ["
                                            + default + "]: " + Bcolor.END)).rstrip().lstrip()
        if not tmp_interval == "":
            return tmp_interval
        else:
            return default

    def get_config_access_key(self, default):
        tmp_accesskey = "%s" % str(raw_input(Bcolor.GREEN + "Please provide the Probe Access Key as defined on the "
                                                            "PRTG Core [" + default + "]: "
                                             + Bcolor.END)).rstrip().lstrip()
        if (tmp_accesskey == "") and not (default == ""):
            tmp_accesskey = default
        else:
            if tmp_accesskey == "":
                print(Bcolor.YELLOW + "You have not provided the Probe Access Key as defined on the PRTG Core." 
                      + Bcolor.END)
                return self.get_config_access_key(default)
            else:
                return tmp_accesskey

    def get_config_path(self, default=os.path.dirname(os.path.abspath(__file__))):
        default += "/miniprobe"
        tmp_path = "%s" % str(raw_input(Bcolor.GREEN + "Please provide the path where the probe files are located [" 
                                        + default + "]: " + Bcolor.END)).rstrip().lstrip()
        if not tmp_path == "":
            return tmp_path
        else:
            return default

    def get_config_clean_memory(self, default=None):
        tmp_cleanmem = "%s" % str(raw_input(Bcolor.GREEN + "Do you want the mini probe flushing buffered and cached "
                                                           "memory [y/N]: " + Bcolor.END)).rstrip().lstrip()
        if tmp_cleanmem.lower() == "y":
            return "True"
        else:
            return "False"

    def get_config_subprocs(self, default="10"):
        tmp_subprocs = "%s" % str(raw_input(Bcolor.GREEN + "How much subprocesses should be spawned for scanning [" 
                                            + default + "]: " + Bcolor.END)).rstrip().lstrip()
        if not tmp_subprocs == "":
            return tmp_subprocs
        else:
            return default

    # For future use
    def get_config_announced(self, default):
        return default

    # For future use
    def get_config_protocol(self, default):
        return default

    def get_config_debug(self, default):
        tmp_debug = "%s" % str(raw_input(Bcolor.GREEN + "Do you want to enable debug logging (" + Bcolor.YELLOW + 
                                         "can create massive logfiles!" + Bcolor.GREEN + ") [y/N]: " 
                                         + Bcolor.END)).rstrip().lstrip()
        if tmp_debug.lower() == "y":
            tmp_debug1 = "%s" % str(raw_input(Bcolor.YELLOW + "Are you sure you want to enable debug logging? "
                                                              "This will create massive logfiles [y/N]: " 
                                              + Bcolor.END)).rstrip().lstrip()
            if tmp_debug1.lower() == "y":
                return "True"
            else:
                return "False"
        else:
            return "False"

    def get_config(self, config_old):
        print("")
        print(Bcolor.YELLOW + "Checking for necessary modules and Python Version" + Bcolor.END)
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
        print(Bcolor.GREEN + "Successfully imported modules." + Bcolor.END)
        print("")
        if self.install_w1_module():
            sensors = self.get_w1_sensors()
            if not sensors == "":
                print(Bcolor.GREEN + "Adding DS18B20.py and selected sensors to /miniprobe/sensors/__init__.py"
                      + Bcolor.END)
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
            print(Bcolor.GREEN + "Creating Logrotation Config" + Bcolor.END)
            self.write_file(path_rotate, self.logrotation(probe_path))
            print(Bcolor.GREEN + "Setting up runlevel" + Bcolor.END)
            self.write_file(path_init, self.init_script(probe_path, probe_user))
            print(Bcolor.GREEN + "Changing File Permissions" + Bcolor.END)
            os.chmod('%s/probe.py' % probe_path, 0o0755)
            os.chmod(path_init, 0o0755)
            return True
        except Exception as e:
            print(Bcolor.RED + "%s. Exiting!" % e + Bcolor.END)
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

if sys.version_info > (3, 0):
    py_requires = 'requirements3.txt'
else:
    py_requires = 'requirements.txt'
with open(py_requires) as f:
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


