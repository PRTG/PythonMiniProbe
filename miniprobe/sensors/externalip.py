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
import requests
import socket
import fcntl
import struct
server = "http://icanhazip.com"


class ExternalIP(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpexternalip"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": ExternalIP.get_kind(),
            "name": "External IP",
            "description": "Returns the external ip address of the probe",
            "default": "yes",
            "help": "Returns the external ip address of the probe using the website icanhasip.com",
            "tag": "mpexternalipsensor",
            "fields": [],
            "groups": []
        }
        return sensordefinition

    @staticmethod
    def get_data(data, out_queue):
        ip = ExternalIP()
        # address = ""
        logging.debug("Running sensor: %s" % ip.get_kind())
        try:
            address = ip.get_ip(server)
            logging.debug("IP-Address: %s" % address)
            localip = ip.local_ip('eth0')
            remoteip = ip.remote_ip(server)
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (ip.get_kind(),
                                                                                         data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "External IP sensor failed. See log for details"
            }
            out_queue.put(data)
            return 1
        addressdata = []
        for element in address:
            addressdata.append(element)
        data = {
            "sensorid": int(data['sensorid']),
            "message": "External IP: " + remoteip + "  Internal IP: " + localip,
            "channel": addressdata
        }
        del address
        gc.collect()
        out_queue.put(data)
        return 0

    @staticmethod
    def get_ip(url):
        channel_list = [
            {
                "name": "IP-Address",
                "ShowChart": 0,
                "ShowTable": 0,
                "mode": "integer",
                "kind": "Custom",
                "customunit": "",
                "value": 1
            }]
        return channel_list

    @staticmethod
    def remote_ip(url):
        ip = requests.get(url, timeout=30)
        address = str(ip.text[0:-1])
        ip.close
        return address

    def local_ip(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
