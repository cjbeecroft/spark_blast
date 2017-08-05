import os
import sys
from pyspark import SparkContext, SparkConf
import swiftclient

'''                   _        _     _           _      _ _
 ___ _ __   __ _ _ __| | __   | |__ | | __ _ ___| |_ __| | |__   _ __  _   _
/ __| '_ \ / _` | '__| |/ /   | '_ \| |/ _` / __| __/ _` | '_ \ | '_ \| | | |
\__ \ |_) | (_| | |  |   <    | |_) | | (_| \__ \ || (_| | |_) || |_) | |_| |
|___/ .__/ \__,_|_|  |_|\_\___|_.__/|_|\__,_|___/\__\__,_|_.__(_) .__/ \__, |
    |_|                  |_____|                                |_|    |___/
'''

def main(ST_AUTH, ST_USER, ST_KEY, SHARDS, OBJECT_STORES):
    # Set the context
    conf = SparkConf() # .setAppName("spark_blast").setMaster(master)
    conf.setExecutorEnv(key='Auth', value='value', pairs=None)
    sc = SparkContext(conf=conf)

    # Quiet the logs
    sc.setLogLevel("WARN")

    # Set our spark database creation script and add all the files that are needed to be on the
    # remote hosts to the shall script
    ShellScript = "SparkBlastDB.bash"
    sc.addFile("makeblastdb")
    sc.addFile(ShellScript)

    # this will be our root name for our DB names
    DBs = "blastdb_" + ",".join(sorted(OBJECT_STORES)) + "_" + str(SHARDS)

    # log into swift
    conn = swiftclient.Connection(user=ST_USER, key=ST_KEY, authurl=ST_AUTH)

    # Create the continer for our results if it does not exist
    if DBs not in [t['name'] for t in conn.get_account()[1]]:
        print("Creating container " + DBs + " to contain our blast dbs")
        conn.put_container(DBs)
    else:
        # Container already existed, remove any contents
        print("Container " + DBs + " already exists, removing contents")
        for data in conn.get_container(DBs)[1]:
            conn.delete_object(DBs, data['name'])

    # Get the list of objects we are oing to need
    files = []
    for container in OBJECT_STORES:
        print("Collecting files from " + container)
        for data in conn.get_container(container)[1]:
            files.append("%s/%s" % (container, data['name']))

    # Distribute our data
    distData = sc.parallelize(files, SHARDS)

    # Pass our bash script our parameters, spark is grumpy with an integer, so convert SHARDS to a string
    pipeRDD = distData.pipe(ShellScript, {'ST_AUTH': ST_AUTH, 'ST_USER': ST_USER, 'ST_KEY': ST_KEY, 'SHARDS': str(SHARDS), 'DBs': DBs})

    # Now let the bash script do its work.  This will assemble and store the results of all the list of
    # fna files collected from each Object Store
    # 
    # It has done its work--I toss it carelessly to fall where it may
    #   -- Walt Whitman: Leaves of Grass, Book 4 - Children of Adam, Spontaneous Me
    print("Starting to create %d blast database 'shards'" % SHARDS)
    for line in pipeRDD.collect():
        print(line)

    print("Complete")


if __name__ == '__main__':

    # Get our environment
    ST_AUTH = os.getenv('ST_AUTH')
    ST_USER = os.getenv('ST_USER')
    ST_KEY = os.getenv('ST_KEY')

    if ST_AUTH is None or ST_USER is None or ST_KEY is None:
        print("Environment does not contain ST_AUTH or ST_USER or ST_KEY")
        print("Please set these values object store before running")
        exit()

    if len(sys.argv) > 1:
        # Get the list of shards we are going to create
        try:
            SHARDS = int(sys.argv[1])
        except:
            print("Argument 1 (number of database shards to create) is not an integer")

        # Get the list of containers we should look at
        if len(sys.argv) > 2:
            OBJECT_STORES = sys.argv[2:]

            # Run
            main(ST_AUTH, ST_USER, ST_KEY, SHARDS, OBJECT_STORES)
        else:
            print("No object containers listed, please provide a list of object containers containing fna files")

    else:
        print("Argument 1 (number of database shards to create) is not provided")
        print("Usage: Shards object_store_to_use [object_store_to_user ...]")