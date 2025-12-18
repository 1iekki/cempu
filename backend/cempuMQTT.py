import asyncio
import logging
import paho.mqtt.client as mqtt

from connectionManager import ConnectionManager

IP_ADDRESS = "127.0.0.1"
PORT = 1883

ENGAGEMENT_TOPIC = "CEMPU/+/engagement"
COMMAND_TOPIC = "CEMPU/{}/command"

LIST_OF_TOPICS = [ENGAGEMENT_TOPIC]

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

def on_message(client, userdata, msg):
    # 1. Unpack the tuple you passed in __init__
    queue, loop = userdata
    
    # 2. Decode the message
    payload = msg.payload.decode()
    
    # 3. Thread-Safety Magic:
    # Tell the main loop: "Please run queue.put_nowait(payload) ASAP"
    loop.call_soon_threadsafe(queue.put_nowait, payload)

class CempuMQTT:
    client: mqtt.Client
    deviceID: str

    def __init__(self, deviceID: str, queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        self.client = mqtt.Client(userdata=(queue, loop))
        self.client.on_message = on_message
        self.deviceID = deviceID


    def __enter__(self):
        self.client.connect(IP_ADDRESS, PORT)
        self.SubscribeToTopics(LIST_OF_TOPICS)
        self.client.loop_start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.loop_stop()
        self.client.disconnect()


    def SubscribeToTopics(self, listOfTopics: list[str]) -> None:
        for topic in listOfTopics:
            topic = topic.format(self.deviceID)
            self.client.subscribe(topic)    
        
    def sendEngagement(self, engagement: float) -> None:
        topic = ENGAGEMENT_TOPIC.format(self.deviceID)
        self.client.publish(topic, engagement, qos=1)

    def sendCommand(self, command: int, deviceID: str) -> None:
        topic = ENGAGEMENT_TOPIC.format(deviceID)
        self.client.publish(topic, command, qos=1)