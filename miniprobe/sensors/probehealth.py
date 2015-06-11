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

import os
import logging


class Probehealth(object):
    def __init__(self):
        pass
    
    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpprobehealth"
    
    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": Probehealth.get_kind(),
            "name": "Probe Health",
            "description": "Internal sensor used to monitor the health of a PRTG probe",
            "default": "yes",
            "help": "Internal sensor used to monitor the health of a PRTG probe",
            "tag": "mpprobehealthsensor",
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
                        {
                            "type": "integer",
                            "name": "maxtemp",
                            "caption": "Error temperature",
                            "required": "1",
                            "minimum": 20,
                            "maximum": 75,
                            "help": "Set the maximum temperature above which the temperature sensor will "
                                    "provide a error (not below 20 or above 75)",
                            "default": 45
                        },
                    ]
                }
            ]
        }
        return sensordefinition
    
    @staticmethod
    def get_data(data, out_queue):
        probehealth = Probehealth()
        try:
            mem = probehealth.read_memory('/proc/meminfo')
            cpu = probehealth.read_cpu('/proc/loadavg')
            temperature = probehealth.read_temp()
            disk = probehealth.read_disk()
            health = probehealth.read_probe_health(data)
            logging.debug("Running sensor: %s" % probehealth.get_kind())
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (probehealth.get_kind(),
                                                                                         data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "Probe Health sensor failed. See log for details"
            }
            out_queue.put(data)
            return 1
        probedata = []
        for element in health:
            probedata.append(element)
        for element in mem:
            probedata.append(element)
        for element in temperature:
            probedata.append(element)
        for element in cpu:
            probedata.append(element)
        for element in disk:
            probedata.append(element)
        data = {
            "sensorid": int(data['sensorid']),
            "message": "OK",
            "channel": probedata
        }
        out_queue.put(data)
        return 0

    def read_memory(self, path):
        mem = open(path, "r")
        data = {}
        for line in mem:
            tmp = line.split(":")[1].lstrip()
            data[line.split(":")[0].rstrip()] = tmp.split(" ")[0].rstrip()
        channel_list = [{"name": "Memory Total",
                         "mode": "integer",
                         "kind": "BytesMemory",
                         "value": int(data['MemTotal']) * 1024},
                        {"name": "Memory Free",
                         "mode": "integer",
                         "kind": "BytesMemory",
                         "value": int(data['MemFree']) * 1024},
                        {"name": "Swap Total",
                         "mode": "integer",
                         "kind": "BytesMemory",
                         "value": int(data['SwapTotal']) * 1024},
                        {"name": "Swap Free",
                         "mode": "integer",
                         "kind": "BytesMemory",
                         "value": int(data['SwapFree']) * 1024}]
        mem.close()
        return channel_list
        
    def read_cpu(self, path):
        cpu = open(path, "r")
        data = []
        for line in cpu:
            for element in line.split(" "):
                data.append(element)
        channel_list = [{"name": "Load Average 1min",
                         "mode": "float",
                         "kind": "Custom",
                         "customunit": "",
                         "value": float(data[0])},
                        {"name": "Load Average 5min",
                         "mode": "float",
                         "kind": "Custom",
                         "customunit": "",
                         "value": float(data[1])},
                        {"name": "Load Average 10min",
                         "mode": "float",
                         "kind": "Custom",
                         "customunit": "",
                         "value": float(data[2])}]
        cpu.close()
        return channel_list
       
    def read_disk(self):
        disks = []
        channel_list = []
        for line in os.popen("df -k"):
            if line.startswith("/"):
                disks.append(line.rstrip().split())
        for line in disks:
            channel1 = {"name": "Total Bytes " + str(line[0]),
                        "mode": "integer",
                        "kind": "BytesDisk",
                        "value": int(line[1]) * 1024}
            channel2 = {"name": "Used Bytes" + str(line[0]),
                        "mode": "integer",
                        "kind": "BytesDisk",
                        "value": int(line[2]) * 1024}
            channel3 = {"name": "Free Bytes " + str(line[0]),
                        "mode": "integer",
                        "kind": "BytesDisk",
                        "value": int(line[3]) * 1024}
            total = float(line[2]) + float(line[3])
            used = float(line[2]) / total
            free = float(line[3]) / total

            channel4 = {"name": "Free Space " + str(line[0]),
                        "mode": "float",
                        "kind": "Percent",
                        "value": free * 100}
            channel5 = {"name": "Used Space" + str(line[0]),
                        "mode": "float",
                        "kind": "Percent",
                        "value": used * 100}
            channel_list.append(channel1)
            channel_list.append(channel2)
            channel_list.append(channel3)
            channel_list.append(channel4)
            channel_list.append(channel5)
        return channel_list

    def read_temp(self):
        data = []
        chandata = []
        try:
            if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
                temp = open("/sys/class/thermal/thermal_zone0/temp", "r")
                lines = temp.readlines()
                temp.close()
                temp_string = lines[0]
            else:
                return chandata
        except OSError:
            logging.debug("Could not read temp file, no data will be returned")
            return chandata
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

    def read_probe_health(self, config):
        health = 100
        logging.debug("Current Health: %s percent" % health)
        data = []
        chandata = []
        try:
            if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
                temp = open("/sys/class/thermal/thermal_zone0/temp", "r")
                lines = temp.readlines()
                temp.close()
                temp_float = float(lines[0]) / 1000.0
                if temp_float > config['maxtemp']:
                    health -= 25
                    logging.debug("Current Health: %s percent" % health)
            else:
                return chandata
        except OSError:
            logging.debug("Health not changed, no temperature available")
            pass
        disks = []
        for line in os.popen("df -k"):
            if line.startswith("/"):
                disks.append(line.rstrip().split())
                tmphealth = 25 / len(disks)
        for line in disks:
            free = (float(line[3]) / (float(line[2]) + float(line[3]))) * 100
            if free < 10:
                health -= tmphealth
                logging.debug("Current Health: %s percent" % health)
        cpu = open('/proc/loadavg', "r")
        for line in cpu:
            for element in line.split(" "):
                data.append(element)
        if float(data[1]) > 0.70:
            health -= 25
            logging.debug("Current Health: %s percent" % health)
        chandata.append({"name": "Overall Probe Health",
                         "mode": "integer",
                         "unit": "percent",
                         "value": health})
        return chandata
