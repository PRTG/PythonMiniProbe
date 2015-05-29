"""
Not stable therefore removed in the Beta. Might come back later.
"""
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

import time
import socket
import logging
import gc


class Portrange(object):
    def __init__(self):
        pass

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpportrange"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": Portrange.get_kind(),
            "name": "Port Range",
            "description": "Checks the availability of a port range on a target system",
            "help": "Checks the availability of a port range on a target system",
            "tag": "mpportrangesensor",
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
                            "name": "startport",
                            "caption": "Port",
                            "required": "1",
                            "default": 110,
                            "minimum": 1,
                            "maximum": 65534,
                            "help": "Specify the port ranges starting port"
                        },
                        {
                            "type": "integer",
                            "name": "endport",
                            "caption": "Port",
                            "required": "1",
                            "default": 110,
                            "minimum": 1,
                            "maximum": 65534,
                            "help": "Specify the port ranges end port"
                        }
                    ]
                }
            ]
        }
        return sensordefinition

    def portrange(self, target, timeout, start, end):
        remote_server = socket.gethostbyname(target)
        numberofports = int(end) - int(start)
        result = 1234
        a = 0
        start_time = time.time()
        for port in range(int(start), int(end)):
            try:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.settimeout(float(timeout))
                result = conn.connect_ex((remote_server, int(port)))
                conn.close()
            except socket.gaierror as e:
                print e
            except socket.timeout as e:
                print e
            except Exception as e:
                print "test %s" % e
            if result == 0:
                a += 1
            else:
                raise Exception('port %s not open' % port)

        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        if a == numberofports:
            channel_list = [
                {
                    "name": "Available",
                    "mode": "float",
                    "kind": "TimeResponse",
                    "value": float(response_time)
                }
            ]
            return channel_list
        else:
            raise Exception

    @staticmethod
    def get_data(data):
        port = Portrange()
        try:
            port_data = port.portrange(data['host'], data['timeout'], data['startport'], data['endport'])
            logging.debug("Running sensor: %s" % port.get_kind())
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (port.get_kind(),
                                                                                         data['sensorid'], e))
            sensor_data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "Port check failed or ports closed. See log for details"
            }
            return sensor_data
        sensor_data = {
            "sensorid": int(data['sensorid']),
            "message": "OK Ports open",
            "channel": port_data
        }
        del port
        gc.collect()
        return sensor_data
