<h3 align="center"> Assignment #2: Testing Reliability of Quorum Systems</h1>
<center>Shuyang Ji (sji15)</center>


#### 1. Select a Quorum System

**Q1: What is your quorum system of choice?**

<span style="color: green">TiKV, a distrbuted key-value stroage that relies on the Multi-Raft provided by Raftstore for data replicating and strong consistency, and RocksDB for persistence. </span>



#### **2. Run The Quorum System and Measure The Baseline Performance**

**Q2: Please describe your configuration.**
<span style="color: green">The experiments are run on a machine with 4 cores and 8 GB of memory.</span>

<span style="color: green">I use go-ycsb (the Golang port of YCSB) as the client to measure performance.</span>



**Q3: What is your client workload?**

<span style="color: green">I use a client workload of 10000 record count, 100000 operation count, 0.5/0.5 read/update proportion.</span> 

<span style="color: green">Based on the experiment results of 1-29 threads (see Q4), 26 hits the max throughput.</span> 

<span style="color: green">We conclude the bottleneck is the CPU as it exceeded the 100% CPU utilization.</span> 



**Q4: What is your baseline performance? Plot the throughput-latency figure (how does such a paper look like? the x-axis is the throughput and the y-axis is the latency, see Figure 7 in** [**this paper**](https://www.usenix.org/system/files/osdi20-ngo.pdf)).**

![](assets/baseline.png)

<div style="page-break-after: always;"></div>

#### **3. Fail-Injection Testing**

**Q5: How do you simulate crash, slow CPU and memory contention?**

<span style="color: green"><b>Crash:</b> By killing the process of targeted node</span> 

<span style="color: green"><b>Slow CPU:</b> By configuring cgroups to limit CPU usage of the process of targeted node</span> 

<span style="color: green"><b>Memory contention:</b> By configuring cgroups to limit memory usage of the process of targeted node</span> 



**Q6: Please plot the performance with faults on the** **leader** **node and compare it with the baseline performance.**

![](assets/leader.png)



**Q7: Please explain the above results. Is it expected? Why or why not?**

When I choose the quota 50000, 



**Q8: Please plot the performance with faults on the** **follower** **node and compare it with the baseline performance.**

![](assets/follower.png)

**Q9: Please explain the above results. Is it expected? Why or why not?**



**Q10: For the slow CPU and memory contention, could you vary the level of slowness/contention and report the results?**
