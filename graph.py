import matplotlib.pyplot as plt
import json

map = json.load(open("result.json"))
# plt.rcParams["figure.figsize"] = (12, 12)
for i, to_plot in enumerate(["baseline", "slowcpu", "memcontention"]):
    perfs = map[to_plot]
    xs = []
    ys = []
    threads = []
    for perf in perfs:
        xs.append(perf["throughput"])
        ys.append(perf["latency"])
        threads.append(perf["thread"])
    if i == 0:
        plt.plot(xs, ys, marker=".", label=to_plot)
        for x, y, thread in zip(xs, ys, threads):
            plt.annotate(thread, xy=(x, y))

plt.xlabel="Throughput (ops/sec)"
plt.ylabel="Average Latency (us)"

plt.savefig("assets/baseline.png")