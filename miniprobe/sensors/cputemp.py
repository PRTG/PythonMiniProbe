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

import gc
import logging
import os.path
temp = True
if not os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
    temp = False


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
    def get_sensordef(testing=False):
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
                {
                    "name": "Group",
                    "caption": "Temperature settings",
                    "fields": [
                        {
                            "type": "radio",
                            "name": "celfar",
                            "caption": "Choose between Celsius or Fahrenheit display",
                            "help": "Choose wether you want to return the value in Celsius or Fahrenheit",
                            "options": {
                                "C": "Celsius",
                                "F": "Fahrenheit"
                            },
                            "default": "C"
                        },
                    ]
                }
            ]
        }
        if not temp and not testing:
            sensordefinition = ""
        return sensordefinition

    @staticmethod
    def get_data(data, out_queue):
        temperature = CPUTemp()
        logging.debug("Running sensor: %s" % temperature.get_kind())
        try:
            tmp = temperature.read_temp(data)
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (temperature.get_kind(),
                                                                                         data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "CPUTemp sensor failed. See log for details"
            }
            out_queue.put(data)
            return 1
        tempdata = []
        for element in tmp:
            tempdata.append(element)
        data = {
            "sensorid": int(data['sensorid']),
            "message": "OK",
            "channel": tempdata
        }
        del temperature
        gc.collect()
        out_queue.put(data)
        return 1

    @staticmethod
    def read_temp(config):
        data = []
        chandata = []
        tmp = open("/sys/class/thermal/thermal_zone0/temp", "r")
        lines = tmp.readlines()
        tmp.close()
        temp_string = lines[0]
        logging.debug("CPUTemp Debug message: Temperature from file: %s" % temp_string)
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        logging.debug("CPUTemp Debug message: Temperature after calculations:: %s" % temp_c)
        if config['celfar'] == "C":
            data.append(temp_c)
        else:
            data.append(temp_f)
        for i in range(len(data)):
            chandata.append({"name": "CPU Temperature",
                             "mode": "float",
                             "unit": "Custom",
                             "customunit": config['celfar'],
                             "LimitMode": 1,
                             "LimitMaxError": 40,
                             "LimitMaxWarning": 35,
                             "value": float(data[i])})
        return chandata
