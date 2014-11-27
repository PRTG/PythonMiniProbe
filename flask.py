from flask import Flask
try:
    from PythonMiniProbe import probe
except:
    import probe

import requests
import json
import gc
import time
import sys

pyprtg = Flask(__name__)


@pyprtg.route('/')
def mini_probe_home():
    return 'Python Mini Probe Home'

if __name__ == '__main__':
        pyprtg.debug = True
        pyprtg.run(host='0.0.0.0', port=50000)

        # mini_probe = probe.Probe()
        # # Enable Garbage Collection
        # gc.enable()
        # # make sure the probe will not stop
        # probe_stop = False
        # # Create instance of Logger to provide logging
        # log = Logger()
        # # make sure probe is announced at every start
        # announce = False
        # # read configuration file (existence check done in probe_controller.py)
        # config = mini_probe.read_config('./probe.conf')
        # # create hash of probe access key
        # key_sha1 = mini_probe.hash_access_key(config['key'])
        # # get list of all sensors announced in __init__.py in package sensors
        # sensor_list = mini_probe.get_import_sensors()
        # sensor_announce = mini_probe.build_announce(sensor_list)
        # announce_json = json.dumps(sensor_announce)
        # url_announce = mini_probe.create_url(config, 'announce')
        # data_announce = mini_probe.create_parameters(config, announce_json, 'announce')
        #
        # while not announce:
        #     try:
        #         # announcing the probe and all sensors
        #         request_announce = requests.get(url_announce, params=data_announce, verify=False)
        #         announce = True
        #         log.log(True, None, config, "ANNOUNCE", None, None)
        #         if config['debug']:
        #             log.log_custom(config['server'])
        #             log.log_custom(config['port'])
        #             log.log_custom("Status Code: %s | Message: %s" % (request_announce.status_code, request_announce.text))
        #         request_announce.close()
        #     except Exception as e:
        #         log.log_custom(e)
        #         time.sleep(int(config['baseinterval']) / 2)
        #
        # while not probe_stop:
        #     # creating some objects only needed in loop
        #     url_task = mini_probe.create_url(config, 'tasks')
        #     task_data = {'gid':config['gid'], 'protocol':config['protocol'], 'key':key_sha1}
        #
        #     task = False
        #     while not task:
        #         json_payload_data = []
        #         try:
        #             request_task = requests.get(url_task, params=task_data, verify=False)
        #             json_response = request_task.json()
        #             request_task.close()
        #             gc.collect()
        #             task = True
        #             log.log(True, None, config, "TASK", None, None)
        #             if config['debug']:
        #                 log.log_custom(url_task)
        #         except Exception as e:
        #             log.log_custom(e)
        #             time.sleep(int(config['baseinterval']) / 2)
        #     gc.collect()
        #     if str(json_response) != '[]':
        #         json_response_chunks = [json_response[i:i+10] for i in range(0, len(json_response), 10)]
        #         for element in json_response_chunks:
        #             for part in element:
        #                 if config['debug']:
        #                     log.log_custom(part)
        #                 for sensor in sensor_list:
        #                     if part['kind'] == sensor.get_kind():
        #                         json_payload_data.append(sensor.get_data(part))
        #                     else:
        #                         pass
        #                 gc.collect()
        #             url_data = mini_probe.create_url(config, 'data')
        #             try:
        #                 request_data = requests.post(url_data, data=json.dumps(json_payload_data), verify=False)
        #                 log.log(True, None, config, "DATA", None, None)
        #
        #                 if config['debug']:
        #                     log.log_custom(json_payload_data)
        #                 request_data.close()
        #                 json_payload_data = []
        #             except Exception as e:
        #                 log.log_custom(e)
        #             if (len(json_response) > 10):
        #                 time.sleep((int(config['baseinterval']) * (9 / len(json_response))))
        #             else:
        #                 time.sleep(int(config['baseinterval']) / 2)
        #     else:
        #         log.log(True, "Nothing", config, None, None, None)
        #         time.sleep(int(config['baseinterval']) / 3)
        #
        #     # Delete some stuff used in the loop and run the garbage collector
        #     del json_response
        #     del json_payload_data
        #     gc.collect()
        #
        #     if config['cleanmem']:
        #         # checking if the clean memory option has been chosen during install then call the method to flush mem
        #         from utils import Utils
        #         Utils.clean_mem()
        # sys.exit()

