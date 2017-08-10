# Genomic Search

The heart of this project deals with searching genomics databases.  Primary focus is on DNA searches, but in reality, if the code is properly abstracted, any type of search can be done (RNA, Protein, etc) as these are not fundamentally different.  There are several different tools and algorithms that do matching and will provide a match score between the query string and the closest matching entries in the database.  We will focus on an older algorithm called BLAST (Basic Local Alignment Search Tool).

Distributed approaches will likely not out-perform a search on a multi-core machine where the entire search database can be stored in memory.  As the databases get larger, it will become more expensive to requisition high memory machines, this is where a distributed approach will shine.  Current the NCBI RefSeq contains about 60k genomes which can fit in under 300GB of memory.  Half-terabyte and 1-terabyte systems should outperform distributed systems for the foreseeable future.  As the search database grows beyond the capacity of high memory machines, or searches become massively parallel, then these approaches should win out.

# Approach

We leverage the existing BLAST library, distributing computation using spark. There are two steps necessary to run a query. First, the reference query set must be pre-processed and loaded into an object store. While it comes with increased network overhead, we use an object store to store data cheaply and persistently, allowing us to use the same pre-processed data set across multiple queries from multiple clusters. In this case, we use IBMs block store. Second, the actual computation search must run

We use a similar approach for both steps. In each case, a bash helper script invokes a pyspark script on the driver. The driver distributes blast requests to the worker node via a second helper shell script. The responses are collected and sorted to find the best match

# Requirements

## Packages
- Swift (python-swiftclient)
- Blast (TODO -- how to install blast)
## Cluster
This project assumes a functional spark cluster, similar to the set up in HW6

## Environment Setup

The following environment variables must be defined
```
export ST_USER="SLOS1..."
export ST_KEY="748fea..."
export ST_AUTH="https://sjc01.objectstorage.softlayer.net/auth/v1.0"
export ST_AUTH="https://sjc01.objectstorage.service.networklayer.com/auth/v1.0"
```

# Running
## Step 0 -- setup

Fill in the appropriate information in `setup.bash`, then 
```
source setup.bash
```

## Step 1 -- Creating the db

```
./run_blastdb.bash
```


This invokes `spark_blastdb.py`, which in turn invokes `spark_blastdb.bash` across the worker nodes

## Step 2 -- Querying the db

```
./run_blast.bash
```

This invokes `spark_blast.py`, which in turn invokes `spark_blast.bash` across the worker nodes
