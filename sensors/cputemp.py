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

import gc
import os
import logging
import time
import __init__

class CPUTemp(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpcputemp"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": CPUTemp.get_kind(),
            "name": "CPU Temperature",
            "description": "Returns the CPU temperature",
            "default": "yes",
            "help": "Returns the CPU temperature",
            "tag": "mpcputempsensor",
            "groups": [
		      ]
        }
        return sensordefinition

    @staticmethod
    def get_data(data):
        temperature = CPUTemp()
        logging.info("Running sensor: %s" % temperature.get_kind())
        try:
            temp = temperature.read_temp()
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (temperature.get_kind(),
                                                                                         data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "CPUTemp sensor failed. See log for details"
            }
            return data
        tempdata = []
        for element in temp:
            tempdata.append(element)
        data = {
            "sensorid": int(data['sensorid']),
            "message": "OK",
            "channel": tempdata
        }
        del temperature
        gc.collect()
        return data

    @staticmethod
    def read_temp():
	data = []
        chandata = []
        temp = open("/sys/class/thermal/thermal_zone0/temp", "r")
        lines = temp.readlines()
        temp.close()
        temp_string = lines[0]
        logging.debug("CPUTemp Debug message: Temperature from file: %s" % temp_string)
        temp_c = float(temp_string) / 1000.0
        logging.debug("CPUTemp Debug message: Temperature after calculations:: %s" % temp_c)
        data.append(temp_c)
        for i in range(len(data)):
            chandata.append({"name": "CPU Temperature",
	                     "mode": "float",
	                     "unit": "Custom",
		             "customunit": "C",
                             "LimitMode": 1,
                             "LimitMaxError": 40,
                             "LimitMaxWarning": 35,
	                     "value": float(data[i])})
        return chandata
