import paho.mqtt.client as mqtt
import sys
import time
#-----------------------------------Global variables---------------------------------
host_name = "localhost"

# the id of the publisher, specified by the command line argument
instance_id = -1

# the number of publishers that should be active, specified by analyser
instance_count = int(sys.argv[1])

# the qos level from 0 to 2
qos = 0

# the delay level
delay = 0

# the dictionary which stores the qos and delay level of the publisher
# specified by the broker
settings = {"request/qos": None, "request/delay": None, "request/instancecount": None}

# the publisher MQTT client
publisher = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

#-----------------------------------Global variables---------------------------------
def on_publish(client, userdata, mid, reason_code, properties):
    # reason_code and properties will only be present in MQTTv5. It's always unset in MQTTv3
    # print("Published: ", userdata)
    return

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")
    
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')

    print("Received topic: " + msg.topic + ": " + payload)

    if topic == "request/instancecount":
        global instance_count
        instance_count= int(payload)

        settings["request/instancecount"] = instance_count
        check_and_publish_all_messages()
    
    elif topic == "request/qos":
        global qos 
        qos = int(payload)

        settings[topic] = payload
        check_and_publish_all_messages()
    elif topic == "request/delay":
        global delay 
        delay = int(payload)
        
        settings[topic] = payload
        check_and_publish_all_messages()

    return


def check_and_publish_all_messages():
    """
    Perform a check, if 
    """
    if all(value is not None for value in settings.values()):
        publish_all_messages(settings)
        # 处理完之后清空消息
        for key in settings:
            settings[key] = None
    return

def publish_all_messages(messages):
    # keep publishing the counter for 1 minute, if the
    # instance_id <= 
    if instance_id > instance_count:
        return

    print("Publishing all mesages for publisher-" + str(instance_id))
    counter = 0

    topic = f"counter/{instance_id}/{qos}/{delay}"

    start = time.time()

    
    print("Should publish to:", topic)
    

    while time.time() - start < 20:
        print("publish " + str(counter) + " from publisher-" + str(instance_id))
        publisher.publish(topic, counter, qos)
        counter += 1
        time.sleep(delay)
    
    print()
    print("------------------------------------------------")
    print("Finished sending for publisher-" + str(instance_id) + ". Sent " + str(counter) + " in total.")
    print("------------------------------------------------")
    print()

    for key in settings:
        settings[key] = None

    
    
    

    return
    

instance_id = int(sys.argv[1])
print("instance_id: ", instance_id)
    
# setup the callback functions
publisher.on_connect=on_connect
publisher.on_publish=on_publish
publisher.on_subscribe=on_subscribe
publisher.on_message=on_message

# connect to the broker
publisher.connect(host_name, 1883, 60)
    
publisher.loop_start()
    
# The publisher first subscribe to the following topics
publisher.subscribe("request/qos")
publisher.subscribe("request/delay")
publisher.subscribe("request/instancecount")

print("Waiting for parameters...")

publisher.loop_forever()









