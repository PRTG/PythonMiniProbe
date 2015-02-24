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

class DS18B20(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpds18b20"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        if os.path.isdir("/sys/bus/w1/devices"):
            default = "yes"
        else:
            default = "no"
        sensordefinition = {
            "kind": DS18B20.get_kind(),
            "name": "DS18B20 Temperature",
            "description": "Returns the temperature measured by an attached DS18B20 temperature sensor on pin 4",
            "default": default,
            "help": "Returns the temperature measured by an attached DS18B20 temperature sensor on pin 4",
            "tag": "mpds18b20sensor",
            "groups": [
               {
               "name":"Group",
               "caption":"Temperature settings",
               "fields":[
                  {
                       "type":"radio",
                       "name":"celfar",
                       "caption":"Choose between Celsius or Fahrenheit display",
                       "help":"Choose wether you want to return the value in Celsius or Fahrenheit",
                       "options":{
                                               "C":"Celsius",
                                               "F":"Fahrenheit"
                                               },
                       "default":"C"
                  },
                        ]
               }
          ]
        }
        return sensordefinition

    @staticmethod
    def get_data(data, out_queue):
        temperature = DS18B20()
        logging.info("Running sensor: %s" % temperature.get_kind())
        try:
            temp = temperature.read_temp(data)
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (temperature.get_kind(),
                                                                                         data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "DS18B20 sensor failed. See log for details"
            }
            out_queue.put(data)
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
        out_queue.put(data)

    @staticmethod
    def read_temp(config):
        data = []
        sens = []
        chandata = []
        for sensor in __init__.DS18B20_sensors:
            sens.append(sensor)
            temp = open("/sys/bus/w1/devices/28-" + sensor + "/w1_slave", "r")
            lines = temp.readlines()
            temp.close()
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                logging.debug("DS18B20 Debug message: Temperature from file: %s" % temp_string)
                temp_c = float(temp_string) / 1000.0
                temp_f = 1.8 * temp_c + 32.0
                if config['celfar'] == "C":
                    data.append(temp_c)
                    logging.debug("DS18B20 Debug message: Temperature after calculations:: %s %s" % (temp_c, config['celfar']))
                else:
                    data.append(temp_f)
                    logging.debug("DS18B20 Debug message: Temperature after calculations:: %s %s" % (temp_f, config['celfar']))
            temp.close()
        for i in range(len(data)):
            chandata.append({"name": "Sensor: " + sens[i],
                            "mode": "float",
                            "unit": "Custom",
                            "customunit": config['celfar'],
                            "LimitMode": 1,
                            "LimitMaxError": 40,
                            "LimitMaxWarning": 35,
                            "value": float(data[i])})
        return chandata
