import paho.mqtt.client as mqtt
import sys
import time
#-----------------------------------Global variables---------------------------------
host_name = "localhost"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# a dictionary which stores the records of received messages, indexed by topic string
records = {}

# a boolean value to indicate whether we have finished receiving from all topics
finish_receiving = False
#-----------------------------------Global variables---------------------------------
def on_publish(client, userdata, mid, reason_code, properties):
    # reason_code and properties will only be present in MQTTv5. It's always unset in MQTTv3
    print("Published : ", userdata)

def on_message(client, userdata, msg):
    topic = msg.topic
    content = msg.payload.decode('utf-8')
    timee = time.time()

    records[topic].append((content, timee))
    print(topic + ": " + content + ". Received time: " + str(timee))
    print("Updated records:")
    print(records)
    print()


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Successfully subscribed with the following QoS: {reason_code_list[0].value}")

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")

"""
The analyser will be given 4 parameters: instancecount, publisher_qos, delay, publisher_qos.

The first 3 will be sent by the analyser to the publisher via a broker, while the last parameter, i.e.,
analyser_qos will be the qos level of the analyser to the broker.
"""

# first, parse the parameters to get the instacecount, qos and delay value
instancecount = int(sys.argv[1])
print("instance count: ", instancecount)

publisher_qos = int(sys.argv[2])
print("publisher_qos: ", publisher_qos)

delay         = int(sys.argv[3])
print("delay: ", delay)

analyser_qos  = int(sys.argv[4])
print("analyser_qos: ", analyser_qos)

# setup the callback function
client.on_publish=on_publish
client.on_connect=on_connect
client.on_message=on_message
client.on_subscribe=on_subscribe
    
# connect to broker
client.connect(host_name, 1883, 60)

client.loop_start()

# First we subscribe to all topics
for i in range(1, instancecount + 1):
    topic = f"counter/{i}/{publisher_qos}/{delay}"
    print("subscrived to topic: ", topic)
    client.subscribe(topic)

    if topic not in records:
        records[topic] = []

# then, publish to request/qos, request/delay and request/instancecount topics
client.publish("request/qos", publisher_qos, analyser_qos)
client.publish("request/delay", delay, analyser_qos)
client.publish("request/instancecount", instancecount, analyser_qos)



# then, listen to the specified counter topics on the broker and take measurements

    

client.loop_start()

time.sleep(70)

    

    




