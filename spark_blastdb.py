import os
import sys
from pyspark import SparkContext, SparkConf
import swiftclient

'''                   _        _     _           _      _ _
 ___ _ __   __ _ _ __| | __   | |__ | | __ _ ___| |_ __| | |__
/ __| '_ \ / _` | '__| |/ /   | '_ \| |/ _` / __| __/ _` | '_ \
\__ \ |_) | (_| | |  |   <    | |_) | | (_| \__ \ || (_| | |_) |
|___/ .__/ \__,_|_|  |_|\_\___|_.__/|_|\__,_|___/\__\__,_|_.__/
    |_|                  |_____|
'''

def main(ST_AUTH, ST_USER, ST_KEY, TASKS, OBJECT_STORES):
    # Set the context
    conf = SparkConf() # .setAppName("spark_blast").setMaster(master)
    conf.setExecutorEnv(key='Auth', value='value', pairs=None)
    sc = SparkContext(conf=conf)

    # Quiet the logs
    sc.setLogLevel("WARN")

    # Set our spark database creation script and add all the files that are needed to be on the
    # remote hosts to the shall script
    ShellScript = "spark_blastdb.bash"
    sc.addFile("makeblastdb")
    sc.addFile(ShellScript)

    # this will be our root name for our DB names
    container = "blastdb_" + ",".join(sorted(OBJECT_STORES)) + "_" + str(TASKS)

    # log into swift
    conn = swiftclient.Connection(user=ST_USER, key=ST_KEY, authurl=ST_AUTH)

    # Create the continer for our results if it does not exist
    if container not in [t['name'] for t in conn.get_account()[1]]:
        print("Creating container " + container + " to contain our blast dbs")
        conn.put_container(container)
    else:
        # Container already existed, remove any contents
        print("Container " + container + " already exists, removing contents")
        for data in conn.get_container(container)[1]:
            conn.delete_object(container, data['name'])

    # Get the list of objects we are oing to need
    files = []
    for container in OBJECT_STORES:
        print("Collecting files from " + container)
        for data in conn.get_container(container)[1]:
            files.append("%s/%s" % (container, data['name']))

    # Distribute our data
    distData = sc.parallelize(files, TASKS)

    # Pass our bash script our parameters, ideally we would like to pass the executor ID/Task ID, but
    # this doesn't appear to be available in ver 2.1.1
    pipeRDD = distData.pipe(ShellScript, {'ST_AUTH': ST_AUTH, 'ST_USER': ST_USER, 'ST_KEY': ST_KEY, 'DBs': container})

    # Now let the bash script do its work.  This will assemble and store the results of all the list of
    # fna files collected from each Object Store
    # 
    # It has done its work--I toss it carelessly to fall where it may
    #   -- Walt Whitman: Leaves of Grass, Book 4 - Children of Adam, Spontaneous Me
    print("Starting to create %d blast database 'partitions'" % TASKS)
    for line in pipeRDD.collect():
        print(line)

    print("Complete")


if __name__ == '__main__':

    # Get our environment
    ST_AUTH = os.getenv('ST_AUTH')
    ST_USER = os.getenv('ST_USER')
    ST_KEY = os.getenv('ST_KEY')
    TASKS = os.getenv('TASKS_TO_USE')

    if ST_AUTH is None or ST_USER is None or ST_KEY is None or TASKS is None:
        print("Environment does not contain ST_AUTH, ST_USER, ST_KEY, or TASKS_TO_USE")
        print("Please set these values object store before running")
        exit()

    try:
        TASKS = int(TASKS)
    except:
        print("TASKS_TO_USE is not defined as an integer")
        exit()

    if len(sys.argv) > 1:
        OBJECT_STORES = sys.argv[1:]

        # Run
        main(ST_AUTH, ST_USER, ST_KEY, TASKS, OBJECT_STORES)
    else:
        print("No object containers listed, please provide a list of object containers containing fna files")
