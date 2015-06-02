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
import re
import os
import sys
import struct
import select
from itertools import islice

class NMAP(object):
    ICMP_ECHO_REQUEST = 8

    def __init__(self):
        pass

    @staticmethod
    def get_kind():
        """
        return sensor kind
        """
        return "mpnmap"

    @staticmethod
    def get_sensordef():
        """
        Definition of the sensor and data to be shown in the PRTG WebGUI
        """
        sensordefinition = {
            "kind": NMAP.get_kind(),
            "name": "NMAP",
            "description": "Checks the availability of systems.",
            "help": "Checks the availability of systems on a network and logs this to a separate logfile on the miniprobe.",
            "tag": "mpnmapsensor",
            "groups": [
                {
                    "name": "nmapspecific",
                    "caption": "NMAP specific",
                    "fields": [
                        {
                            "type": "integer",
                            "name": "timeout",
                            "caption": "Timeout (in ms)",
                            "required": "1",
                            "default": 50,
                            "minimum": 10,
                            "maximum": 1000,
                            "help": "If the reply takes longer than this value the request is aborted "
                                    "and an error message is triggered. Max. value is 1000 ms. (=1 sec.)"
                        },
                        {
                            "type": "edit",
                            "name": "ip",
                            "caption": "IP-Address(es)",
                            "required": "1",
                            "default": "",
                            "help": "Specify the ip-address or a range of addresses using one of the following notations:[br]Single: 192.168.1.1[br]CIDR: 192.168.1.0/24[br]- separated: 192.168.1.1-192.168.1.100"
                        }
                    ]
                }
            ]
        }
        return sensordefinition

    @staticmethod
    def get_data(data, out_queue):
        nmap = NMAP()
        error = False
        tmpMessage = ""
        cidr = ""
        alive_str = ""
        alive_cnt = 0
        try:
            logging.debug("Running sensor: %s" % nmap.get_kind())
            if '/' in data['ip']:
                validCIDR = nmap.validateCIDRBlock(data['ip'])
                if validCIDR:
                    tmpMessage = "True"
                    cidr = nmap.returnCIDR(data['ip'])
                    for ip in islice(cidr, 1, len(cidr)-1):
                        result = nmap.do_one_ping(ip, float(data['timeout'])/1000)
                        if not result == None:
                            alive_str = alive_str + ip + ": " + str(int(result * 1000)) + " ms, "
                            alive_cnt = alive_cnt + 1
                else:
                    tmpMessage = validCIDR
                    error = True
            channel_list = [
                {
                    "name": "Hosts alive",
                    "mode": "Integer",
                    "kind": "count",
                    "value": alive_cnt
                }]
        except Exception as e:
            logging.error("Ooops Something went wrong with '%s' sensor %s. Error: %s" % (nmap.get_kind(),
                                                                                         data['sensorid'], e))
            sensor_data = {
                "sensorid": int(data['sensorid']),
                "error": "Exception",
                "code": 1,
                "message": "Port check failed or ports closed. See log for details"
            }
            out_queue.put(sensor_data)
            return 1
        sensor_data = {
            "sensorid": int(data['sensorid']),
            "message": alive_str[:-2],
            "channel": channel_list
        }
        del nmap
        gc.collect()
        out_queue.put(sensor_data)
        return 0

    def ip2bin(self,ip):
        b = ""
        nmap = NMAP()
        inQuads = ip.split(".")
        outQuads = 4
        for q in inQuads:
            if q != "":
                b += nmap.dec2bin(int(q),8)
                outQuads -= 1
        while outQuads > 0:
            b += "00000000"
            outQuads -= 1
        return b

    def dec2bin(self,n,d=None):
        s = ""
        while n>0:
            if n&1:
                s = "1"+s
            else:
                s = "0"+s
            n >>= 1
        if d is not None:
            while len(s)<d:
                s = "0"+s
        if s == "": s = "0"
        return s

    def bin2ip(self,b):
        ip = ""
        for i in range(0,len(b),8):
            ip += str(int(b[i:i+8],2))+"."
        return ip[:-1]

    def validateCIDRBlock(self,b):
        # appropriate format for CIDR block ($prefix/$subnet)
        p = re.compile("^([0-9]{1,3}\.){0,3}[0-9]{1,3}(/[0-9]{1,2}){1}$")
        if not p.match(b):
            return "Error: Invalid CIDR format!"
        # extract prefix and subnet size
        prefix, subnet = b.split("/")
        # each quad has an appropriate value (1-255)
        quads = prefix.split(".")
        for q in quads:
            if (int(q) < 0) or (int(q) > 255):
                return "Error: quad "+str(q)+" wrong size."
        # subnet is an appropriate value (1-32)
        if (int(subnet) < 1) or (int(subnet) > 32):
            return "Error: subnet "+str(subnet)+" wrong size."
        # passed all checks -> return True
        return True

    def returnCIDR(self,c):
        nmap = NMAP()
        ips = []
        parts = c.split("/")
        baseIP = nmap.ip2bin(parts[0])
        subnet = int(parts[1])
        # Python string-slicing weirdness:
        # "myString"[:-1] -> "myStrin" but "myString"[:0] -> ""
        # if a subnet of 32 was specified simply print the single IP
        if subnet == 32:
            return nmap.bin2ip(baseIP)
        # for any other size subnet, print a list of IP addresses by concatenating
        # the prefix with each of the suffixes in the subnet
        else:
            ipPrefix = baseIP[:-(32-subnet)]
            for i in range(2**(32-subnet)):
                ips.append(nmap.bin2ip(ipPrefix+nmap.dec2bin(i, (32-subnet))))
            return ips

    def checksum(self, source_string):
        """
        I'm not too confident that this is right but testing seems
        to suggest that it gives the same answers as in_cksum in ping.c
        """
        sum = 0
        countTo = (len(source_string)/2)*2
        count = 0
        while count<countTo:
            thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
            sum = sum + thisVal
            sum = sum & 0xffffffff # Necessary?
            count = count + 2
        if countTo<len(source_string):
            sum = sum + ord(source_string[len(source_string) - 1])
            sum = sum & 0xffffffff # Necessary?
        sum = (sum >> 16)  +  (sum & 0xffff)
        sum = sum + (sum >> 16)
        answer = ~sum
        answer = answer & 0xffff
        # Swap bytes. Bugger me if I know why.
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer

    def receive_one_ping(self, my_socket, ID, timeout):
        """
        receive the ping from the socket.
        """
        timeLeft = float(timeout)
        while True:
            startedSelect = time.time()
            whatReady = select.select([my_socket], [], [], timeLeft)
            howLongInSelect = (time.time() - startedSelect)
            if whatReady[0] == []: # Timeout
                return
            timeReceived = time.time()
            recPacket, addr = my_socket.recvfrom(1024)
            icmpHeader = recPacket[20:28]
            type, code, checksum, packetID, sequence = struct.unpack(
                "bbHHh", icmpHeader
            )
            if packetID == ID:
                bytesInDouble = struct.calcsize("d")
                timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
                return timeReceived - timeSent
            timeLeft = timeLeft - howLongInSelect
            if timeLeft <= 0:
                return

    def send_one_ping(self, my_socket, dest_addr, ID):
        """
        Send one ping to the given >dest_addr<.
        """
        dest_addr  =  socket.gethostbyname(dest_addr)
        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        my_checksum = 0
        # Make a dummy heder with a 0 checksum.
        header = struct.pack("bbHHh", self.ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
        bytesInDouble = struct.calcsize("d")
        data = (192 - bytesInDouble) * "Q"
        data = struct.pack("d", time.time()) + data
        # Calculate the checksum on the data and the dummy header.
        my_checksum = self.checksum(header + data)
        # Now that we have the right checksum, we put that in. It's just easier
        # to make up a new header than to stuff it into the dummy.
        header = struct.pack(
            "bbHHh", self.ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
        )
        packet = header + data
        my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1

    def do_one_ping(self, dest_addr, timeout):
        """
        Returns either the delay (in seconds) or none on timeout.
        """
        icmp = socket.getprotobyname("icmp")
        try:
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        except socket.error, (errno, msg):
            if errno == 1:
                # Operation not permitted
                msg = msg + (
                    " - Note that ICMP messages can only be sent from processes"
                    " running as root."
                )
                raise socket.error(msg)
            raise # raise the original error
        my_ID = os.getpid() & 0xFFFF
        self.send_one_ping(my_socket, dest_addr, my_ID)
        delay = self.receive_one_ping(my_socket, my_ID, timeout)
        my_socket.close()
        return delay
