PythonMiniProbe
===============

Current Status: EARLY BETA  
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
- copy the miniprobe folder to your linux machine
- make the file "probe_installer.py" executable (e.g. "chmod 755 probe_installer.py")
- within the folder you placed the probe.py file create another folder called "logs" (mkdir logs)
- run the probe installer (e.g. "python probe_installer.py")
- when asked for a username by the installer script, please choose "root" for now

The miniprobe should now be started. You should also be able to start/stop the same using the command /etc/init.d/probe.sh start resp. /etc/init.d/probe.sh stop  

Debugging
---------

To enable debugging, open the file probe.conf and replace the line  

debug:  

with  

debug:True  

This will enable detailed logging to folder "logs" which is as sub folder of the miniprobe folder. For further debugging, please stop the miniprobe process as outlined above. Navigate to the folder the file "probe.py" can be found then run following command "python probe.py". On major errors you will get the details and traceback directly on the console.
