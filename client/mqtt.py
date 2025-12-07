import paho.mqtt.client as mqtt

IP_ADDRESS = "192.168.0.7"
PORT = 1883

def on_message(client, userdata, msg):
    print(msg.topic, msg.payload.decode())

client = mqtt.Client()
client.on_message = on_message

client.connect(IP_ADDRESS, PORT)
client.subscribe("CEMPU/dev1")

client.loop_start()

client.publish("CEMPU/dev1", "hehe", qos=1)

while True:
    pass