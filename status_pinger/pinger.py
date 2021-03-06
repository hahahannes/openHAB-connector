"""
   Copyright 2018 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

# /things mit ids aus device ppool status checken
import threading, time, configparser, os, logging
from api_manager import api_manager
from connector_client.modules import device_pool
from connector_client.client import Client
from logger.logger import root_logger


dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../config.ini')
config = configparser.ConfigParser()
config.read(filename)

logger = root_logger.getChild('pinger')

class Pinger(threading.Thread):
    def __init__(self):
        super().__init__()
        self.openhab_api_manager = api_manager.OpenhabAPIManager()
        self.platform_api_manager = api_manager.PlatformAPIManager()

    def run(self):
        while True:
            time.sleep(int(config["CONNECTOR"]["ping_interval"]))
            current_connected_devices = device_pool.DevicePool.devices().keys()
            if len(current_connected_devices) is not 0:
                for device_id in current_connected_devices:
                    self.ping(device_id)

    def ping(self, device_id):
        response = self.openhab_api_manager.get_thing(device_id)
        status = response.get("statusInfo")
        if status:
            if status.get("status") == "OFFLINE":
                Client.disconnect(device_id)
            elif status == "ONLINE":
                device = device_pool.DevicePool.get(device_id)
                Client.add(device)

