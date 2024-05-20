import os

instancecounts = [1, 2, 3, 4, 5]
qoses          = [0, 1, 2]
delays         = [0, 1, 2, 4]


for instancecount in instancecounts:
    for qos in qoses:
        for delay in delays:
            directory_name = "instancecount-" + str(instancecount) + "-qos-"+str(qos)+"-delay-"+str(delay)
            os.mkdir(directory_name)


