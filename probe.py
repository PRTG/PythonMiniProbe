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


### PRTG Python Miniprobe
### Miniprobe needs at least Python 2.7 because of "importlib"
### If older python version is used you will have to install "importlib"

# import general modules
import sys
import hashlib
import json
import time
import importlib
import gc

# import own modules
sys.path.append('./')

try:
    from logger import Logger
    # import external modules
    import sensors
    import requests
except Exception as e:
    print e
    #sys.exit()


class Probe(object):
    """
    Main class for the Python Mini Probe
    """
    def __init__(self):
        gc.enable()
        self.log = Logger()
        pass

    def get_import_sensors(self):
        """
        import available sensor modules and return list of sensor objects
        """
        sensor_objects = []
        for mod in sensors.__all__:
            try:
                sensor_objects.append(self.load_class("sensors.%s.%s" % (mod.lower(), mod)))
            except Exception as import_error:
                print import_error
        return sensor_objects

    def load_class(self, full_class_string):
        """
        dynamically load a class from a string
        """
        class_data = full_class_string.split(".")
        module_path = ".".join(class_data[:-1])
        class_str = class_data[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_str)

    def read_config(self, path):
        """
        read configuration file and write data to dict
        """
        config = {}
        try:
            conf_file = open(path)
            for line in conf_file:
                if not (line == '\n'):
                    if not (line.startswith('#')):
                        config[line.split(':')[0]] = line.split(':')[1].rstrip()
            conf_file.close()
            return config
        except Exception as read_error:
            self.log.log("No config found! Error Message: %s Exiting!" % read_error)
            sys.exit()

    def hash_access_key(self, key):
        """
        create hash of probes access key
        """
        return hashlib.sha1(key).hexdigest()

    def create_parameters(self, config, jsondata, i=None):
        """
        create URL parameters for announce, task and data requests
        """
        if i == 'announce':
            return {'gid': config['gid'], 'key': self.hash_access_key(config['key']), 'protocol': config['protocol'],
                    'name': config['name'], 'baseinterval': config['baseinterval'], 'sensors': jsondata}
        else:
            return {'gid': config['gid'], 'key': self.hash_access_key(config['key']), 'protocol': config['protocol']}

    def create_url(self, config, i=None):
        """
        creating the actual URL
        """

        if not (i is None) and (i != "data"):
            return "https://%s:%s/probe/%s" % (
                config['server'], config['port'], i)
        elif i == "data":
            return "https://%s:%s/probe/%s?gid=%s&protocol=%s&key=%s" % (config['server'], config['port'], i,
                                                                         config['gid'], config['protocol'],
                                                                         self.hash_access_key(config['key']))
            pass
        else:
            return "No method given"

    def build_announce(self, sensor_list):
        """
        build json for announce request
        """
        sensors_avail = []
        for sensor in sensor_list:
            sensors_avail.append(sensor.get_sensordef())
        return sensors_avail

    def main(self):
        """
        Main routine for MiniProbe (Python)
        """
        # Enable Garbage Collection
        gc.enable()
        # make sure the probe will not stop
        probe_stop = False
        # Create instance of Logger to provide logging
        log = Logger()
        # make sure probe is announced at every start
        announce = False
        # read configuration file (existence check done in probe_controller.py)
        config = mini_probe.read_config('./probe.conf')
        # create hash of probe access key
        key_sha1 = mini_probe.hash_access_key(config['key'])
        # get list of all sensors announced in __init__.py in package sensors
        sensor_list = mini_probe.get_import_sensors()
        sensor_announce = mini_probe.build_announce(sensor_list)
        announce_json = json.dumps(sensor_announce)
        url_announce = mini_probe.create_url(config, 'announce')
        data_announce = mini_probe.create_parameters(config, announce_json, 'announce')

        while not announce:
            try:
                # announcing the probe and all sensors
                request_announce = requests.get(url_announce, params=data_announce, verify=False)
                announce = True
                log.log(True, None, config, "ANNOUNCE", None, None)
                if config['debug']:
                    log.log_custom(config['server'])
                    log.log_custom(config['port'])
                    log.log_custom("Status Code: %s | Message: %s" % (request_announce.status_code,
                                                                      request_announce.text))
                request_announce.close()
            except Exception as announce_error:
                log.log_custom(announce_error)
                time.sleep(int(config['baseinterval']) / 2)

        while not probe_stop:
            # creating some objects only needed in loop
            url_task = mini_probe.create_url(config, 'tasks')
            task_data = {
                'gid': config['gid'],
                'protocol': config['protocol'],
                'key': key_sha1
            }
            task = False
            while not task:
                json_payload_data = []
                try:
                    request_task = requests.get(url_task, params=task_data, verify=False)
                    json_response = request_task.json()
                    request_task.close()
                    gc.collect()
                    task = True
                    log.log(True, None, config, "TASK", None, None)
                    if config['debug']:
                        log.log_custom(url_task)
                except Exception as announce_error:
                    log.log_custom(announce_error)
                    time.sleep(int(config['baseinterval']) / 2)
            gc.collect()
            if str(json_response) != '[]':
                json_response_chunks = [json_response[i:i + 10] for i in range(0, len(json_response), 10)]
                for element in json_response_chunks:
                    for part in element:
                        if config['debug']:
                            log.log_custom(part)
                        for sensor in sensor_list:
                            if part['kind'] == sensor.get_kind():
                                json_payload_data.append(sensor.get_data(part))
                            else:
                                pass
                        gc.collect()
                    url_data = mini_probe.create_url(config, 'data')
                    try:
                        request_data = requests.post(url_data, data=json.dumps(json_payload_data), verify=False)
                        log.log(True, None, config, "DATA", None, None)

                        if config['debug']:
                            log.log_custom(json_payload_data)
                        request_data.close()
                        json_payload_data = []
                    except Exception as announce_error:
                        log.log_custom(announce_error)
                    if len(json_response) > 10:
                        time.sleep((int(config['baseinterval']) * (9 / len(json_response))))
                    else:
                        time.sleep(int(config['baseinterval']) / 2)
            else:
                log.log(True, "Nothing", config, None, None, None)
                time.sleep(int(config['baseinterval']) / 3)

            # Delete some stuff used in the loop and run the garbage collector
            del json_response
            del json_payload_data
            gc.collect()

            if config['cleanmem']:
                # checking if the clean memory option has been chosen during install then call the method to flush mem
                from utils import Utils
                Utils.clean_mem()
        sys.exit()

if __name__ == "__main__":
    mini_probe = Probe()
    mini_probe.main()
