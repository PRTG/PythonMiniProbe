#!/usr/bin/env python

from nose.tools import *
from miniprobe import miniprobe

config = {}
config['gid'] = 'testgid'
config['key'] = 'testkey'
config['protocol'] = 'testprotocol'
config['name'] = 'testname'
config['baseinterval'] = 'testbaseinterval'
config['server'] = 'testserver'
config['port'] = 'testport'

def test_miniprobe_hash_access_key():
    """miniprobe returns the correct hash_access_key"""
    test_hash_access_key = miniprobe.MiniProbe()
    assert_equal(test_hash_access_key.hash_access_key('test'), 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3')

def test_miniprobe_create_parameters():
    """miniprobe returns the correct create_parameters"""
    test_create_parameters = miniprobe.MiniProbe()
    assert_equal(test_create_parameters.create_parameters(config, '{}'), {'gid': 'testgid', 'protocol': 'testprotocol', 'key': '913a73b565c8e2c8ed94497580f619397709b8b6'})
    assert_equal(test_create_parameters.create_parameters(config, '{}', 'announce'), {'protocol': 'testprotocol', 'name': 'testname', 'gid': 'testgid', 'baseinterval': 'testbaseinterval', 'key': '913a73b565c8e2c8ed94497580f619397709b8b6', 'sensors': '{}'})

def test_miniprobe_create_url():
    """miniprobe returns the correct create_url"""
    test_create_url = miniprobe.MiniProbe()
    assert_equal(test_create_url.create_url(config), 'No method given')
    assert_equal(test_create_url.create_url(config, 'test'), 'https://testserver:testport/probe/test')
    assert_equal(test_create_url.create_url(config, 'data'), 'https://testserver:testport/probe/data?gid=testgid&protocol=testprotocol&key=913a73b565c8e2c8ed94497580f619397709b8b6')
