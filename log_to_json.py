
   
from collections import defaultdict
import glob
import os
import json

read_map = defaultdict(list)
update_map = defaultdict(list)
ycsb_files = glob.glob("logs/*")
final_thread_num = 26
for ycsb_file in ycsb_files:
    file_name = os.path.basename(ycsb_file)
    tokens = file_name.split("_")
    perf = {"throughput": 0.0, "latency": 0.0}
    if tokens[0] in ["baseline"]:
        fault_type = tokens[0]
        thread_num = tokens[2]
    elif tokens[0] in ["slowcpu"]:
        fault_type = f"{tokens[0]}_{tokens[1]}_{tokens[3]}"
    elif tokens[0] in ["memcontention"]:
        fault_type = f"{tokens[0]}_{tokens[1]}_{tokens[2]}"
    elif tokens[0] in ["crash"]:
        fault_type = f"{tokens[0]}_{tokens[1]}"
    else:
        fault_type = "nofault"
    for line in open(ycsb_file).readlines():
        if "READ   - " in line:
            latency = float(line.split("Avg(us): ")[1].split(",")[0])
            throughput = float(line.split("OPS: ")[1].split(",")[0])
            if fault_type == 'baseline':
                perf["thread"] = int(thread_num)
            perf["throughput"] = throughput
            perf["latency"] = latency
            read_map[fault_type].append(perf.copy())
        elif "UPDATE - " in line:
            latency = float(line.split("Avg(us): ")[1].split(",")[0])
            throughput = float(line.split("OPS: ")[1].split(",")[0])
            perf["throughput"] = throughput
            perf["latency"] = latency
            if fault_type == 'baseline':
                perf["thread"] = int(thread_num)
                continue # only the last line for baseline
            update_map[fault_type].append(perf.copy())
    if len(update_map[fault_type]) == 0 and fault_type != "baseline":
        update_map[fault_type].append(perf)
    if fault_type == 'baseline':
        update_map[fault_type].append(perf.copy())
print(read_map)

for fault_type in update_map:
    if fault_type == 'baseline':
        update_map[fault_type] = sorted(update_map[fault_type], key=lambda i: i["thread"])

json.dump(update_map, open("result.json", "w"), indent=4)
