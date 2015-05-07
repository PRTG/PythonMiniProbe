PythonMiniProbe
===============

Current Status: BETA  
MiniProbe POC for PRTG Network Monitor written in Python which accesses the MiniProbe Interface on the PRTG Core Server.  

Prerequisites
-----------------
Debian based system (tested on Ubuntu, Debian, Raspbian)  
Python 2.7+  
Needed modules are delivered with the probe package:  
- pyasn1 (https://pypi.python.org/pypi/pyasn1/0.1.7)  
- pysnmp (https://pypi.python.org/pypi/pysnmp/4.2.5)  
- requests (https://pypi.python.org/pypi/requests/2.5.3)
- dnspython (https://pypi.python.org/pypi/dnspython/1.12.0)

Installation
------------
- set up your PRTG server to use HTTPS (other connection methods not allowed at the moment)
- allow MiniProbes to connect (Setup -> Probes -> Allow MiniProbes to connect)
- make sure you can reach the PRTG web interface from the machine the mini probe should run on (e.g. wget https://YOUR_PRTG_SERVER)
  - This is tested during the setup
- copy the miniprobe folder to your linux machine
- run the probe installer (e.g. "python probe_installer.py")

The miniprobe should now be started. You should also be able to start/stop the same using the command /etc/init.d/probe.sh start resp. /etc/init.d/probe.sh stop  

Instalation of DS18B20
----------------------
Requirements:
- DS18B20
- 4.7K Ohm resistor

Setup:
- Solder the resister between pin 2 and 3 of the DS18B20 (when the flat part of the DS18B20 is facing ou, then pin 2 and 3 is from the middle pin to the right)
- place Pin 1 on pin 6 on the Raspberry
- place Pin 2 on pin 7 on the Raspberry
- place Pin 3 on pin 1 on the Raspberry
- Run the installscript of the probe and answer Yes to the question if you want to use the Raspberry Pi temperature sensor.
- The installscript will now make a change to the raspberry boot process to include a special library and it will reboot the Raspberry. After the reboot, run the installer again and answer the same question again. It will now (if all is correct) detect your DS18B20 (using it's own unique serial number) and just confirm that this is correct by presing <Return> on your keyboard.

Debugging
---------

To enable debugging, open the file probe.conf and replace the line  

debug:  

with  

debug:True  

This will enable detailed logging to folder "logs" which is as sub folder of the miniprobe folder. For further debugging, please stop the miniprobe process as outlined above. Navigate to the folder the file "probe.py" can be found then run following command "python probe.py". On major errors you will get the details and traceback directly on the console.

Changelog
=========
07-05-2015
----------
- Finished the DNS Sensor for all dns types currently available in a Windows Probe
- Added an APT sensor to check for available updates on the system

04-05-2015
----------
- Added dns sensor with support for A MX and SOA Records
- Set the log message "Running Sensor: ..." to a debug message
- Added the dnspython module for the dns sensor

24-02-2015
----------
- Added support for multiprocessing, now sensors are spawned as subprocesses (merged branch experimental with master)
- fixed some indentation stuff (tabs instead of whitespaces) 
- fixed function get_config_key in probe_installer.py as key was set to None type all the time, fixed some sensors to put return data in the queue rather than simply returning it. 
- other minor fixes resp. code cleanup
- preparation for a workflow (no direct commits to master any more)

14-02-2015
----------
- Added full support for the DS18B20 and a lot of cleanup and fixes
- Also added the boot/config.txt fix for the DS18B20 that is needed on the RPi
- Removed the no longer needed W1ThermSensor module from the repo
    as the Raspbian Image for raspberry already includes everything needed

02-02-2015
----------
- Installer cleanup and preparation for reading current config
- Fix typo :(
- Installer cleanup continued, added uninstall option to the installer, debug option added during installation
- added W1ThermSensor module to the repo

26-01-2015
----------
- Merge pull request #2 from eagle00789/master 
-- Fixed Update-rd.d command
-- Removed duplicate defined baseinterval check
-- Fixed a bug in the installer that created the config file before any values where asked
-- Added ping check for PRTG Server availability with possibility to still continue
-- Added several checks and moved some code around to a function.

19-01-2015
----------
- added optional debug information

08-01-2015
----------
- fix for issue 1

05-11-2014
----------
- updated module requests

10-10-2014
----------
- dropped own logging
-- now using python built in logging function (you might delete the file logger.py if existant)
-- created file miniprobe.py which offers base functionality, probe.py now only does the work
-- various changes and code cleanup
-- added script templates for the probe_installer.py in folder /scripts
-- changed version number to reflect YY.QQ.Release

28-08-2014
----------
- added module retry

26-08-2014
----------
- Updated module requests
-- from now it is not necessary to use weakened security in the PRTG web server. There will be a one time warning if you are using a self signed certificate which can be ignored.
- added VERSION.txt file
-- the version number is built up from Year.Quarter.Buildnumber
- moved Python version check to the beginning of the script
- big code cleanup
- applied PEP 8 rules to the code, some other refactoring). To be continued... (Probably tomorrow)

17-07-2014
----------
- Changed readme file, adjusted setup.py
 
07-07-2014
----------
- Fixed typos
- Added check for logs folder

27-06-2014
----------
- Updated documentation
- Merge Remote-tracking branch

26-06-2014
----------
- Updated Readme
- Changed line separators
- Initial Commit
- Changed readme file
- deleted readme

25-06-2014
----------
- Initial commit
 
