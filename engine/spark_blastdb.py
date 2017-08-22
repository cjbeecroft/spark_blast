import os
import sys
from random import shuffle
from pyspark import SparkContext, SparkConf
import swiftclient

'''                   _        _     _           _      _ _
 ___ _ __   __ _ _ __| | __   | |__ | | __ _ ___| |_ __| | |__
/ __| '_ \ / _` | '__| |/ /   | '_ \| |/ _` / __| __/ _` | '_ \
\__ \ |_) | (_| | |  |   <    | |_) | | (_| \__ \ || (_| | |_) |
|___/ .__/ \__,_|_|  |_|\_\___|_.__/|_|\__,_|___/\__\__,_|_.__/
    |_|                  |_____|
'''


def main():
    ''' Main function
        ST_AUTH - Object storage auth string where fna containers are found
        ST_USER - Ojbect storage user token
        ST_KEY - Ojbect storage secret token
        MAX_FILE_SIZE - Maximum file set parameter for makeblastdb
        TASKS - Number of tasks to launch, db partition factor
        MAKEBLASTDB - Location of makeblastdb executable
        OBJECT_STORES - list of source containers that built the blast db
    '''
    # Set the context
    conf = SparkConf()
    sc = SparkContext(conf=conf)
    all_config = sc._conf.getAll()
    fasta_files = all_config['dirs'].split(",")

    OBJECT_STORES = ['geba']
    TASKS = 3

    # Quiet the logs
    sc.setLogLevel("WARN")

    # Set our spark database creation script and add all the files that are needed to be on the
    # remote hosts to the shall script
    ShellScript = "hdfs:///exec/spark_blast/spark_blastdb.bash"
    sc.addFile(ShellScript)

    sc.addFile("hdfs:///exec/spark_blast/makeblastdb")
    # this will be our root name for our DB names
    db_container = "blastdb_" + "-".join(sorted(OBJECT_STORES)) + "_" + str(TASKS)

    # Get the list of objects we are going to need, i.e. .fast files
    # Distribute our data, shuffle it in case there is any size ordering going on
    shuffle(fasta_files)
    distData = sc.parallelize(fasta_files, TASKS)

    # Pass our bash script our parameters, ideally we would like to pass the executor ID/Task ID, but
    # this doesn't appear to be available in ver 2.1.1
    pipeRDD = distData.pipe(ShellScript)

    # Now let the bash script do its work.  This will assemble and store the results of all the list of
    # fna files collected from each Object Store
    #
    # It has done its work--I toss it carelessly to fall where it may
    #   -- Walt Whitman: Leaves of Grass, Book 4 - Children of Adam, Spontaneous Me
    print("Starting to create %d blast database 'partitions'" % TASKS)
    for line in pipeRDD.collect():
        print(line)

    print("Complete")


def usage():
    ''' Usage: print home help information '''
    print("Usage: <object container[s] used to build blast databases>")
    print("Envionment variables:")
    print("       ST_AUTH - Object store auth token URL")
    print("       ST_USER - Object store user name of account on cluster")
    print("       ST_KEY - Object store user password of account on cluster")
    print("       TASKS_TO_USE - The number of workers to devote to the task/number of db partitions to use")
    print("       MAX_FILE_SIZE - The maximum file size parameter to makeblastdb")
    print("       MAKEBLASTDB - The name and location of the blastn program, defaults to './makeblastdb'")


if __name__ == '__main__':

    main()
