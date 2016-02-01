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

import sys
import gc
import logging

try:
    from pysnmp.entity.rfc3413.oneliner import cmdgen
    snmp = True
except Exception as e:
    logging.error("PySNMP could not be imported. SNMP Sensors won't work.Error: %s" % e)
    snmp = False
    pass


class SNMPLoad(object):

    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpsnmpload"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": SNMPLoad.get_kind(),
            "name": "SNMP Load",
            "description": "Monitors a numerical value returned by a specific OID using SNMP",
            "help": "Monitors a numerical value returned by a specific OID using SNMP",
            "tag": "mpsnmploadsensor",
            "groups": [
                {
                    "name": "OID values",
                    "caption": "OID values",
                    "fields": [
                        {
                            "type": "radio",
                            "name": "snmp_version",
                            "caption": "SNMP Version",
                            "required": "1",
                            "help": "Choose your SNMP Version",
                            "options": {
                                "1": "V1",
                                "2": "V2c",
                                "3": "V3"
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
        if not snmp:
            sensordefinition = ""
        return sensordefinition

    def snmp_get(self, target, community, port):
        try:
            sys.path.append('./')
            from pysnmp.entity.rfc3413.oneliner import cmdgen

            data = ['.1.3.6.1.4.1.2021.10.1.3.1','.1.3.6.1.4.1.2021.10.1.3.2','.1.3.6.1.4.1.2021.10.1.3.3'] 

            snmpget = cmdgen.CommandGenerator()
            error_indication, error_status, error_index, var_binding = snmpget.getCmd(
                cmdgen.CommunityData(community), cmdgen.UdpTransportTarget((target, port)), *data
            )
        except Exception as import_error:
            logging.error(import_error)
            raise

        channel_list = [ 
            {   
                "name": "Load Average 1min",
                "mode": "float",
                "kind": "Custom",
                "customunit": "", 
                "value": float(var_binding[0][1])
            },  
            {   
                "name": "Load Average 5min",
                "mode": "float",
                "kind": "Custom",
                "customunit": "", 
                "value": float(var_binding[1][1])
            },  
            {   
                "name": "Load Average 10min",
                "mode": "float",
                "kind": "Custom",
                "customunit": "", 
                "value": float(var_binding[2][1])
            }
        ]
        return channel_list

    @staticmethod
    def get_data(data, out_queue):
        snmpcustom = SNMPLoad()
        try:
            snmp_data = snmpcustom.snmp_get(
                data['host'], 
                data['community'], 
                int(data['port'])
            )
            logging.debug("Running sensor: %s" % snmpcustom.get_kind())
        except Exception as get_data_error:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (snmpcustom.get_kind(),
                                                                                         data['sensorid'],
                                                                                         get_data_error))
            data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "SNMP Request failed. See log for details"
            }
            out_queue.put(data)
            return 1

        data = {
            "sensorid": int(data['sensorid']),
            "message": "OK",
            "channel": snmp_data
        }
        del snmpcustom
        gc.collect()
        out_queue.put(data)
        return 0
