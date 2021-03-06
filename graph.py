import matplotlib.pyplot as plt
import json

map = json.load(open("result.json"))
# baseline

fault_types = [
    "nofault",
    "crash_follower",
    "crash_leader",
    "memcontention_follower_128",
    "memcontention_follower_160",
    "memcontention_follower_192",
    "memcontention_follower_224",
    "memcontention_follower_256",
    "memcontention_follower_512",
    "memcontention_leader_128",
    "memcontention_leader_160",
    "memcontention_leader_192",
    "memcontention_leader_224",
    "memcontention_leader_256",
    "memcontention_leader_512",
    "slowcpu_follower_50000",
    "slowcpu_follower_60000",
    "slowcpu_follower_70000",
    "slowcpu_follower_80000",
    "slowcpu_follower_90000",
    "slowcpu_follower_100000",
    "slowcpu_follower_200000",
    "slowcpu_leader_50000",
    "slowcpu_leader_60000",
    "slowcpu_leader_70000",
    "slowcpu_leader_80000",
    "slowcpu_leader_90000",
    "slowcpu_leader_100000",
    "slowcpu_leader_200000"
]

markers = ["v", "^", "8", "s", "p", "P", "*", "h", "X"]

def plot_baseline():
    perfs = map["baseline"]
    xs = []
    ys = []
    threads = []
    for perf in perfs:
        xs.append(perf["throughput"])
        ys.append(perf["latency"])
        threads.append(perf["thread"])
    plt.plot(xs, ys, marker=".", label="baseline")
    for x, y, thread in zip(xs, ys, threads):
        plt.annotate(thread, xy=(x, y))

    plt.xlabel("Throughput (ops/sec)\n Figure 1")
    plt.ylabel("Average Latency (us)")
    plt.title("Baseline performance for 1-32 threads (100K operations)")
    plt.savefig("assets/baseline.png")
    plt.clf()

initial_fault_plot = ["128", "256", "512", "50000", "100000", "200000", "crash"]

def plot_fault():
    plt.rcParams["figure.figsize"] = (16, 16)
    fig, axs = plt.subplots(3, 2)
    
    '''
    Four plots:
    leader all, baseline // follower all, baseline;
    cpu all, baseline   // memory all, baseline
    '''
    for i, fault in enumerate(fault_types):
        perfs = map[fault]
        x = []
        y = []
        for perf in perfs:
            x.append(perf["throughput"])
            y.append(perf["latency"])
        if fault == "nofault":
            for i in range(2):
                axs[0, i].plot(x, y, marker=".", linestyle="-", label="No fault")

        # if "leader" in fault and "crash" in fault:
        #     axs[0, 0].plot(x, y, marker=markers[i % 9], linestyle="-", label=fault)
        # if "follower" in fault and "crash" in fault:
        #     axs[0, 1].plot(x, y, marker=markers[i % 9], linestyle="-", label=fault)
        
        if "leader" in fault and any(num in fault for num in initial_fault_plot):
            axs[0, 0].plot(x, y, marker=markers[i % 9], linestyle="-", label=fault)
        if "follower" in fault and any(num in fault for num in initial_fault_plot):
            axs[0, 1].plot(x, y, marker=markers[i % 9], linestyle="-", label=fault)
        if "slowcpu" in fault and "leader" in fault:
            axs[1, 0].plot(x, y, marker=markers[i % 9], linestyle="-", label=fault)
        if "slowcpu" in fault and "follower" in fault:
            axs[1, 1].plot(x, y, marker=markers[i % 9], linestyle="-", label=fault)
        if "memcontention" in fault and "leader" in fault:
            axs[2, 0].plot(x, y, marker=markers[i % 9], linestyle="-", label=fault)
        if "memcontention" in fault and "follower" in fault:
            axs[2, 1].plot(x, y, marker=markers[i % 9], linestyle="-", label=fault)


    for i in range(3):
        for j in range(2):
            axs[i, j].set(xlabel="Throughput (ops/sec)", ylabel="Average Latency (us)")
            axs[i, j].legend()
    
    # axs[0, 0].get_figure().savefig('assets/leader.png')
    # axs[0, 1].get_figure().savefig('assets/follower.png')
    # axs[1, 0].get_figure().savefig('assets/cpu.png')
    # axs[1, 1].get_figure().savefig('assets/memory.png')
    axs[0, 0].set_title("Figure 2: leader faults")
    axs[0, 1].set_title("Figure 3: follower faults")
    axs[1, 0].set_title("Figure 4: slow CPU for leader")
    axs[1, 1].set_title("Figure 5: slow CPU for follower")
    axs[2, 0].set_title("Figure 6: memory contention for leader")
    axs[2, 1].set_title("Figure 7: memory contention for follower")

    # axs[0, 0].get_figure().savefig('assets/fault.png')
    axs[0, 0].get_figure().savefig('assets/crash.png')


if __name__ == "__main__":
    # plot_baseline()
    plot_fault()

