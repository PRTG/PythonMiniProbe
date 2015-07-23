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

# PRTG Python Miniprobe
# Miniprobe needs at least Python 2.7 because of "importlib"
# If older python version is used you will have to install "importlib"

# import general modules
import sys
import json
import time
import gc
import logging
import socket

# import own modules
sys.path.append('./')
try:
    from miniprobe import MiniProbe
    import sensors
    import requests
    import multiprocessing
except Exception as e:
    print(e)

# Implemented for internal testing only. Not for public usage!
http = False
if sys.argv[1:] and sys.argv[1] == "http":
    http = True


class Probe(object):
    def __init__(self):
        gc.enable()
        self.mini_probe = MiniProbe(http)
        self.config = self.mini_probe.read_config('./probe.conf')
        self.probe_stop = False
        self.announce = False
        self.task = False
        self.key_sha1 = self.mini_probe.hash_access_key(self.config['key'])
        self.out_queue = multiprocessing.Queue()
        self.sensor_list = self.mini_probe.get_import_sensors()
        self.announce_json = json.dumps(self.mini_probe.build_announce(self.sensor_list))
        self.announce_data = self.mini_probe.create_parameters(self.config, self.announce_json, 'announce')
        self.url_announce = self.mini_probe.create_url(self.config, 'announce', http)
        self.url_task = self.mini_probe.create_url(self.config, 'tasks', http)
        self.task_data = self.mini_probe.build_task(self.config)
        self.url_data = self.mini_probe.create_url(self.config, 'data', http)
        self.procs = []
        # Set up debug logging
        self.logger = logging.getLogger("")
        if self.config['debug'] == "True":
            self.config['debug'] = True
            self.logger.setLevel(logging.DEBUG)
            logging.warning("DEBUG LOGGING HAS BEEN TURNED ON!!")
            logging.getLogger("requests").setLevel(logging.INFO)
        else:
            self.config['debug'] = False
            self.logger.setLevel(logging.INFO)
            logging.info("Debug logging has been turned off!!")
            logging.getLogger("requests").setLevel(logging.WARNING)
        if self.config['cleanmem'] == "True":
            self.config['cleanmem'] = True
        else:
            self.config['cleanmem'] = False

    def main(self):
            """
            Main routine for MiniProbe (Python)
            """
            # Doing some startup logging
            logging.info("PRTG Small Probe '%s' starting on '%s'" % (self.config['name'], socket.gethostname()))
            logging.info("Connecting to PRTG Core Server at %s:%s" % (self.config['server'], self.config['port']))
            while not self.announce:
                try:
                    announce_request = self.mini_probe.request_to_core("announce", self.announce_data, self.config)
                    if announce_request.status_code == requests.codes.ok:
                        self.announce = True
                        logging.info("Announce success.")
                        logging.debug("Announce success. Details: HTTP Status %s, Message: %s"
                                      % (announce_request.status_code, announce_request.text))
                    else:
                        logging.info("Announce pending. Trying again in %s seconds"
                                     % str(int(self.config['baseinterval']) / 2))
                        logging.debug("Announce pending. Details: HTTP Status %s, Message: %s"
                                      % (announce_request.status_code, announce_request.text))
                        time.sleep(int(self.config['baseinterval']) / 2)
                except Exception as request_exception:
                    logging.error(request_exception)
                    time.sleep(int(self.config['baseinterval']) / 2)

            while not self.probe_stop:
                self.task = False
                while not self.task:
                    json_payload_data = []
                    has_json_content = False
                    try:
                        task_request = self.mini_probe.request_to_core("tasks", self.task_data, self.config)
                        try:
                            if str(task_request.json()) != "[]":
                                json_response = task_request.json()
                                has_json_content = True
                                self.task = True
                                logging.info("Task success.")
                                logging.debug("Task success. HTTP Status %s, Message: %s"
                                              % (task_request.status_code, task_request.text))
                            else:
                                logging.info("Task has no JSON content. Trying again in %s seconds"
                                             % (time.sleep(int(self.config['baseinterval']) / 2)))
                                logging.debug("Task has no JSON content. Details: HTTP Status %s, Message: %s"
                                              % (task_request.status_code, task_request.text))
                                time.sleep(int(self.config['baseinterval']) / 2)
                        except Exception as json_exception:
                            logging.info(json_exception)
                            logging.info("No JSON. HTTP Status: %s, Message: %s"
                                         % (task_request.status_code, task_request.text))
                    except Exception as request_exception:
                        logging.error(request_exception)
                        time.sleep(int(self.config['baseinterval']) / 2)

                gc.collect()
                if task_request.status_code == requests.codes.ok and has_json_content:
                    logging.debug("JSON response: %s" % json_response)
                    if self.config['subprocs']:
                        json_response_chunks = self.mini_probe.split_json_response(json_response,
                                                                                   self.config['subprocs'])
                    else:
                        json_response_chunks = self.mini_probe.split_json_response(json_response)
                    for element in json_response_chunks:
                        for part in element:
                            logging.debug(part)
                            for sensor in self.sensor_list:
                                if part['kind'] == sensor.get_kind():
                                    p = multiprocessing.Process(target=sensor.get_data, args=(part, self.out_queue),
                                                                name=part['kind'])
                                    self.procs.append(p)
                                    p.start()
                                else:
                                    pass
                            gc.collect()
                        try:
                            while len(json_payload_data) < len(element):
                                out = self.out_queue.get()
                                json_payload_data.append(out)
                        except Exception as data_queue_exception:
                            logging.error(data_queue_exception)
                            pass

                        try:
                            data_request = self.mini_probe.request_to_core("data", json.dumps(json_payload_data),
                                                                           self.config)
                            if data_request.status_code == requests.codes.ok:
                                logging.info("Data success.")
                                logging.debug("Data success. Details: HTTP Status %s, Message: %s"
                                              % (data_request.status_code, data_request.text))
                                json_payload_data = []
                            else:
                                logging.info("Data issue. Current data might be dropped, please turn on debug logging")
                                logging.debug("Data issue. Details: HTTP Status %s, Message: %s"
                                              % (data_request.status_code, data_request.text))
                        except Exception as request_exception:
                            logging.error(request_exception)

                        if len(json_response) > 10:
                            time.sleep((int(self.config['baseinterval']) * (9 / len(json_response))))
                        else:
                            time.sleep(int(self.config['baseinterval']) / 2)
                elif task_request.status_code != requests.codes.ok:
                    logging.info("Task issue. Request returning incorrect status code. Turn on debugging for details")
                    logging.debug("Task issue. Details: HTTP Status %s, Message: %s"
                                  % (task_request.status_code, task_request.text))
                else:
                    logging.info("Task has no JSON content. Nothing to do. Waiting for %s seconds."
                                 % (int(self.config['baseinterval']) / 3))
                    time.sleep(int(self.config['baseinterval']) / 3)

                # Delete some stuff used in the loop and run the garbage collector
                for p in self.procs:
                    if not p.is_alive():
                        p.join()
                        p.terminate()
                        del p
                gc.collect()

                if self.config['cleanmem']:
                    # checking if clean memory option has been chosen during install then call the method to flush mem
                    self.mini_probe.clean_mem()
            sys.exit()

if __name__ == "__main__":
    probe = Probe()
    probe.main()
