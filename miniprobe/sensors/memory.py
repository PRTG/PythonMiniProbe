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


class Memory(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpmemory"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": Memory.get_kind(),
            "name": "Memory",
            "description": "Monitors memory on the system the mini probe is running on",
            "default": "yes",
            "help": "Monitors memory on the system the mini probe is running on",
            "tag": "mpmemorysensor",
            "fields": [],
            "groups": []
        }
        return sensordefinition

    @staticmethod
    def get_data(data, out_queue):
        memory = Memory()
        try:
            mem = memory.read_memory('/proc/meminfo')
            logging.debug("Running sensor: %s" % memory.get_kind())
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (memory.get_kind(),
                                                                                         data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "Memory sensor failed. See log for details"
            }
            out_queue.put(data)
            return 1
        memorydata = []
        for element in mem:
            memorydata.append(element)
        data = {
            "sensorid": int(data['sensorid']),
            "message": "OK",
            "channel": memorydata
        }
        del memory
        gc.collect()
        out_queue.put(data)
        return 0

    def read_memory(self, path):
        mem = open(path, "r")
        data = {}
        for line in mem:
            tmp = line.split(":")[1].lstrip()
            data[line.split(":")[0].rstrip()] = tmp.split(" ")[0].rstrip()
        channel_list = [
            {
                "name": "Memory Total",
                "mode": "integer",
                "kind": "BytesMemory",
                "value": int(data['MemTotal']) * 1024
            },
            {
                "name": "Memory Free",
                "mode": "integer",
                "kind": "BytesMemory",
                "value": int(data['MemFree']) * 1024
            },
            {
                "name": "Swap Total",
                "mode": "integer",
                "kind": "BytesMemory",
                "value": int(data['SwapTotal']) * 1024
            },
            {
                "name": "Swap Free",
                "mode": "integer",
                "kind": "BytesMemory",
                "value": int(data['SwapFree']) * 1024
            }]
        mem.close()
        return channel_list
