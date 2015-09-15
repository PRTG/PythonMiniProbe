#!/usr/bin/env python
# With nice greetings from Dynam-IT GbR
# Suggestion for a mdadm-raid sensor
# Thanks to Paessler for providing the free PRTG Python Probe and the API

import os
# import re for use of re.split; explained below
import re
import gc
import logging


class MDADM(object):
    def __init__(self):
        gc.enable()

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpmdadm"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": MDADM.get_kind(),
            "name": "MDADM RAID Status",
            "description": "Monitors status of RAID arrays provided by MDADM",
            "help": "Count total number of Arrays, count arrays with missing drives,count arrays resyncing, recovering and checking",
            "tag": "mpmdadmsensor",
            "fields": [],
            "groups": []

        }
        return sensordefinition

    def check(self):

        # Get the standard information output of mdadm and count
        numberOfArrays = os.popen("grep ^md -c /proc/mdstat").read()
        arraysMissingDrives = 0
        arraysRecovering = 0
        arraysResyncing = 0
        arraysChecking = 0

        ret = os.popen("cat /proc/mdstat").readlines()
        mdstat = ' '.join([line.strip() for line in ret])
        # Using re.split to split output instead of split to prevent cutting the leading "md"
        raidArrayList = re.split(' (?=md)', mdstat)

        for index in range(len(raidArrayList)):
            # Searching for list entries beginning with "md"
            if re.match('^md', raidArrayList[index]):
                    print raidArrayList[index]
                    if '_' in raidArrayList[index]:
                            # adrive missing can also be a defect drive. Defect or missing drives are marked with an "_" instead of an "U" in the drive list
                            arraysMissingDrives += 1
                    if 'recovering' in raidArrayList[index]:
                            arraysRecovering += 1
                    if 'resync' in raidArrayList[index]:
                            arraysResyncing += 1
                    if 'check' in raidArrayList[index]:
                            arraysChecking += 1

        channel_list = [
            {
                "name": "Total count of RAID arrays",
                "mode": "integer",
                "unit": "count",
                "limitmaxwarning": 0,
                "limitmode": 0,
                "value": numberOfArrays
            },
            {
                "name": "RAID arrays with missing drives",
                "mode": "integer",
                "unit": "count",
                # setting this channel to error if arraysMissingDrives is > 0
                "limitmaxerror": 0,
                "limitmode": 1,
                "value": arraysMissingDrives
            },
            {
                "name": "RAID arrays recovering",
                "mode": "integer",
                "unit": "count",
                "limitmaxwarning": 0,
                "limitmode": 1,
                "value": arraysRecovering
            },
            {
                "name": "RAID arrays resyncing",
                "mode": "integer",
                "unit": "count",
                "limitmaxwarning": 0,
                "limitmode": 1,
                "value": arraysResyncing
            },
            {
                "name": "RAID arrays in automatic checking task",
                "mode": "integer",
                "unit": "count",
                # In many linux distributions an array check is performed automatically once a day or week. So we should not warn about this
                "limitmaxwarning": 0,
                "limitmode": 0,
                "value": arraysChecking
            },
            ]
        return channel_list

    @staticmethod
    def get_data(data, out_queue):
        mdadm = MDADM()
        try:
            mdadmdata = mdadm.check()
            data_r = {
                "sensorid": int(data['sensorid']),
                "message": "OK",
                "channel": mdadmdata
            }
            logging.debug("Running sensor: %s" % mdadm.get_kind())
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (mdadm.get_kind(),
                                                                                         data['sensorid'], e))
            data_r = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "MDADM Sensor failed. %s" % e
            }
            out_queue.put(data_r)
            return 1
        del mdadm
        gc.collect()
        out_queue.put(data_r)
        return 0
