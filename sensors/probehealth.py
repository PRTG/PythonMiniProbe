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
            "help": "test",
            "tag": "mpprobehealthsensor",
            "fields": [],
            "groups": []
        }
        return sensordefinition
    
    @staticmethod
    def get_data(data, out_queue):
        probehealth = Probehealth()
        try:
            mem = probehealth.read_memory('/proc/meminfo')
            cpu = probehealth.read_cpu('/proc/loadavg')
            logging.info("Running sensor: %s" % probehealth.get_kind())
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (probehealth.get_kind(),
                                                                                         data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "Probe Health sensor failed. See log for details"
            }
            return data
        probedata = []
        for element in mem:
            probedata.append(element)
        for element in cpu:
            probedata.append(element)
        data = {
            "sensorid": int(data['sensorid']),
            "message": "OK",
            "channel": probedata
        }
        out_queue.put(data)
        return data

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
        tmp = []
        for line in os.popen("df -h"):
            if line.startswith("/"):
                tmp.append(line.rstrip())     
        print disks
