# TiKV fail-slow testing

## Setup

1. Install TiUP: `curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh`
2. Run `tiup playground --pd 1 --kv 3 --without-monitor` to start a 1-node PD and 3-node TiKV cluster. (Find out each node's pid with `tiup playground display`)
3. Setup go-ycsb
    ```
    git clone https://github.com/pingcap/go-ycsb.git
    cd go-ycsb
    make
    ```
4. run `benchmark.xonsh` (comment out parts of main to run some tests seperately)
<!--
## References
* https://github.com/pingcap/tiup/blob/master/doc/user/overview.md
* 
* 
* 


* https://tikv.org/blog/double-system-read-throughput/

-->
## Result
See [Report](report.md).