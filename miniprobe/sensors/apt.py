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


class APT(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpapt"
    
    @staticmethod       
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": APT.get_kind(),
            "name": "Linux Updates",
            "description": "Monitors the available updates for the linux system",
            "help": "Monitors the available updates for the linux system using apt-get/yum",
            "tag": "mpaptsensor",
            "fields": [],
            "groups": []
        }
        return sensordefinition

    def check(self):
        upgrade = 0
        install = 0
        remove = 0
        ret = os.popen("LC_ALL=C apt-get -s dist-upgrade | grep 'newly inst'")
        updatedata = ret.readlines()
        ret.close()
        for line in updatedata:
            upgrade = int(line.split(" ")[0].lstrip())
            install = int(line.split(" ")[2].lstrip())
            remove = int(line.split(" ")[5].lstrip())
        total = upgrade + install + remove
        channel_list = [
            {
                "name": "Total updates available",
                "mode": "integer",
                "unit": "Count",
                "limitmaxwarning": 1,
                "limitmode": 1,
                "value": total
            },
            {
                "name": "Upgrades",
                "mode": "integer",
                "unit": "Count",
                "value": upgrade
            },
            {
                "name": "New to install",
                "mode": "integer",
                "unit": "Count",
                "value": install
            },
            {
                "name": "Old to remove",
                "mode": "integer",
                "unit": "Count",
                "limitmaxwarning": 1,
                "LimitMode": 1,
                "value": remove
            },
        ]
        return channel_list

    @staticmethod
    def get_data(data, out_queue):
        apt = APT()
        try:
            aptdata = apt.check()
            data_r = {
                "sensorid": int(data['sensorid']),
                "message": "OK",
                "channel": aptdata
            }
            logging.debug("Running sensor: %s" % apt.get_kind())
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (apt.get_kind(),
                                                                                         data['sensorid'], e))
            data_r = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "APT failed. %s" % e
            }
            out_queue.put(data_r)
            return 1
        del apt
        gc.collect()
        out_queue.put(data_r)
        return 0
