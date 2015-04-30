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

import gc
import logging
import requests
import dns

class DNS(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpdns"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": DNS.get_kind(),
            "name": "DNS",
            "description": "Monitors a DNS server (Domain Name Service), resolves a domain name, and compares it to an IP address",
            "help": "The DNS sensor monitors a Domain Name Service (DNS) server. It resolves a domain name and compares it to a given IP address.",
            "tag": "mpdnssensor",
            "groups": [
                {
                    "name": "DNS Specific",
                    "caption": "DNS Specific",
                    "fields": [
                        {
                            "type": "integer",
                            "name": "timeout",
                            "caption": "Timeout (in s)",
                            "required": "1",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 900,
                            "help": "Timeout in seconds. A maximum value of 900 is allowed."
                        },
                        {
                            "type": "integer",
                            "name": "port",
                            "caption": "Port",
                            "required": "1",
                            "default": 53,
                            "minimum": 1,
                            "maximum": 65535,
                            "help": "Enter the port on which the DNS service of the parent device is running."
                        },
                        {
                            "type": "edit",
                            "name": "domain",
                            "caption": "Domain",
                            "required": "1",
                            "help": "Enter a DNS name or IP address to resolve."
                        },
                        {
                            "type": "radio",
                            "name": "type",
                            "caption": "Query Type",
                            "required": "1",
                            "help": "Specify the type of query that the sensor will send to the DNS server.",
                            "options": {
                                           "A":"Host address IPv4 (A)",
                                           "AAAA":"Host address IPv6 (AAAA)",
                                           "NS":"Authoritative name server (NS)",
                                           "SOA":"Start of a zone of authority marker (SOA)",
                                           "PTR":"Domain name pointer (PTR)",
                                           "MX":"Mail exchange (MX)",
                                           "CNAME":"Canonical name for an alias (CNAME)"
                                       },
                            "default": "A",
                        },
                              ]
                }
        }
        return sensordefinition

    @staticmethod
    def get_data(data, out_queue):
        dns = DNS()
        result = ""
        logging.info("Running sensor: %s" % ip.get_kind())
        try:
            result = dns.get_dns(server)
            logging.debug("IP-Address: %s" % address)
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (ip.get_kind(),
                                                                                         data['sensorid'], e))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "DNS sensor failed. See log for details"
            }
            out_queue.put(data)
        addressdata = []
        for element in address:
            addressdata.append(element)
        data = {
            "sensorid": int(data['sensorid']),
            "message": "DNS: " + dns.remote_ip(server),
            "channel": addressdata
        }
        del address
        gc.collect()
        out_queue.put(data)

    @staticmethod
    def get_dns(url):
        channel_list = [{"name": "IP-Address",
                        "ShowChart": 0,
                        "ShowTable": 0,
                        "mode": "integer",
                        "kind": "Custom",
                        "customunit": "",
                        "value": 1}]
        return channel_list

    @staticmethod
    def remote_ip(url):
        ip = requests.get(url, timeout=30)
        address = str(ip.text[0:-1])
        ip.close
        return address
