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
import json
import time
import gc
import logging
import socket
import warnings
from requests.packages.urllib3 import exceptions

# import own modules
sys.path.append('./')

try:
    from miniprobe import MiniProbe
    import sensors
    import requests
    import multiprocessing
except Exception as e:
    print e
    #sys.exit()

# Implemented for internal testing only. Not for public usage!
http = False
if sys.argv[1:] and sys.argv[1] == "http":
    http = True


def main():
        """
        Main routine for MiniProbe (Python)
        """
        # Enable Garbage Collection
        gc.enable()
        # make sure the probe will not stop
        probe_stop = False
        # make sure probe is announced at every start
        announce = False
        # read configuration file (existence check done in probe_controller.py)
        config = mini_probe.read_config('./probe.conf')
        logger = logging.getLogger("")
        if config['debug'] == "True":
            config['debug'] = True
            logger.setLevel(logging.DEBUG)
            logging.warning("DEBUG LOGGING HAS BEEN TURNED ON!!")
            logging.getLogger("requests").setLevel(logging.INFO)
        else:
            config['debug'] = False
            logger.setLevel(logging.INFO)
            logging.info("Debug logging has been turned off!!")
            logging.getLogger("requests").setLevel(logging.WARNING)
        if config['cleanmem'] == "True":
            config['cleanmem'] = True
        else:
            config['cleanmem'] = False
        # Doing some startup logging
        logging.info("PRTG Small Probe '%s' starting on '%s'" % (config['name'], socket.gethostname()))
        logging.info("Connecting to PRTG Core Server at %s:%s" % (config['server'], config['port']))
        # create hash of probe access key
        key_sha1 = mini_probe.hash_access_key(config['key'])
        # get list of all sensors announced in __init__.py in package sensors
        sensor_list = mini_probe.get_import_sensors()
        sensor_announce = mini_probe.build_announce(sensor_list)
        announce_json = json.dumps(sensor_announce)
        url_announce = mini_probe.create_url(config, 'announce', http)
        data_announce = mini_probe.create_parameters(config, announce_json, 'announce')
        logging.debug("Announce Data: %s" % data_announce)
        json_history = []
        timeout = False

        while not announce:
            try:
                # announcing the probe and all sensors
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", exceptions.InsecureRequestWarning)
                    request_announce = requests.post(url_announce, data=data_announce, verify=False, timeout=30)

                announce = True
                logging.info("ANNOUNCE request successfully sent to PRTG Core Server at %s:%s."
                             % (config["server"], config["port"]))
                logging.debug("Connecting to %s:%s" % (config["server"], config["port"]))
                logging.debug("Status Code: %s | Message: %s" % (request_announce.status_code,
                                                                     request_announce.text))
                request_announce.close()
            except requests.exceptions.Timeout:
                logging.error("ANNOUNCE Timeout: " + str(data_announce))
            except Exception as announce_error:
                logging.error(announce_error)
                time.sleep(int(config['baseinterval']) / 2)

        while not probe_stop:
            # creating some objects only needed in loop
            url_task = mini_probe.create_url(config, 'tasks', http)
            task_data = {
                'gid': config['gid'],
                'protocol': config['protocol'],
                'key': key_sha1
            }
            procs = []
            out_queue = multiprocessing.Queue()
            task = False
            while not task:
                json_payload_data = []
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", exceptions.InsecureRequestWarning)
                        request_task = requests.post(url_task, data=task_data, verify=False, timeout=30)
                    logging.debug(request_task.headers)
                    logging.debug(request_task.text)
                    json_response = request_task.json()
                    request_task.close()
                    gc.collect()
                    task = True
                    logging.info("TASK request successfully sent to PRTG Core Server at %s:%s. Status: %s"
                                 % (config["server"], config["port"], request_task.status_code))
                    logging.debug("task_url: " + url_task + "\ntask_data: " + str(task_data))
                except requests.exceptions.Timeout:
                    logging.error("TASK Timeout: " + str(task_data))
                    logging.debug("Timeout encountered. Need to write more code to handle timeoutzzzzz: %s" % json_history)
                    timeout = True
                except Exception as announce_error:
                    logging.error(announce_error)
                    time.sleep(int(config['baseinterval']) / 2)
            gc.collect()
            if str(json_response) != '[]':
                json_history = json_response
                logging.debug("json response: %s" % json_response)
                if config['subprocs']:
                    json_response_chunks = [json_response[i:i + int(config['subprocs'])]
                                            for i in range(0, len(json_response), int(config['subprocs']))]
                else:
                    json_response_chunks = [json_response[i:i + 10]
                                            for i in range(0, len(json_response), 10)]
                for element in json_response_chunks:
                    for part in element:
                        logging.debug(part)
                        for sensor in sensor_list:
                            if part['kind'] == sensor.get_kind():
                                p = multiprocessing.Process(target=sensor.get_data, args=(part, out_queue),
                                                            name=part['kind'])
                                procs.append(p)
                                p.start()
                            else:
                                pass
                        gc.collect()
                    try:
                        while len(json_payload_data) < len(element):
                            out = out_queue.get()
                            json_payload_data.append(out)
                    except Exception as e:
                        logging.error(e)
                        pass

                    url_data = mini_probe.create_url(config, 'data', http)
                    try:
                        request_data = requests.post(url_data, data=json.dumps(json_payload_data), verify=False, timeout=30)
                        logging.info("DATA request successfully sent to PRTG Core Server at %s:%s. Status: %s"
                                     % (config["server"], config["port"], request_data.status_code))
                        logging.debug("data_url: " + url_data + "\ndata_data: " + str(json_payload_data))
                        request_data.close()
                        json_payload_data = []
                    except requests.exceptions.Timeout:
                        logging.error("DATA Timeout: " + str(json_payload_data).strip('[]'))
                    except Exception as announce_error:
                        logging.error(announce_error)
                    if len(json_response) > 10:
                        time.sleep((int(config['baseinterval']) * (9 / len(json_response))))
                    else:
                        time.sleep(int(config['baseinterval']) / 2)

            else:
                logging.info("Nothing to do. Waiting for %s seconds." % (int(config['baseinterval']) / 3))
                time.sleep(int(config['baseinterval']) / 3)

            # Delete some stuff used in the loop and run the garbage collector
            for p in procs:
                if not p.is_alive():
                    p.join()
                    p.terminate()
                    del p
            del json_response
            del json_payload_data
            gc.collect()

            if config['cleanmem']:
                # checking if the clean memory option has been chosen during install then call the method to flush mem
                mini_probe.clean_mem()
        sys.exit()

if __name__ == "__main__":
    mini_probe = MiniProbe()
    main()
