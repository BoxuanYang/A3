import paho.mqtt.client as mqtt
import sys
import time
import os
#-----------------------------------Global variables---------------------------------
host_name = "localhost"

analyser = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# a dictionary which stores the records of received messages, indexed by topic string
records = {}
#-----------------------------------Global variables---------------------------------

def on_publish(client, userdata, mid, reason_code, properties):
    return

def on_message(client, userdata, msg):
    topic = msg.topic
    content = msg.payload.decode('utf-8')
    timee = time.time()

    records[topic].append((content, timee))
    print(topic + ": " + content + ". Received time: " + str(timee))
    #print("Updated records:")
    #print(records)
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

def on_disconnect(client, userdata, rc, a, b):
    print("Disconnected")

"""
The analyser will be given 4 parameters: instancecount, publisher_qos, delay, publisher_qos.

The first 3 will be sent by the analyser to the publisher via a broker, while the last parameter, i.e.,
analyser_qos will be the qos level of the analyser to the broker.
"""

# first, parse the parameters to get the instacecount, qos and delay value
instancecount = int(sys.argv[1])
print("instance count: ", instancecount)

publisher_qos = int(sys.argv[2])
print("publisher_qos:  ", publisher_qos)

delay         = int(sys.argv[3])
print("delay:          ", delay)

analyser_qos  = int(sys.argv[4])
print("analyser_qos:   ", analyser_qos)

# setup the callback function
analyser.on_publish=on_publish
analyser.on_connect=on_connect
analyser.on_message=on_message
analyser.on_subscribe=on_subscribe
analyser.on_disconnect=on_disconnect
    
# connect to broker
analyser.connect(host_name, 1883, 60)

analyser.loop_start()

# First we subscribe to all topics
for i in range(1, instancecount + 1):
    topic = f"counter/{i}/{publisher_qos}/{delay}"
    print("subscribed to topic: ", topic)
    analyser.subscribe(topic, analyser_qos)

    if topic not in records:
        records[topic] = []

# then, publish to request/qos, request/delay and request/instancecount topics
analyser.publish("request/qos", publisher_qos, analyser_qos)
analyser.publish("request/delay", delay, analyser_qos)
analyser.publish("request/instancecount", instancecount, analyser_qos)



# then, listen to the specified counter topics on the broker and take measurements


analyser.loop_start()

time.sleep(15)

analyser.loop_stop()
analyser.disconnect()

directory = "instancecount-" + str(instancecount) + "-qos-"+str(publisher_qos)+"-delay-"+str(delay)

 
"""
Write the data we received to local file
"""
for topic in records:
    file_name = "counter-" + topic[8:9] + "-" + topic[10:11]+"-"+topic[12:13]+".txt"

    file_path = os.path.join(directory, file_name)
    print()
    print("Begin writing to: " + directory + "/" + file_name)
    print("Received " + str(len(records[topic])) + " in total")

    with open(file_path, 'w') as fp:
        for counter, timee in records[topic]:
            fp.write(str(counter) + "\t" + str(timee) + "\n")

print("Finish writing to: " + directory)  
exit()




    




