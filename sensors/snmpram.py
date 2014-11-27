#!/usr/bin/env python
#Copyright (c) 2014, Paessler AG <support@paessler.com>
#All rights reserved.
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import gc


#import logging module
sys.path.append('../')
#from logger import Logger

#log = Logger()
try:
    sys.path.append('./')
    from pysnmp.entity.rfc3413.oneliner import cmdgen
except Exception as e:
    print e
    #sys.exit()
    pass


class SNMPRam(object):

    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpsnmpram"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind" : SNMPRam.get_kind(),
            "name" : "SNMP RAM",
            "description" : "Monitors a numerical value returned by a specific OID using SNMP",
            "help" : "",
            "tag" : "mpsnmpramsensor",
            "groups" : [
                {
                    "name" : "OID Racine values",
                    "caption" : "OID Racine values",
                    "fields" : [
                        {
                            "type": "edit",
                            "name": "oid",
                            "caption": "OID Racine Value",
                            "required": "1",
                            "help": "Please enter the OID value."
                        },
                        {
                            "type": "edit",
                            "name": "unit",
                            "caption": "Unit String",
                            "default": "#",
                            "help": "Enter a 'unit' string, e.g. 'ms', 'Kbyte' (for display purposes only)."
                        },
                        {
                            "type": "radio",
                            "name": "value_type",
                            "caption": "Value Type",
                            "required": "1",
                            "help": "Select 'Gauge' if you want to see absolute values (e.g. for temperature value) or 'Delta' for counter differences divided by time period (e.g. for bandwidth values)",
                            "options":{
                                "1":"Gauge",
                                "2":"Delta"
                            },
                            "default": 1
                        },
                        {
                            "type": "integer",
                            "name": "multiplication",
                            "caption": "Multiplication",
                            "required": "1",
                            "default": 1,
                            "help": "Provide a value the raw SNMP value is to be multipled by."
                        },
                        {
                            "type": "integer",
                            "name": "division",
                            "caption": "Division",
                            "required": "1",
                            "default": 1,
                            "help": "Provide a value the raw SNMP value is divided by."
                        },
                        {
                            "type": "radio",
                            "name": "snmp_version",
                            "caption": "SNMP Version",
                            "required": "1",
                            "help": "Choose your SNMP Version",
                            "options":{
                                "1":"V1",
                                "2":"V2c",
                                "3":"V3"
                            },
                            "default": 2
                        },
                        {
                            "type": "edit",
                            "name": "community",
                            "caption": "Community String",
                            "required": "1",
                            "help": "Please enter the community string."
                        },
                        {
                            "type": "integer",
                            "name": "port",
                            "caption": "Port",
                            "required": "1",
                            "default": 161,
                            "help": "Provide the SNMP port"
                        }
                    ]
                }
            ]
            }
        return sensordefinition

    def snmp_get(self, oid, target, snmpversion, type, community, port, unit, multiplication=1, division=1):
        try:
            sys.path.append('./')
            from pysnmp.entity.rfc3413.oneliner import cmdgen
        except Exception as e:
            pass
        snmpget = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinding = snmpget.getCmd(cmdgen.CommunityData(community), cmdgen.UdpTransportTarget((target, port)), oid)
        channellist = []

        if type == "1":
            channellist = [{"name": "Value",
                        "mode" : "integer",
                        "kind" : "custom",
                        "customunit" : "",
                        "value" : (int(varBinding[0][1]) * int(multiplication)) / int(division)
                        }]
        else:
            channellist = [{"name": "Value",
                        "mode" : "counter",
                        "kind" : "custom",
                        "customunit" : "%s" % unit,
                        "value" : (int(varBinding[0][1]) * int(multiplication)) / int(division)
                        }]
        return channellist


    @staticmethod
    def get_data(data, q=None):
        snmpram = SNMPRam()
        try:
            snmp_data_size = snmpram.snmp_get(str(data['oid'])+".5.1", data['host'], data['snmp_version'], data['value_type'], data['community'], int(data['port']), data['unit'], int(data['multiplication']),int(data['division']))
            snmp_data_used = snmpram.snmp_get(str(data['oid'])+".6.1", data['host'], data['snmp_version'], data['value_type'], data['community'], int(data['port']), data['unit'], int(data['multiplication']),int(data['division']))
        except Exception as e:
            #log.log_custom("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (snmpram.get_kind(), data['sensorid'], e))
            data = {
                "sensorid" : int(data['sensorid']),
                "error" : "Exception",
                "code" : 1,
                "message" : "SNMP Ram Request failed. See log for details",
            }
            return data
        snmp_data = str(int(snmp_data_size) - int(snmp_data_used))
        data = {
            "sensorid" : int(data['sensorid']),
            "message" : "OK",
            "channel":
                snmp_data
            }
        #del log
        del snmpram
        gc.collect()
        return data

