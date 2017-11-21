import requests 
import time 
import threading
from connector_client.connector import client
from connector_client.connector import device as device_file
from connector_client.modules import device_pool

# get data from openhab items -> channel id = rest api je funtkion => service url auf platform 

hab_ip = "127.0.0.1"
hab_port = 8080

class Monitor(threading.Thread):
    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip 
        self.port = port 

    def run(self):
        while True:
            time.sleep(10)
            unknown_devices = self.get_things()
            if unknown_devices:
                self._evaluate(unknown_devices)

    def _diff(self, known, unknown):
        known_set = set(known.keys())
        unknown_ids = list(map(lambda device: device.get("UID"), unknown))
        unknown_set = set(unknown_ids)
        missing = known_set - unknown_set
        new = unknown_set - known_set
        new = list(filter(lambda device: device.get("UID") in new, unknown))
        return missing, new

    def format(self,device, device_type):
        device_name = device.get("label")
        device_id = device.get("UID")
        return device_file.Device(device_id, device_type, device_name)

    def _evaluate(self, unknown_devices):        
        missing_devices, new_devices = self._diff(device_pool.DevicePool.devices(), unknown_devices)
        if missing_devices:
            for device in missing_devices:
                client.Client.delete(device)
        
        if new_devices:
            for device in new_devices:
                items = device.get("linkedItems")
                platform_services = []
                if items:
                    for item in items:
                        item = self.get_item(item) 
                        platform_services.append({
                            "name": item.get("label"),
                            "service_uri": item.get("link")
                        })
                
                # todo create device type automatically 
                # if type not already created

                device_type="iot#1a6572ed-f572-44df-be22-4ea844d6381b" 
                formatted_device = self.format(device, device_type)
                client.Client.add(formatted_device)

    def get_item(self,item):
        response = requests.get("http://{ip}:{port}/rest/items{item}".format(ip=self.ip, port=self.port,item=item))
        return response.json()
        
    def get_things(self):
        response = requests.get("http://{ip}:{port}/rest/things".format(ip=self.ip, port=self.port))
        return response.json()

if __name__ == "__main__":
    connector_client = client.Client(device_manager=device_pool.DevicePool) 
    monitor = Monitor(hab_ip, hab_port)
    monitor.start()