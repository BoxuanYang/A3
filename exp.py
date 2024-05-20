import os

directory = "counter-5-2-4"
file_name = "hello.txt"
file_path = os.path.join(directory, file_name)


with open(file_path, 'w') as file:
    file.write("Hello world")
    