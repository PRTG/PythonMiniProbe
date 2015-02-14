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
- requests (https://pypi.python.org/pypi/requests/2.3.0)

Installation
------------
- set up your PRTG server to use HTTPS (other connection methods not allowed at the moment)
- allow MiniProbes to connect (Setup -> Probes -> Allow MiniProbes to connect)
- make sure you can reach the PRTG web interface from the machine the mini probe should run on (e.g. wget https://YOUR_PRTG_SERVER)
  - This is tested during the setup
- copy the miniprobe folder to your linux machine
- run the probe installer (e.g. "python probe_installer.py")

The miniprobe should now be started. You should also be able to start/stop the same using the command /etc/init.d/probe.sh start resp. /etc/init.d/probe.sh stop  

Debugging
---------

To enable debugging, open the file probe.conf and replace the line  

debug:  

with  

debug:True  

This will enable detailed logging to folder "logs" which is as sub folder of the miniprobe folder. For further debugging, please stop the miniprobe process as outlined above. Navigate to the folder the file "probe.py" can be found then run following command "python probe.py". On major errors you will get the details and traceback directly on the console.

Changelog
=========
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
 
