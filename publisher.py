import paho.mqtt.client as mqtt
import json
import time
import threading

host_name = "localhost"
port = 1883

class Publisher:
    def __init__(self, instance_id):
        # instantiate publisher client
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,f"Publisher_{instance_id}")

        # setup callback functions
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        # initialize the instance_id
        self.instance_id = instance_id
        # settings is used to identify which topic to send to, initialized with None
        self.settings = {'qos': None, 'delay': None, 'instancecount': None}
        
    # once connected, subscribe to all settings topics
    def on_connect(self, client, userdata, flags, rc):
        print(f"Publisher {self.instance_id} connected with result code {rc}")
        self.client.subscribe("request/qos", qos=0)
        self.client.subscribe("request/delay", qos=0)
        self.client.subscribe("request/instancecount", qos=0)
        print("Subscribed to control topics")
    
    # check whether all settings are set
    def all_settings_set(self):

        for key in self.settings:
            if self.settings[key] == None:
                return False
        return True
    
    # Each time we receive a setting parameter from "request/qos", 
    # "request/delay" and "request/instancecount", we check whether
    # the settings has been all set and publish if all set and 
    # instanceid < instancecount
    def on_message(self, client, userdata, msg):
        data = json.loads(msg.payload)
        new_test_id = data.get('test_id', -1)
        
        if msg.topic == "request/qos":
            self.settings['qos'] = data['qos']
            print(f"Publisher {self.instance_id} received new QoS setting: {self.settings['qos']}")
            if self.all_settings_set() == True and self.instance_id <= self.settings['instancecount']:
                self.publish_messages()
                return

        elif msg.topic == "request/delay":
            self.settings['delay'] = data['delay']
            print(f"Publisher {self.instance_id} received new delay setting: {self.settings['delay']} ms")
            if self.all_settings_set() == True and self.instance_id <= self.settings['instancecount']:
                self.publish_messages()
                return

        elif msg.topic == "request/instancecount":
            self.settings['instancecount'] = data['instancecount']
            print(f"Publisher {self.instance_id} received new instance count: {self.settings['instancecount']}")
            if self.all_settings_set() == True and self.instance_id <= self.settings['instancecount']:
                self.publish_messages()
                return


    def publish_messages(self):
        start_time = time.time()
        counter = 0

        while (time.time() - start_time < 2):
            topic = f"counter/{self.instance_id}/{self.settings['qos']}/{self.settings['delay']}"
            self.client.publish(topic, str(counter), qos=self.settings['qos'])
            print(f"Publisher {self.instance_id} sent message {counter} to {topic}")
            counter += 1
            
            time.sleep(self.settings['delay'] / 1000.0)
        
        # set all settings to None after sending finish
        for key in self.settings:
            self.settings[key] = None
        return

    def on_disconnect(self, client, userdata, rc):
        print(f"Publisher {self.instance_id} disconnected with result code {rc}")

    def mainn(self):
        self.client.connect(host_name, port, 60)
        self.client.loop_forever()

# 启动5个发布者实例
if __name__ == "__main__":
    for i in range(1, 6):
        publisher = Publisher(i)
        thread = threading.Thread(target=publisher.mainn)
        thread.start()
