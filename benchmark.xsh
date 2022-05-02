import os
from datetime import datetime
import random
from time import sleep

threads = 26
node_num = 3
experiment_folder = "T4cm2Wk" # random generated string by tiup, check ~/.tiup/data/

def restart():
    tiup clean --all
    tiup playground --pd 1 --kv 3 --without-monitor
    sleep(10)

def get_pids():
    tiup playground display | grep tikv | awk '{print $1}' > pids.tmp
    with open("pids.tmp", "r") as f:
        pids = f.read().splitlines()
    return pids

def kill_pid(pids):
    for pid in pids:
        kill -9 @(pid)

def find_leader():
    last_leader_node = -1
    last_leader_port = -1
    last_leader_timestamp = datetime.strptime("2022/01/01 00:00:00.000", "%Y/%m/%d %H:%M:%S.%f") 

    for i in range(node_num):
        # make sure there is only one folder in ~/.tiup/data/ so * can work
        # tikv0, tikv1, tikv2
        log_path = "~/.tiup/data/{}/tikv-{}/tikv.log".format(experiment_folder, i)
        os.system(f"cat {log_path} | grep 'status-addr\|became leader at term' > leader{i}.tmp")
        with open(f"leader{i}.tmp", "r") as f:
            lines = f.readlines()
            if len(lines) > 0:
                last_line_split = lines[-1].split(" ")
                timestamp = datetime.strptime(last_line_split[0][1:] + " " + last_line_split[1], "%Y/%m/%d %H:%M:%S.%f")
                if timestamp > last_leader_timestamp:
                    last_leader_node = i
                    last_leader_port = lines[0].split("127.0.0.1:")[1].split("]")[0]
                    last_leader_timestamp = timestamp
    
    os.system(f"lsof -t -i:{last_leader_port} > leader_pid.tmp")
    with open("leader_pid.tmp", "r") as f:
        lines = f.read().splitlines()
        if len(lines) > 0 and int(lines[0]) > 0:
            return lines[0]
        else:
            return find_leader()

    # find pid by port
    
def slow_cpu(period, quota, pids):
    cgroup_name = "/sys/fs/cgroup/cpu/tikv"
    os.system("sudo cgcreate -g cpu:tikv -f 777")
    os.system("sudo echo {} > {}/cpu.cfs_quota_us".format(quota, cgroup_name))
    os.system("sudo echo {} > {}/cpu.cfs_period_us".format(period, cgroup_name))
    for pid in pids:
        os.system("echo {} > {}/cgroup.procs".format(pid, cgroup_name))

def memory_contention(quota, pids):
    cgroup_name = "/sys/fs/cgroup/memory/tikv"
    os.system("sudo cgcreate -g memory:tikv -f 777")
    os.system("sudo echo {} > {}/memory.limit_in_bytes".format(quota * 1024, cgroup_name))
    for pid in pids:
        os.system("sudo echo {} > {}/cgroup.procs".format(pid, cgroup_name))


def remove_fault_injection(fault_type):
    if fault_type == "cpu":
        os.system("sudo cgdelete cpu:tikv")
    elif fault_type == "memory":
        os.system("sudo cgdelete memory:tikv")

def run_baseline():
    for i in range(1, 33):
        os.system(f'./go-ycsb/bin/go-ycsb run tikv -P workload_mixed -p tikv.pd="127.0.0.1:2379" -p tikv.type="raw" -p threadcount={i} | tee logs/baseline_update_{i}')
    
def run_slow_cpu():
    period = 1000000
#    quotas = [50000, 100000, 200000]
    quotas = [i for i in range(90000, 40000, -10000)]

    # follower slow cpu
    for quota in quotas:
        # needs re-lookup leader pid every time
        leader_pid = find_leader()
        all_pids = get_pids()
        all_pids.remove(leader_pid)
        follower_pids = all_pids
        follower_pid_to_slow = follower_pids[random.randint(0, 1)]
        slow_cpu(period, quota, [follower_pid_to_slow])
        os.system(f'./go-ycsb/bin/go-ycsb run tikv -P workload_mixed -p tikv.pd="127.0.0.1:2379" -p tikv.type="raw" -p threadcount={threads} | tee logs/slowcpu_follower_{period}_{quota}')
        remove_fault_injection("cpu")
        sleep(10)

    # leader slow cpu
    for quota in quotas:
        # needs re-lookup leader pid every time
        leader_pid = find_leader()
        slow_cpu(period, quota, [leader_pid])
        os.system(f'./go-ycsb/bin/go-ycsb run tikv -P workload_mixed -p tikv.pd="127.0.0.1:2379" -p tikv.type="raw" -p threadcount={threads} | tee logs/slowcpu_leader_{period}_{quota}')
        remove_fault_injection("cpu")
        sleep(10)
    
def run_memory_contention():
    quotas = [i for i in range(512, 127, -32)]

    # follower memory contention
    for quota in quotas:
        # needs re-lookup leader pid every time
        leader_pid = find_leader()
        all_pids = get_pids()
        all_pids.remove(leader_pid)
        follower_pids = all_pids
        follower_pid_to_slow = follower_pids[random.randint(0, 1)]
        memory_contention(quota, [follower_pid_to_slow])
        os.system(f'timeout 1m ./go-ycsb/bin/go-ycsb run tikv -P workload_mixed -p tikv.pd="127.0.0.1:2379" -p tikv.type="raw" -p threadcount={threads} | tee logs/memcontention_follower_{quota}')
        remove_fault_injection("memory")
        sleep(10)

    # leader memory contention
    for quota in quotas:
        # needs re-lookup leader pid every time
        leader_pid = find_leader()
        memory_contention(quota, [leader_pid])
        os.system(f'timeout 1m ./go-ycsb/bin/go-ycsb run tikv -P workload_mixed -p tikv.pd="127.0.0.1:2379" -p tikv.type="raw" -p threadcount={threads} | tee logs/memcontention_leader_{quota}')
        remove_fault_injection("memory")
        sleep(10)

def run_crash_node():
    # kill follower
    leader_pid = find_leader()
    follower_pids = get_pids().remove(leader_pid)
    follower_pid_to_kill = follower_pids[random.randint(0, 1)]
    kill_pid([follower_pid_to_kill])
    os.system(f'timeout 1m ./go-ycsb/bin/go-ycsb run tikv -P workload_mixed -p tikv.pd="127.0.0.1:2379" -p tikv.type="raw" -p threadcount={threads} | tee logs/crash_follower')
    restart()
    # kill leader
    leader_pid = find_leader()
    kill_pid([leader_pid])
    os.system(f'timeout 1m ./go-ycsb/bin/go-ycsb run tikv -P workload_mixed -p tikv.pd="127.0.0.1:2379" -p tikv.type="raw" -p threadcount={threads} | tee logs/crash_leader')
    restart()


if __name__ == "__main__":
    # restart()
    ls ~/.tiup/data > log_path.tmp
    with open("log_path.tmp", "r") as f:
        experiment_folder = f.read().splitlines()[0]

    tikv_pids = get_pids()
#    # find_leader()
#    # run baseline
#    run_baseline()
#
#    # run crash node
#    run_crash_node()
#
#    # run slow cpu
#    remove_fault_injection("cpu")
#    #run_slow_cpu()
#

    remove_fault_injection("memory")
    run_memory_contention()

    rm *.tmp