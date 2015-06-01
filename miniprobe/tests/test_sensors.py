#!/usr/bin/env python

from nose.tools import *
from miniprobe.sensors import nmap,adns,apt,cpuload,cputemp,snmptraffic

def test_nmap_get_kind():
    """nmap returns the correct kind"""
    test_nmap = nmap.NMAP()
    assert_equal(test_nmap.get_kind(), 'mpnmap')

def test_nmap_icmp_echo_request():
    """nmap const ICMP_ECHO_REQUEST is set correct"""
    test_nmap = nmap.NMAP()
    assert_equal(test_nmap.ICMP_ECHO_REQUEST, 8)

def test_nmap_dec2bin():
    """nmap dec2bin results"""
    test_nmap = nmap.NMAP()
    assert_equal(test_nmap.dec2bin(255,8),'11111111')
    assert_equal(test_nmap.dec2bin(254,8),'11111110')
    assert_equal(test_nmap.dec2bin(128,8),'10000000')
    assert_equal(test_nmap.dec2bin(127,8),'01111111')
    assert_equal(test_nmap.dec2bin(0,8),'00000000')

def test_nmap_ip2bin():
    """nmap ip2bin results"""
    test_nmap = nmap.NMAP()
    assert_equal(test_nmap.ip2bin('255.255.255.255'),'11111111111111111111111111111111')
    assert_equal(test_nmap.ip2bin('254.254.254.254'),'11111110111111101111111011111110')
    assert_equal(test_nmap.ip2bin('128.128.128.128'),'10000000100000001000000010000000')
    assert_equal(test_nmap.ip2bin('127.127.127.127'),'01111111011111110111111101111111')
    assert_equal(test_nmap.ip2bin('0.0.0.0'),'00000000000000000000000000000000')

def test_nmap_bin2ip():
    """nmap bin2ip results"""
    test_nmap = nmap.NMAP()
    assert_equal(test_nmap.bin2ip('11111111111111111111111111111111'),'255.255.255.255')
    assert_equal(test_nmap.bin2ip('11111110111111101111111011111110'),'254.254.254.254')
    assert_equal(test_nmap.bin2ip('10000000100000001000000010000000'),'128.128.128.128')
    assert_equal(test_nmap.bin2ip('01111111011111110111111101111111'),'127.127.127.127')
    assert_equal(test_nmap.bin2ip('00000000000000000000000000000000'),'0.0.0.0')

def test_nmap_validateCIDRBlock():
    """nmap validateCIDRBlock results"""
    test_nmap = nmap.NMAP()
    assert_equal(test_nmap.validateCIDRBlock('127.0.0.0'),'Error: Invalid CIDR format!')
    assert_equal(test_nmap.validateCIDRBlock('256.256.256.256/8'),'Error: quad 256 wrong size.')
    assert_equal(test_nmap.validateCIDRBlock('127.0.0.0/33'),'Error: subnet 33 wrong size.')
    assert_true(test_nmap.validateCIDRBlock('127.0.0.0/8'))

def test_nmap_returnCIDR():
    """nmap returnCIDR results"""
    test_nmap = nmap.NMAP()
    assert_equal(test_nmap.returnCIDR('127.0.0.0/30'),['127.0.0.0', '127.0.0.1', '127.0.0.2', '127.0.0.3'])

def test_nmap_checksum():
    """nmap checksum results"""
    test_nmap = nmap.NMAP()
    assert_equal(test_nmap.checksum('test'),6182)
    assert_equal(test_nmap.checksum('python'),43951)
    assert_equal(test_nmap.checksum('prtg'),6950)

def test_adns_get_kind():
    """dns returns the correct kind"""
    test_adns = adns.aDNS()
    assert_equal(test_adns.get_kind(), 'mpdns')

def test_apt_get_kind():
    """apt returns the correct kind"""
    test_apt = apt.APT()
    assert_equal(test_apt.get_kind(), 'mpapt')

def test_cpuload_get_kind():
    """cpuload returns the correct kind"""
    test_cpuload = cpuload.CPULoad()
    assert_equal(test_cpuload.get_kind(), 'mpcpuload')

def test_cputemp_get_kind():
    """cputemp returns the correct kind"""
    test_cputemp = cputemp.CPUTemp()
    assert_equal(test_cputemp.get_kind(), 'mpcputemp')


def test_snmptraffic_get_kind():
    """cputemp returns the correct kind"""
    test_snmptraffic = snmptraffic.SNMPTraffic()
    assert_equal(test_snmptraffic.get_kind(), 'mpsnmptraffic')

