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
import gc
import logging


class Ping(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpping"
    
    @staticmethod       
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": Ping.get_kind(),
            "name": "Ping",
            "description": "Monitors the availability of a target using ICMP",
            "help": "Monitors the availability of a target using ICMP",
            "tag": "mppingsensor",
            "groups": [
                {
                    "name": " Ping Settings",
                    "caption": "Ping Settings",
                    "fields": [
                        {
                            "type": "integer",
                            "name": "timeout",
                            "caption": "Timeout (in s)",
                            "required": "1",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 300,
                            "help": "Timeout in seconds. A maximum value of 300 is allowed."  
                        },
                        {
                            "type": "integer",
                            "name": "packsize",
                            "caption": "Packetsize (Bytes)",
                            "required": "1",
                            "default": 32,
                            "minimum": 1,
                            "maximum": 10000,
                            "help": "The default packet size for Ping requests is 32 bytes, "
                                    "but you can choose any other packet size between 1 and 10,000 bytes."
                        },
                        {
                            "type": "integer",
                            "name": "pingcount",
                            "caption": "Ping Count",
                            "required": "1",
                            "default": 1,
                            "minimum": 1,
                            "maximum": 20,
                            "help": "Enter the count of Ping requests PRTG will send to the device during an interval"
                        }
                    ]
                }
            ]
        }
        return sensordefinition

    def ping(self, target, count, timeout, packetsize):
        ping = ""
        ret = os.popen("/bin/ping -c %s -s %s -W %s %s" % (str(count), str(packetsize), str(timeout), str(target)))
        pingdata = ret.readlines()
        ret.close()
        for line in pingdata:
            if line.startswith("r"):
                ping = line.split("=")[1].lstrip()
            if line.find("packet") > 0:
                pack_loss = line.split(",")[2].lstrip()
                pack_loss = pack_loss.split(' ')[0].lstrip()
                pack_loss = pack_loss[:-1]
        if ping == '':
            return "Not reachable!"
        values = ping.split("/") + [pack_loss]
        channel_list = [
            {
                "name": "Ping Time Min",
                "mode": "float",
                "kind": "TimeResponse",
                "value": float(values[0])
            },
            {
                "name": "Ping Time Avg",
                "mode": "float",
                "kind": "TimeResponse",
                "value": float(values[1])
            },
            {
                "name": "Ping Time Max",
                "mode": "float",
                "kind": "TimeResponse",
                "value": float(values[2])
            },
            {
                "name": "Ping Time MDEV",
                "mode": "float",
                "kind": "TimeResponse",
                "value": float(values[3].split(' ')[0])
            },
            {
                "name": "Packet Loss",
                "mode": "integer",
                "kind": "Percent",
                "value": int(values[4])
            }
        ]
        return channel_list

    @staticmethod
    def get_data(data, out_queue):
        ping = Ping()
        try:
            pingdata = ping.ping(data['host'], data['pingcount'], data['timeout'], data['packsize'])
            if pingdata == "Not reachable!":
                data_r = {
                    "sensorid": int(data['sensorid']),
                    "error": "Exception",
                    "code": 1,
                    "message": data['host'] + " is " + pingdata
                }
            else:
                data_r = {
                    "sensorid": int(data['sensorid']),
                    "message": "OK",
                    "channel": pingdata
                }
            logging.debug("Running sensor: %s" % ping.get_kind())
            logging.debug("Host: %s Pingcount: %s timeout: %s packetsize: %s" % (data['host'], data['pingcount'],
                                                                                 data['timeout'], data['packsize']))
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (ping.get_kind(),
                                                                                         data['sensorid'], e))
            data_r = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "Ping failed."
            }
            out_queue.put(data_r)
            return 1
        del ping
        gc.collect()
        out_queue.put(data_r)
        return 0
