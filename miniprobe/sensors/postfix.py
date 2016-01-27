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


class Postfix(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mppostfix"
    
    @staticmethod       
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": Postfix.get_kind(),
            "name": "Postfix Mailqueue",
            "description": "Monitors the mailqueue of a postfix server",
            "help": "Monitors the mailqueue of a postfix server for active, deferred, hold or corrupt mail",
            "tag": "mppostfixsensor",
            "fields": [],
            "groups": []
        }
        return sensordefinition

    def check(self):
        spoolcmd = os.popen("postconf -h queue_directory")
        spooldir = spoolcmd.readline().replace('\n', '')
        spoolcmd.close()
        deferredcmd = os.popen("test -d %s/deferred && find %s/deferred -type f | wc -l" % (spooldir, spooldir))
        deferredcnt = deferredcmd.readline().replace('\n', '')
        deferredcmd.close()
        activecmd = os.popen("test -d %s/active && find %s/active -type f | wc -l" % (spooldir, spooldir))
        activecnt = activecmd.readline().replace('\n', '')
        activecmd.close()
        holdcmd = os.popen("test -d %s/hold && find %s/hold -type f | wc -l" % (spooldir, spooldir))
        holdcnt = holdcmd.readline().replace('\n', '')
        holdcmd.close()
        corruptcmd = os.popen("test -d %s/corrupt && find %s/corrupt -type f | wc -l" % (spooldir, spooldir))
        corruptcnt = corruptcmd.readline().replace('\n', '')
        corruptcmd.close()
        channel_list = [
            {
                "name": "Deferred mails",
                "mode": "integer",
                "unit": "Count",
                "limitmaxwarning": 40,
                "limitmaxerror": 50,
                "limitmode": 1,
                "value": deferredcnt
            },
            {
                "name": "Active mails",
                "mode": "integer",
                "unit": "Count",
                "value": activecnt
            },
            {
                "name": "Hold mails",
                "mode": "integer",
                "unit": "Count",
                "value": holdcnt
            },
            {
                "name": "Corrupt mails",
                "mode": "integer",
                "unit": "Count",
                "value": corruptcnt
            },
        ]
        return channel_list

    @staticmethod
    def get_data(data, out_queue):
        postfix = Postfix()
        try:
            postfixdata = postfix.check()
            data_r = {
                "sensorid": int(data['sensorid']),
                "message": "OK",
                "channel": postfixdata
            }
            logging.debug("Running sensor: %s" % postfix.get_kind())
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (postfix.get_kind(),
                                                                                         data['sensorid'], e))
            data_r = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "Postfix failed. %s" % e
            }
            out_queue.put(data_r)
            return 1
        del postfix
        gc.collect()
        out_queue.put(data_r)
        return 0
