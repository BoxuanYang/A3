import os
import paho.mqtt.client as mqtt
import time
import json
import statistics
from collections import defaultdict
import pandas as pd
#--------------------------------Global variables---------------------------------
broker_address = "localhost"
port = 1883
analyser = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,"Analyser")

records = {}
test_results_summary = []  # 用于存储测试结果的总结信息
current_test_id = 1
#--------------------------------Global variables---------------------------------
def on_connect(client, userdata, flags, rc):
    print("Analyser connected with result code " + str(rc))
    return

def on_message(client, userdata, msg):
    receive_time = time.time()

    global current_test_id
    topic = msg.topic
    payload = msg.payload.decode()
    message = int(payload)

    instance_id   = int(topic[8:9])
    publisher_qos = int(topic[10:11])
    delay         = int(topic[12:])

    analyser_qos  = int(client._userdata['analyser_qos'])
    key = (analyser_qos, publisher_qos, delay, instance_id)
    if current_test_id not in records:
        records[current_test_id] = defaultdict(lambda: {
            "messages": [],
            "times": []
        })
    
    records[current_test_id][key]["messages"].append(message)
    records[current_test_id][key]["times"].append(receive_time)
    return



def analyze_data(test_id, analyser_qos):
    if test_id not in records:
        print(f"No data found for test_id {test_id}")
        return
    
    for key, data in records[test_id].items():
        analyser_qos, publisher_qos, delay, count = key
        messages = data["messages"]
        times = data["times"]
        if not messages:
            continue
        
        # Collect statistics for average message rate
        total_messages_received = len(messages)
        total_duration = 60
        average_message_rate = total_messages_received / total_duration
        
        # Collect statistics for message loss rate
        expected_messages = total_duration * 1000
        if delay > 0:
            expected_messages = total_duration * 1000 / delay

        expected_messages = max(expected_messages, total_messages_received)  # 确保 expected_count 至少为 total_messages_received

        if expected_messages > 0:
            message_loss_rate = (1 - total_messages_received / expected_messages) * 100 
        else:
            message_loss_rate = 0

        # Collect statistics for out of order rate
        out_of_order = 0
        for i in range(1, len(messages)):
            if messages[i - 1] > messages[i]:
                out_of_order += 1
        
        out_of_order_rate = 0
        if total_messages_received > 0:
            out_of_order_rate = (out_of_order / total_messages_received) * 100
        
        
        # collect statistics for median gap       
        gaps = [times[i] - times[i - 1] for i in range(1, len(messages))]
        if gaps != []: 
            # the time we measures is in s, need to convert it to ms
            median_gap = statistics.median(gaps) * 1000
        else:
            median_gap = 0

        
        # save results to records
        records[test_id][key].update({
            "total_messages_received": total_messages_received,
            "average_message_rate": average_message_rate,
            "message_loss_rate": message_loss_rate,
            "out_of_order_rate": out_of_order_rate,
            "median_gap": median_gap
        })

        # 将测试结果添加到总结信息中
        test_results_summary.append({
            "test_id": test_id,
            "qos_levels_analyser": analyser_qos,
            "qos_levels_publisher": publisher_qos,
            "delays": delay,
            "instance_counts": count,
            "total_messages_received": total_messages_received,
            "average_message_rate": average_message_rate,
            "message_loss_rate": message_loss_rate,
            "out_of_order_rate": out_of_order_rate,
            "median_gap": median_gap
        })
        
        

    # save to csv
    save_as_csv()

def save_as_csv():
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    file_path = os.path.join(desktop_path, 'results.csv')

    df = pd.DataFrame(test_results_summary)
    df.to_csv(file_path, index=False)
    print(f"Test results saved to '{file_path}'")

# 发布新的控制指令
def send_control_commands():
    global delays, current_test_id
    qos_levels_analyser = [0, 1, 2]
    qos_levels_publisher = [0, 1, 2]
    delays = [0, 1, 2, 4]
    instance_counts = [1, 2, 3, 4, 5]
    
    for analyser_qos in qos_levels_analyser:
        for publisher_qos in qos_levels_publisher:
            for delay in delays:
                for count in instance_counts:
                    key = (analyser_qos, publisher_qos, delay, count)
                    control_info_qos = json.dumps({'qos': publisher_qos, 'test_id': current_test_id})
                    control_info_delay = json.dumps({'delay': delay, 'test_id': current_test_id})
                    control_info_instance = json.dumps({'instancecount': count, 'test_id': current_test_id})
                    
                    analyser.user_data_set({'analyser_qos': analyser_qos})  # 设置 analyser_qos 到用户数据中
                    analyser.publish("request/qos", control_info_qos, 2)  # 发送单独的QoS控制信息
                    analyser.publish("request/delay", control_info_delay, 2)  # 发送单独的延迟控制信息
                    analyser.publish("request/instancecount", control_info_instance, 2)  # 发送单独的实例数量控制信息
                    print(f"Sent publisher parameters with analyser QoS: {analyser_qos}, publisher QoS: {publisher_qos}, delay: {delay}, instancecount: {count}")
                    
                    # Subscribe to all topics
                    for i in range(1, count + 1):
                        topic = f"counter/{i}/{publisher_qos}/{delay}"
                        analyser.subscribe(topic, analyser_qos)
                        print(f"Subscribed to topic {topic} with QoS {analyser_qos}")
                    
                    time.sleep(3)  # 等待60秒接收数据
                    
                    # 当一分钟过去后停止订阅之前的counter主题，不再接收和存储迟到的数据
                    for i in range(1, count + 1):
                        topic = f"counter/{i}/{publisher_qos}/{delay}"
                        analyser.unsubscribe(topic)
                        print(f"Unsubscribed from topic {topic}")
                    
                    analyze_data(current_test_id, analyser_qos)  # 分析上一轮存储好的数据
                    current_test_id += 1  # 测试序号加一，准备进入下一轮测试
                    print(f"current_test_id = {current_test_id}, finished current test and begins next")


# setup callback functions
analyser.on_connect = on_connect
analyser.on_message = on_message

analyser.connect(broker_address, port)
analyser.loop_start()


send_control_commands()
exit()
#analyser.loop_stop()
#analyser.disconnect()
