#!/usr/bin/env python

from nose.tools import *
from miniprobe import miniprobe

class TestMiniProbe():
    @classmethod
    def setup_class(cls):
        cls.http = False
        cls.config = {}
        cls.config['gid'] = 'testgid'
        cls.config['key'] = 'testkey'
        cls.config['protocol'] = 'testprotocol'
        cls.config['name'] = 'testname'
        cls.config['baseinterval'] = 'testbaseinterval'
        cls.config['server'] = 'testserver'
        cls.config['port'] = 'testport'
        cls.mp = miniprobe.MiniProbe(cls.http)

    def test_miniprobe_hash_access_key(self):
        """miniprobe returns the correct hash_access_key"""
        test_hash_access_key = self.mp
        assert_equal(test_hash_access_key.hash_access_key(self.config['key']), '913a73b565c8e2c8ed94497580f619397709b8b6')

    def test_miniprobe_create_parameters(self):
        """miniprobe returns the correct create_parameters"""
        test_create_parameters = self.mp
        assert_equal(test_create_parameters.create_parameters(self.config, '{}'), {'gid': 'testgid', 'protocol': 'testprotocol', 'key': '913a73b565c8e2c8ed94497580f619397709b8b6'})
        assert_equal(test_create_parameters.create_parameters(self.config, '{}', 'announce'), {'protocol': 'testprotocol', 'name': 'testname', 'gid': 'testgid', 'baseinterval': 'testbaseinterval', 'key': '913a73b565c8e2c8ed94497580f619397709b8b6', 'sensors': '{}'})

    def test_miniprobe_create_url(self):
        """miniprobe returns the correct create_url"""
        test_create_url = self.mp
        assert_equal(test_create_url.create_url(self.config), 'No method given')
        assert_equal(test_create_url.create_url(self.config, 'test'), 'https://testserver:testport/probe/test')
        assert_equal(test_create_url.create_url(self.config, 'data'), 'https://testserver:testport/probe/data?gid=testgid&protocol=testprotocol&key=913a73b565c8e2c8ed94497580f619397709b8b6')

    def test_build_task(self):
        """miniprobe returns correct task payload"""
        test_build_task = self.mp
        assert_equal(test_build_task.build_task(self.config), {'gid': 'testgid', 'protocol': 'testprotocol', 'key': '913a73b565c8e2c8ed94497580f619397709b8b6'})
