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
import timeit
try:
    import dns.resolver
    import dns.reversename
    dnscheck = True
except Exception as e:
    logging.error("PyDNS could not be imported. DNS Sensor won't work.Error: %s" % e)
    dnscheck = False
    pass


class ADNS(object):
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
            "kind": ADNS.get_kind(),
            "name": "DNS",
            "description": "Monitors a DNS server (Domain Name Service), "
                           "resolves a domain name, and compares it to an IP address",
            "help": "The DNS sensor monitors a Domain Name Service (DNS) server. "
                    "It resolves a domain name and compares it to a given IP address.",
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
                                "A": "Host address IPv4 (A)",
                                "AAAA": "Host address IPv6 (AAAA)",
                                "CNAME": "Canonical name for an alias (CNAME)",
                                "MX": "Mail exchange (MX)",
                                "NS": "Authoritative name server (NS)",
                                "PTR": "Domain name pointer (PTR)",
                                "SOA": "Start of a zone of authority marker (SOA)",
                                "SRV": "Service Record"
                            },
                            "default": "A",
                        },
                    ]
                }
            ]
        }
        if not dnscheck:
            sensordefinition = ""
        return sensordefinition

    @staticmethod
    def get_data(data, out_queue):
        adns = ADNS()
        logging.debug("Running sensor: %s" % adns.get_kind())
        try:
            start_time = timeit.default_timer()
            result = adns.get_record(data['timeout'], data['port'], data['domain'], data['type'], data['host'])
            timed = timeit.default_timer() - start_time
            logging.debug("DNS: %s" % result)
        except Exception as ex:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (adns.get_kind(),
                                                                                         data['sensorid'], ex))
            data_r = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "DNS sensor failed. See log for details"
            }
            out_queue.put(data_r)
            return 1
        dns_channel = adns.get_dns(int(timed * 1000))
        addressdata = []
        for element in dns_channel:
            addressdata.append(element)
        if result[0:9] == "DNS Error":
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": result
            }
        else:
            data = {
                "sensorid": int(data['sensorid']),
                "message": data['type'] + ": " + result,
                "channel": addressdata
            }
        del result
        gc.collect()
        out_queue.put(data)
        return 0

    @staticmethod
    def get_dns(time):
        channel_list = [{"name": "Response Time",
                         "ShowChart": 0,
                         "ShowTable": 0,
                         "mode": "integer",
                         "kind": "Custom",
                         "customunit": "ms",
                         "value": time}]
        return channel_list

    @staticmethod
    def get_record(timeout, port, domain, type, host):
        result = domain + ": "
        try:
            resolver = dns.resolver.Resolver(configure=False)
            resolver.nameservers = [host]
            resolver.port = port
            if type == 'PTR':
                addr = dns.reversename.from_address(domain)
                answers = dns.resolver.query(addr, type)
            else:
                answers = dns.resolver.query(domain, type)
            if (type == 'A') or (type == 'AAAA'):
                for rdata in answers:
                    result = result + str(rdata.address) + ", "
            elif type == 'MX':
                for rdata in answers:
                    result = result + rdata.preference + ": " + rdata.exchange + ", "
            elif type == 'SOA':
                for rdata in answers:
                    result = result + "NS: " + str(rdata.mname) + ", TECH: " + str(rdata.rname) + ", S/N: " + str(rdata.serial) + ", Refresh: " + str(rdata.refresh / 60) + " min, Expire: " \
                             + str(rdata.expire / 60) + " min  "
            elif (type == 'CNAME') or (type == 'NS') or (type == 'PTR'):
                for rdata in answers:
                    result = result + str(rdata.target) + ", "
        except dns.resolver.NoAnswer:
            result = "DNS Error while getting %s record. " \
                     "This could be the result of a misconfiguration in the sensor settings" % type
        return result[:-2]
