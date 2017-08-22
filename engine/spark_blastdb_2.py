import os
import sys
from random import shuffle
from pyspark import SparkContext, SparkConf

def create_db(hdfs_dir):
    conf = SparkConf()
    sc = SparkContext(conf=conf)

    distData = sc.textFile(hdfs_dir)
    mkdb = "hdfs://exec/spark_blast/makeblastdb"
    executable = mkdb + " -dbtype nucl -title part_1 -out /data/testpipe -max_file_sz 2GB"

    # Pass our bash script our parameters, ideally we would like to pass the executor ID/Task ID, but
    # this doesn't appear to be available in ver 2.1.1
    pipeRDD = distData.pipe(executable, {'DBs': db_container, 'MAX_FILE_SIZE': '2GB' })
    for line in pipeRDD.collect():
        print(line)

if __name__ == "__main__":
    create_db("hdfs://data/spark_blast/geba")