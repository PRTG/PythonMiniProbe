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
try:
    import dns.resolver
    import dns.reversename
    dnscheck = True
except Exception as e:
    logging.error("PyDNS could not be imported. DNS Sensor won't work.Error: %s" % e)
    dnscheck = False
    pass

class Blacklist(object):
    blacklists = []
    blacklists.append("zen.spamhaus.org")
    blacklists.append("spam.abuse.ch")
    blacklists.append("cbl.abuseat.org")
    blacklists.append("virbl.dnsbl.bit.nl")
    blacklists.append("dnsbl.inps.de")
    blacklists.append("ix.dnsbl.manitu.net")
    blacklists.append("dnsbl.sorbs.net")
    blacklists.append("bl.spamcannibal.org")
    blacklists.append("bl.spamcop.net")
    blacklists.append("xbl.spamhaus.org")
    blacklists.append("pbl.spamhaus.org")
    blacklists.append("dnsbl-1.uceprotect.net")
    blacklists.append("dnsbl-2.uceprotect.net")
    blacklists.append("dnsbl-3.uceprotect.net")
    blacklists.append("db.wpbl.info")
    blacklists.append("bsb.emtpy.us")
    blacklists.append("dnsbl.anticaptcha.net")
    blacklists.append("aspews.ext.sorbs.net")
    blacklists.append("ips.backscatterer.org")
    blacklists.append("b.barracudacentral.org")
    blacklists.append("bl.blocklist.de")
    blacklists.append("dnsbl.burnt-tech.com")
    blacklists.append("cblless.anti-spam.org.cn")
    blacklists.append("bogons.cymru.com")
    blacklists.append("fullbogons.cymru.com")
    blacklists.append("tor.dan.me.uk")
    blacklists.append("torexit.dan.me.uk")
    blacklists.append("rbl.dns-servicios.com")
    blacklists.append("bl.drmx.org")
    blacklists.append("dnsbl.dronebl.org")
    blacklists.append("rbl.efnetrbl.org")

    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpblacklist"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": Blacklist.get_kind(),
            "name": "Blacklist",
            "description": "Monitors a server for blacklisting",
            "help": "The Blacklist sensor monitors a server for blacklisting",
            "tag": "mpblacklist",
            "groups": [
                {
                    "name": "Blacklist Specific",
                    "caption": "Blacklist Specific",
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
                            "type": "edit",
                            "name": "domain",
                            "caption": "Domain",
                            "required": "1",
                            "help": "Enter a DNS name or IP address to check for blacklisting."
                        }
                    ]
                }
            ]
        }
        if not dnscheck:
            sensordefinition = ""
        return sensordefinition

    @staticmethod
    def get_data(data, out_queue):
        blacklist = Blacklist()
        logging.debug("Running sensor: %s" % blacklist.get_kind())
        try:
            result = blacklist.get_record(data['timeout'], data['domain'])
            logging.debug("Blacklist: %s" % result)
        except Exception as ex:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (blacklist.get_kind(),
                                                                                         data['sensorid'], ex))
            data_r = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "Blacklist sensor failed. See log for details"
            }
            out_queue.put(data_r)
            return 1
        dns_channel = blacklist.get_blacklist(result)
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
                "message": result[0],
                "channel": addressdata
            }
        del result
        gc.collect()
        out_queue.put(data)
        return 0

    @staticmethod
    def get_blacklist(result):
        channel_list = [{"name": "Listed Count",
                         "ShowChart": 0,
                         "ShowTable": 0,
                         "mode": "integer",
                         "kind": "Custom",
                         "customunit": "",
                         "limitmaxerror": 0,
                         "limitmode": 1,
                         "value": result[1]},
                         {"name": "Not Listed Count",
                         "ShowChart": 0,
                         "ShowTable": 0,
                         "mode": "integer",
                         "kind": "Custom",
                         "customunit": "",
                         "value": result[2]},
                         {"name": "No Answer Count",
                         "ShowChart": 0,
                         "ShowTable": 0,
                         "mode": "integer",
                         "kind": "Custom",
                         "customunit": "",
                         "limitmaxwarning": 0,
                         "limitmode": 1,
                         "value": result[3]}]
        return channel_list

    @staticmethod
    def get_record(timeout, domain):
        blacklist = Blacklist()
        noanswer = 0
        notlisted = 0
        listed = 0
        msg = ""
        for bl in blacklist.blacklists:
            try:
                resolver = dns.resolver.Resolver()
                query = '.'.join(reversed(str(domain).split("."))) + "." + bl
                answers = resolver.query(query, "A")
                answer_txt = resolver.query(query, "TXT")[0]
                answer_txt = str(answer_txt).strip('"')
                msg = msg + str(answer_txt) + ", "
                listed += 1
            except dns.resolver.NXDOMAIN:
                notlisted += 1
            except dns.resolver.NoAnswer:
                noanswer += 1
        return [msg[:-2], listed, notlisted, noanswer]

