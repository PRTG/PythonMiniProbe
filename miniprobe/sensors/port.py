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

import time
import socket
import gc
import logging


class Port(object):
    def __init__(self):
        gc.enable()

    def __del__(self):
        gc.collect()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpport"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": Port.get_kind(),
            "name": "Port",
            "description": "Monitors the availability of a port or port range on a target system",
            "help": "test",
            "tag": "mpportsensor",
            "groups": [
                {
                    "name": " portspecific",
                    "caption": "Port specific",
                    "fields": [
                        {
                            "type": "integer",
                            "name": "timeout",
                            "caption": "Timeout (in s)",
                            "required": "1",
                            "default": 60,
                            "minimum": 1,
                            "maximum": 900,
                            "help": "If the reply takes longer than this value the request is aborted "
                                    "and an error message is triggered. Max. value is 900 sec. (=15 min.)"
                        },
                        {
                            "type": "integer",
                            "name": "targetport",
                            "caption": "Port",
                            "required": "1",
                            "default": 110,
                            "minimum": 1,
                            "maximum": 65534,
                            "help": ""
                        }
                    ]
                }
            ]
        }
        return sensordefinition

    def port(self, target, timeout, port):
        remote_server = socket.gethostbyname(target)
        response_time = 0.0
        try:
            start_time = time.time()
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.settimeout(float(timeout))
            conn.connect((remote_server, int(port)))
            conn.close()
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
        except socket.gaierror as e:
            print e
        except socket.timeout as e:
            print e
        except Exception as e:
            print "test %s" % e

        channel_list = [
            {
                "name": "Available",
                "mode": "float",
                "kind": "TimeResponse",
                "value": float(response_time)
            }
        ]
        return channel_list

    @staticmethod
    def get_data(data, out_queue):
        port = Port()
        try:
            port_data = port.port(data['host'], data['timeout'], data['targetport'])
            logging.debug("Running sensor: %s" % port.get_kind())
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (port.get_kind(),
                                                                                         data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "Port check failed. See log for details"
            }
            out_queue.put(data)
            return 1
        data = {
            "sensorid": int(data['sensorid']),
            "message": "OK Port %s available" % data['targetport'],
            "channel": port_data
        }
        del port
        gc.collect()
        out_queue.put(data)
        return 0
