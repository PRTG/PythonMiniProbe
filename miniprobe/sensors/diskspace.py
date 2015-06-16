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


class Diskspace(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpdiskspace"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": Diskspace.get_kind(),
            "name": "Disk space",
            "description": "Monitors disk space on the system the mini probe is running on",
            "default": "yes",
            "help": "Monitors disk space on the system the mini probe is running on",
            "tag": "spdiskspacesensor",
            "fields": [],
            "groups": []
        }
        return sensordefinition

    @staticmethod
    def get_data(data, out_queue):
        diskspace = Diskspace()
        try:
            disk = diskspace.read_disk()
            logging.debug("Running sensor: %s" % diskspace.get_kind())
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (diskspace.get_kind(),
                                                                                         data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "Disk Space Sensor failed. See log for details"
            }
            out_queue.put(data)
            return 1
        channels = disk
        data = {
            "sensorid": int(data['sensorid']),
            "message": "OK",
            "channel": channels
        }
        del diskspace
        gc.collect()
        out_queue.put(data)
        return 0

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
