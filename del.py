import os
import shutil

def delete_instance_directories(path='.'):
    # 获取指定路径下的所有文件和目录
    for item in os.listdir(path):
        # 构建完整路径
        item_path = os.path.join(path, item)
        # 检查是否为目录且目录名以 "instance" 开头
        if os.path.isdir(item_path) and item.startswith("instance"):
            try:
                # 删除目录及其内容
                shutil.rmtree(item_path)
                print(f"Deleted directory: {item_path}")
            except Exception as e:
                print(f"Error deleting directory {item_path}: {e}")

# 调用函数删除当前目录下的 "instance" 目录
delete_instance_directories()