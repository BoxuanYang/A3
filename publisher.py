import paho.mqtt.client as mqtt
import sys
import time
#-----------------------------------Global variables---------------------------------
host_name = "localhost"

# the id of the publisher, specified by the command line argument
instance_id = None

# the dictionary which stores the qos and delay level of the publisher
# specified by the broker
settings = {"request/qos": None, "request/delay": None, "request/instancecount": None}

# the publisher MQTT client
publisher = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

finish_send = False

#-----------------------------------Global variables---------------------------------
def on_publish(client, userdata, mid, reason_code, properties):
    # reason_code and properties will only be present in MQTTv5. It's always unset in MQTTv3
    print("Published: ", userdata)
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
    return

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')

    print("Received topic: " + msg.topic + ". Payload: " + payload)

    if topic == "request/instancecount":
        settings[topic] = int(payload)
        check_and_publish_all_messages()
    
    elif topic == "request/qos":
        settings[topic] = int(payload)
        check_and_publish_all_messages()

    elif topic == "request/delay":
        settings[topic] = int(payload)
        check_and_publish_all_messages()

    return

def on_disconnect(client, userdata, rc, a, b):
    return




def check_and_publish_all_messages():
    """
    Perform a check, if 
    """
    all_settings_set = True
    for setting in settings:
        if settings[setting] == None:
            all_settings_set = False
            break


    if all_settings_set == True:
        publish_all_messages(settings)
        

    return

def publish_all_messages(messages):
    # keep publishing the counter for 1 minute, if the
    # instance_id <= 
    if instance_id > settings["request/instancecount"]:
        return
    

    qos            = settings["request/qos"]
    delay          = settings["request/delay"]
    instance_count = settings["request/instancecount"]
    
    

    print("Publishing all mesages for publisher-" + str(instance_id)
          + " with qos:" + str(qos)
          + ", delay: " + str(delay)
          + " instancount: " + str(instance_count))
    
    counter = 0
    topic = f"counter/{instance_id}/{qos}/{delay}"
    start = time.time()
  
    print("Should publish to:", topic)
    
    while time.time() - start < 10:
        
        ret = publisher.publish(topic, counter, qos)
        print("publish " + str(counter) + " from publisher-" + str(instance_id) + " to topic: " + topic)
        #print(ret)
        counter += 1
        time.sleep(delay / 1000)
    
    print()
    print("------------------------------------------------")
    print("Finished sending for publisher-" + str(instance_id) + ". Published " + str(counter) + " to topic: " + topic + " in total.")
    
    print()

    for key in settings:
        settings[key] = None

    print("Setting from publisher-" + str(instance_id))
    print(settings)
    print("------------------------------------------------")

    global finish_send
    finish_send = True
    
    

    return
    

instance_id = int(sys.argv[1])
print("instance_id: ", instance_id)
    
# setup the callback functions
publisher.on_connect=on_connect
publisher.on_publish=on_publish
publisher.on_subscribe=on_subscribe
publisher.on_message=on_message
publisher.on_disconnect=on_disconnect

# connect to the broker
publisher.connect(host_name, 1883, 60)
    
publisher.loop_start()
    
# The publisher first subscribe to the following topics
publisher.subscribe("request/qos", 2)
publisher.subscribe("request/delay", 2)
publisher.subscribe("request/instancecount", 2)

print("Waiting for parameters...")


publisher.loop_forever()








