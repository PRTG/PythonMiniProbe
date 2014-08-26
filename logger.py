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

import os
import socket
import datetime


class Logger(object):
    # Provides logging functionality  
    def __init__(self):
        pass
    
    path = './logs/probe.log'

    def file_check(self, path):
        # Check if a given file exists
        return os.path.exists(path)    
    
    def file_create(self, path):
        # Creates a given file and writes some startup information to it       
        f = open(path, 'w')
        f.write(str(self.startup_logging()))
        f.close()

    def log(self, kind=None, log_type=None, config=None, request=None, e=None, sensor=None):
        # provides internal logging
        messages = {
            "request_error": "Could not perform %s request! Error Message: %s %s %s. Trying again in %s seconds.",
            "request_success": "%s request successfully sent to PRTG Core Server at %s:%s.",
            "sensor_error": "Ooops Something went wrong with '%s' sensor %s. Error: %s.",
            "nothing_todo": "Nothing to do. Waiting for %s seconds.",
            "subprocess": "Could not start sensor %s subprocess. Error Message: %s"
        }
        loggingtext = ""
        timestamp = datetime.datetime.utcnow()
        if kind and not request:
            loggingtext = messages['request_success'] % (request, config['server'], config['port'])
        elif kind and log_type == "Nothing":
            loggingtext = messages['nothing_todo'] % (int(config['baseinterval']) / 2)
        elif kind and log_type == "Subprocess":
            loggingtext = messages['subprocess'] % (config['sensorid'], e)
        else:
            if log_type == "HTTP":
                loggingtext = messages['request_error'] % (request, e.getcode(), e.reason, e.read(),
                                                           int(config['baseinterval'] / 2))
            elif log_type == "URL":
                loggingtext = messages['request_error'] % (request, e, "", "", int(config['baseinterval'] / 2))
            elif log_type == "SENSOR":
                loggingtext = messages['sensor_error'] % (sensor, config['sensorid'], e)
        if not(self.file_check(self.path)):
            self.file_create(self.path)
        with open(self.path, 'a') as f:
            f.write(str("%s %s\n" % (timestamp, loggingtext)))
        f.close()

    def log_custom(self, loggingtext):
        # writes any given string to a logfile
        timestamp = datetime.datetime.utcnow()
        if not(self.file_check(self.path)):
            self.file_create(self.path)
        with open(self.path, 'a') as f:
            f.write(str("%s %s\n" % (timestamp, loggingtext)))
        f.close()
            
    def startup_logging(self):
        # startup logging
        timestamp = datetime.datetime.utcnow()
        config = self.read_config('./probe.conf')
        startupstring = "%s PRTG Small Probe '%s' starting on '%s'\n" % (timestamp, config['name'],
                                                                         socket.gethostname())
        startupstring += "%s Connecting to PRTG Core Server at %s:%s\n" % (timestamp, config['server'], config['port'])
        return startupstring
            
    def read_config(self, path):
        # Read config file 'mini_probe.conf'
        config = {}
        conf_file = open(path)
        for line in conf_file:
            if not (line == '\n'):
                if not (line.startswith('#')):
                    config[line.split(':')[0]] = line.split(':')[1].rstrip()
        conf_file.close()
        return config
