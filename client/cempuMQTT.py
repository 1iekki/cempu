import paho.mqtt.client as mqtt

IP_ADDRESS = "192.168.0.7"
PORT = 1883
LIST_OF_TOPICS = ["CEMPU/{}/command"]
ENGAGEMENT_TOPIC = "CEMPU/{}/engagement"

def on_message(client, userdata, msg):
    print(msg.topic, msg.payload.decode())

class CempuMQTT:

    client: mqtt.Client
    deviceID: str

    def __init__(self, deviceID: str):
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