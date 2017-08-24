# Genomic Search

The heart of this project deals with searching genomics databases.  Primary focus is on DNA searches, but in reality, if the code is properly abstracted, any type of search can be done (RNA, Protein, etc) as these are not fundamentally different.  There are several different tools and algorithms that do matching and will provide a match score between the query string and the closest matching entries in the database.  We will focus on an older algorithm called BLAST (Basic Local Alignment Search Tool).

Distributed approaches will likely not out-perform a search on a multi-core machine where the entire search database can be stored in memory.  As the databases get larger, it will become more expensive to requisition high memory machines, this is where a distributed approach will shine.  Current the NCBI RefSeq contains about 60k genomes which can fit in under 300GB of memory.  Half-terabyte and 1-terabyte systems should outperform distributed systems for the foreseeable future.  As the search database grows beyond the capacity of high memory machines, or searches become massively parallel, then these approaches should win out.

# Approach

We leverage the existing BLAST library, distributing computation using spark. There are two steps necessary to run a query. First, the reference query set must be pre-processed and loaded into an object store. While it comes with increased network overhead, we use an object store to store data cheaply and persistently, allowing us to use the same pre-processed data set across multiple queries from multiple clusters. In this case, we use IBMs block store. Second, the actual computation search must run

We use a similar approach for both steps. In each case, a bash helper script invokes a pyspark script on the driver. The driver distributes blast requests to the worker node via a second helper shell script. The responses are collected and sorted to find the best match

# Requirements

## Packages
- Swift (python-swiftclient)
- Blast -- Follow instructions at https://www.ncbi.nlm.nih.gov/books/NBK52640/ to install. Move the `makeblastdb` and `blastn` binaries to spark invocation directory from <blast_root>/bin/   Spark will distribute makeblastdb and blastn to the worker nodes from the invocation directory so there is no need to have the executables copied or made visible on the workers.

Alternatively, if blastn and makdeblastdb are visible to every cluster node, environment variables BLASTN and BMAKEBLASTDB can be set pointing to the executables.   If these paths are relative, e.g. BLASTN=./blastn the code will assume that the executables need to be distributed as mentioned above.

## Cluster
This project assumes a functional spark cluster, similar to the set up in HW6 (e.g., stand-alone spark is all that is necessary.  SparkBLAST does not currently use Hadoop, HDFS, nor YARN.

## Swift Object Store

An object store needs to be setup that will contain containers for the gzipped source fna files, the blast databases (one container per configuration), and a tmp container that will be used to transmit query files to the worker nodes.

Ideally the fna containers should parcelled out into small subunits that can be combined into databases, for example NCBI's RefSeq could be loaded and divided by kingdom, such as refseq_archaea, refseq_bacteria, refseq_plant, refseq_fungal, refseq_vertibrate, refseq_viral, refseq_contaminates.

Databases can then be build by the system to combining these sub-units into logical sets of blast database, for example refseq_archaea + refseq_bacteria + refseq_contaminates.  This gives quite a bit of flexibility as different databases can be combined for different purposes, in addition, the partitioning is also part of the container name so the same set of source databases can exist in the object store in different partition sizes.

## Environment Setup

The following environment variables must be defined (see setup.bash):

Swift object store credentials:
```
export ST_USER="SLOS1..."
export ST_KEY="748fea..."
export ST_AUTH="https://sjc01.objectstorage.service.networklayer.com/auth/v1.0"
```

If the source query file is not visible to all nodes, setting COPY_FILE_TO_OBJECT_STORE will tell spark_blast.py to upload the file to the object store (in the 'tmp' container) and the workers will retrieve the file from the object store.  If the file is local to the invocation directory, spark_blast.py will ignore this flag an copy the file to the object store anyway.
```
export COPY_FILE_TO_OBJECT_STORE=1
```

Partitioning level:
```
export TASKS_TO_USE=&lt;N>
```

BLAST settings:
```
export CORES_TO_USE=&lt;N>
export MAX_FILE_SIZE=&lt;N>
```

CORES_TO_USE will be used to both define how many threads BLAST will be given along with telling SPARK how many threads each task will take. 

MAX_FILE_SIZE is optional and will default to 1GB. A maximum files size of 2GB can be specified and is recommended.  This is passed to makeblastdb.


# Running
## Step 0 -- setup

Fill in the appropriate information in `setup.bash`, then 
```
source setup.bash
```

## Step 1 -- Creating the db

```
./run_blastdb.bash &lt;collection_name> [&lt;collection_name> ...]
```
For example,
```
./run_blastdb.bash refseq_bacteria
```


This invokes `spark_blastdb.py`, which in turn invokes `spark_blastdb.bash` across the worker nodes and will create a blastdb using the contents of &lt;collection_name> [...].  The source database collection(s) should only contain gzipped fna files that will be used to build the blastdbs.   The process will end up creating a new container by the name of `blastdb_<partitions>_<list_of_source_containers>`

## Step 2 -- Querying the db

```
./run_blast.bash &lt;query_file> &lt;mode> &lt;collection_name> [&lt;collection_name> ...]
```
For example,
```
run_blast.bash small_query.fasta 1 refseq_bacteria
```

This invokes `spark_blast.py`, which in turn invokes `spark_blast.bash` across the worker nodes,

Mode currently supports two modes, mode 1, which returns the top 1 hit, and mode 2, which returns the list of the most frequent organism(s) that contain the query features.

If the &lt;query_file> is local to the invocation directory, the file will be transmitted to the worker nodes via the object store regardless of the setting of the COPY_FILE_TO_OBJECT_STORE environment variable.

Compressed files are not currently supported.  Files transmitted via the object store currently have a size limit (5GB).  Allowing for compressed and larger files is slated for a future enhancement.
