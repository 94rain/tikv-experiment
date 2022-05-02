<h3 align="center"> Assignment #2: Testing Reliability of Quorum Systems</h1>
<center>Shuyang Ji (sji15)</center>
#### 1. Select a Quorum System

**Q1: What is your quorum system of choice?**

<span style="color: green">TiKV, a distrbuted key-value stroage that relies on the Multi-Raft provided by Raftstore for data replicating and strong consistency, and RocksDB for persistence. </span>



#### **2. Run The Quorum System and Measure The Baseline Performance**

**Q2: Please describe your configuration.**
<span style="color: green">The experiments are run on a Ubuntu VM within MacOS with 8 cores CPU (M1 ARM) and 8 GB of memory.</span>

<span style="color: green">I use go-ycsb (the Golang port of YCSB) as the client to measure performance.</span>

**Q3: What is your client workload?**

<span style="color: green">I use a client workload of 10000 record count, 100000 operation count, 0.5/0.5 read/update proportion.</span> 

<span style="color: green">Based on the experiment results of 1-29 threads (see Q4), 26 hits the max throughput.</span> 

<span style="color: green">I conclude the bottleneck is the CPU as it exceeded the 100% CPU utilization.</span> 

**Q4: What is your baseline performance? Plot the throughput-latency figure (how does such a paper look like? the x-axis is the throughput and the y-axis is the latency, see Figure 7 in** [**this paper**](https://www.usenix.org/system/files/osdi20-ngo.pdf)).

![](assets/baseline.png)

<div style="page-break-after: always;"></div>

#### **3. Fail-Injection Testing**

**Q5: How do you simulate crash, slow CPU and memory contention?**

<span style="color: green"><b>Crash:</b> By killing the process of targeted node</span> 

<span style="color: green"><b>Slow CPU:</b> By configuring cgroups (`cpu.cfs_quota_us` and `cpu.cfs_period_us`) to limit CPU usage of the process of targeted node in a given amount of time.</span> 

<span style="color: green">Initially, I limited a node to use CPU for 0.05, 0.1 and 0.2 seconds out of every 1 second.</span>

<span style="color: green"><b>Memory contention:</b> By configuring cgroups to limit memory usage of the process of targeted node</span> 

<span style="color: green">Initially, I limited a node to use 128/256/512 MB memory.</span>

![](assets/fault.png)

**Q6: Please plot the performance with faults on the** **leader** **node and compare it with the baseline performance.**



Killing the leader node will only slightly affect the operations. This is consistent with Raft and TiKV's fault tolerance design.



**Q7: Please explain the above results. Is it expected? Why or why not?**

When I choose the quota 50000, 



**Q8: Please plot the performance with faults on the** **follower** **node and compare it with the baseline performance.**



**Q9: Please explain the above results. Is it expected? Why or why not?**

Killing the follower node will only slightly affect the operations. This is consistent with Raft and TiKV's fault tolerance design.

**Q10: For the slow CPU and memory contention, could you vary the level of slowness/contention and report the results?**

I observe that when a follower is limited by a memory contention of 128MB, the node will not be able to operate normally (causing `mark store's regions need be refill` exception) and the throughoutput will decrease. I picked 160, 192 and 224 MB as memory quotas for further testing.

I found the result can be a bit flaky. In one run, 160MB memory limit of a follower will not affect update operations. However, 192 MB will cause `mark store's regions need be refill` exception and result in very low throughoutput and long latency.


#### References
* https://github.com/pingcap/tiup/blob/master/doc/user/overview.md
* https://github.com/pingcap/go-ycsb
* https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/resource_management_guide/sec-cpu
* https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/resource_management_guide/sec-memory
