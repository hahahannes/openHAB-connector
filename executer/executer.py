import threading
from connector_client.connector import client
from api_manager import api_manager
import requests

class Executer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.openhab_api_manager = api_manager.OpenhabAPIManager()

    def run(self):
        while True:
            print("executer listens for commands")
            message = client.Client.receive()
            response = self.get_command(message)
            client.Client.response(message, response, metadata=None, timeout=10, callback=None, block=True)

    def get_command(self,message):
        print("Got command from platform")
        payload = message.payload 
        thing_id = payload.get('device_url')
        channel_type_uid = payload.get('service_url')
        linked_item_id = ""
        data = payload.get("protocol_parts")
        if data:
            data = data[0].get("value").strip()

        # GET /thing
        thing = self.openhab_api_manager.get_thing(thing_id)
        for channel in thing.get("channels"):
            # get the matching service instance of the device instance to the service type from the command 
            if channel.get("channelTypeUID") == channel_type_uid:
                # device instance has linked items (= active service instances running on this device instance)
                linked_item_id = channel.get("linkedItems")
                if linked_item_id:
                    linked_item_id = linked_item_id[0]
                    # GET /item and send command
                    item = self.openhab_api_manager.get_item(linked_item_id)
                    print("send data: " + data + "to device link: " + item.get("link"))
                    response = requests.post(item.get("link"),data=data)
                    return response.status_code
                    
        