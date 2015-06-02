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
import requests
import logging


class HTTP(object):
    
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mphttp"
    
    @staticmethod       
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": HTTP.get_kind(),
            "name": "HTTP",
            "description": "Monitors a web server using HTTP",
            "help": "Monitors a web server using HTTP",
            "tag": "mphttpsensor",
            "groups": [
                {
                    "name": "HTTP Specific",
                    "caption": "HTTP Specific",
                    "fields": [
                        {
                            "type": "integer",
                            "name": "timeout",
                            "caption": "Timeout (in s)",
                            "required": "1",
                            "default": 60,
                            "minimum": 1,
                            "maximum": 900,
                            "help": "Timeout in seconds. A maximum value of 900 is allowed."  
                        },
                        {
                            "type": "edit",
                            "name": "url",
                            "caption": "URL",
                            "required": "1",
                            "default": "http://",
                            "help": "Enter a valid URL to monitor. The server part (e.g. www.paessler.com) "
                                    "may be different from the 'DNS Name' property in the settings of the "
                                    "associated server."
                        },
                        {
                            "type": "radio",
                            "name": "http_method",
                            "caption": "Request Method",
                            "required": "1",
                            "help": "Choose the type of the HTTP request",
                            "options": {
                                "1": "GET",
                                "2": "POST",
                                "3": "HEAD"
                            },
                            "default": 1
                        },
                        {
                            "type": "edit",
                            "name": "post_data",
                            "caption": "POST data",
                            "help": "Data in this field will only be used when request type is POST"
                        }
                        
                    ]
                },
                {
                    "name": "Authentication",
                    "caption": "Authentication",
                    "fields": [
                        {
                            "type": "radio",
                            "name": "auth_method",
                            "caption": "Authentication Method",
                            "required": "1",
                            "help": "Choose the type of authentication used",
                            "options": {
                                "1": "No authentication",
                                "2": "Basic"
                            },
                            "default": 1
                        },
                        {
                            "type": "edit",
                            "name": "username",
                            "caption": "Username",
                            "help": "Provide username here if target requires authentication"
                        },
                        {
                            "type": "password",
                            "name": "password",
                            "caption": "Password",
                            "help": "Provide password here if target requires authentication"
                        }
                    ]
                }
            ]
        }

        return sensordefinition

    def request(self, url, request_method=None, auth_method=None, timeout=None, post_data=None,
                user=None, password=None):
        timeout = float(timeout)
        try:
            if request_method == "1":
                # GET
                if (user or password) and auth_method == "2":
                    req = requests.get(url, auth=(user, password), timeout=timeout, verify=False)
                else:
                    req = requests.get(url, timeout=timeout, verify=False)
            elif request_method == "2":
                # POST
                if (user or password) and auth_method == "2":
                    req = requests.post(url, data=post_data, auth=(user, password), timeout=timeout, verify=False)
                else:
                    req = requests.post(url, data=post_data, timeout=timeout, verify=False)
            elif request_method == "3":
                # HEAD
                if (user or password) and auth_method == "2":
                    req = requests.head(url, auth=(user, password), timeout=timeout, verify=False)
                else:
                    req = requests.head(url, timeout=timeout, verify=False)
            time = req.elapsed
        except Exception as e:
            logging.error(e)
            raise
        try:
            code = req.status_code
            response_time = time.microseconds / 1000
        except Exception as e:
            logging.error(e)
            raise
        data = [int(code), float(response_time)]
        return data

    @staticmethod
    def get_data(data, out_queue):
        http = HTTP()
        try:
            http_data = http.request(data['url'], request_method=data["http_method"], auth_method=data["auth_method"],
                                     user=data["username"], password=data["password"],
                                     post_data=data["post_data"], timeout=data["timeout"])
            logging.debug("Running sensor: %s" % http.get_kind())
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s"
                          % (http.get_kind(), data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "HTTP Request failed. See log for details"
            }
            out_queue.put(data)
            return 1
        
        data = {
            "sensorid": int(data['sensorid']),
            "message": "OK Status Code: %s" % http_data[0],
            "channel": [
                {
                    "name": "Response Time",
                    "mode": "float",
                    "kind": "TimeResponse",
                    "value": http_data[1]
                }]
        }
        del http
        gc.collect()
        out_queue.put(data)
        return 0
