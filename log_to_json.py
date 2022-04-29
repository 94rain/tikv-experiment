
   
import glob
import os
import json

read_map = {}
update_map = {}
ycsb_files = glob.glob("logs/*")
for ycsb_file in ycsb_files:
    file_name = os.path.basename(ycsb_file)
    tokens = file_name.split("_")
    thread_num = tokens[2]
    # print(tokens)
    # fault_type = tokens[-2] + "_" + tokens[-1]
    # print(fault_type)
    perf = {"thread": 0,"throughput": 0.0, "latency": 0.0}
    if tokens[0] == "baseline":
        fault_type = "baseline"
    if fault_type not in read_map:
        read_map[fault_type] = []
    if fault_type not in update_map:
        update_map[fault_type] = []
    for line in open(ycsb_file).readlines():
        # READ   - Takes(s): 0.3, Count: 10000, OPS: 28679.4, Avg(us): 372, Min(us): 72, Max(us): 32742, 99th(us): 2000, 99.9th(us): 4000, 99.99th(us): 33000
        if "READ   - " in line:
            throughput = float(line.split("Avg(us): ")[1].split(",")[0])
            latency = float(line.split("OPS: ")[1].split(",")[0])
            perf["throughput"] = throughput
            perf["latency"] = latency
            perf["thread"] = thread_num
            read_map[fault_type].append(perf)
        elif "UPDATE - " in line:
            throughput = float(line.split("Avg(us): ")[1].split(",")[0])
            latency = float(line.split("OPS: ")[1].split(",")[0])
            perf["throughput"] = throughput
            perf["latency"] = latency
            perf["thread"] = int(thread_num)
            update_map[fault_type].append(perf)


        # UPDATE - Takes(s): 0.9, Count: 9966, OPS: 10780.4, Avg(us): 2930, Min(us): 319, Max(us): 99317, 99th(us): 10000, 99.9th(us): 36000, 99.99th(us): 100000
        # elif "UPDATE - " in line:
        #     perf["latency"] = float(line.strip().split(" ")[-1])
        # elif "[UPDATE], AverageLatency(us)," in line:
        #     perf["latency"] = float(line.strip().split(" ")[-1])
print(read_map)
#     if fault_type not in map:
#         map[fault_type] = []
#     perf = {"throughput": 0.0, "read_latency": 0.0, "update_latency": 0.0}
#     for line in open(ycsb_file).readlines():
#         if "[OVERALL], Throughput(ops/sec)," in line:
#             perf["throughput"] = float(line.strip().split(" ")[-1])
#         elif "[READ], AverageLatency(us)," in line:
#             perf["read_latency"] = float(line.strip().split(" ")[-1])
#         elif "[UPDATE], AverageLatency(us)," in line:
#             perf["update_latency"] = float(line.strip().split(" ")[-1])
#     map[fault_type].append(perf)

for fault_type in update_map:
    update_map[fault_type] = sorted(update_map[fault_type], key=lambda i: i["thread"])
print(update_map)
json.dump(update_map, open("result.json", "w"), indent=4)

# for fault_type in map:
#     str = fault_type
#     for item in map[fault_type]:
#         str += "\t({},{})".format(int(item["throughput"]), int(item["update_latency"]))
#     print(str)