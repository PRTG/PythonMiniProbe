#!/usr/bin/env python

from nose.tools import *
from miniprobe import miniprobe

def test_miniprobe_hash_access_key():
    """miniprobe returns the correct hash_access_key"""
    test_hash_access_key = miniprobe.MiniProbe()
    assert_equal(test_hash_access_key.hash_access_key('test'), 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3')

