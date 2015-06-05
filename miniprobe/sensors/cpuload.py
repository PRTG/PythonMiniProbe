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


class CPULoad(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpcpuload"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": CPULoad.get_kind(),
            "name": "CPU Load",
            "description": "Monitors CPU load avg on the system the mini probe is running on",
            "default": "yes",
            "help": "Monitors CPU load avg on the system the mini probe is running on",
            "tag": "mpcpuloadsensor",
            "fields": [],
            "groups": []
        }
        return sensordefinition

    @staticmethod
    def get_data(data, out_queue):
        cpuload = CPULoad()
        logging.debug("Running sensor: %s" % cpuload.get_kind())
        try:
            cpu = cpuload.read_cpu('/proc/loadavg')
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (cpuload.get_kind(),
                                                                                         data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "CPU load sensor failed. See log for details"
            }
            out_queue.put(data)
            return 1
        cpudata = []
        for element in cpu:
            cpudata.append(element)
        data = {
            "sensorid": int(data['sensorid']),
            "message": "OK",
            "channel": cpudata
        }
        del cpuload
        gc.collect()
        out_queue.put(data)
        return 0

    @staticmethod
    def read_cpu(path):
        cpu = open(path, "r")
        data = []
        for line in cpu:
            for element in line.split(" "):
                data.append(element)
        channel_list = [
            {
                "name": "Load Average 1min",
                "mode": "float",
                "kind": "Custom",
                "customunit": "",
                "value": float(data[0])
            },
            {
                "name": "Load Average 5min",
                "mode": "float",
                "kind": "Custom",
                "customunit": "",
                "value": float(data[1])
            },
            {
                "name": "Load Average 10min",
                "mode": "float",
                "kind": "Custom",
                "customunit": "",
                "value": float(data[2])
            }]
        cpu.close()
        return channel_list
