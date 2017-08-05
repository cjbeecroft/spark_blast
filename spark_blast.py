import os
import sys
from pyspark import SparkContext, SparkConf
import swiftclient

'''                   _        _     _           _
 ___ _ __   __ _ _ __| | __   | |__ | | __ _ ___| |_
/ __| '_ \ / _` | '__| |/ /   | '_ \| |/ _` / __| __|
\__ \ |_) | (_| | |  |   <    | |_) | | (_| \__ \ |_
|___/ .__/ \__,_|_|  |_|\_\___|_.__/|_|\__,_|___/\__|
    |_|                  |_____|
'''

def main(ST_AUTH, ST_USER, ST_KEY, TASKS, QUERY_FILE, MODE, OBJECT_STORES):
    # Set the context
    conf = SparkConf() # .setAppName("spark_blast").setMaster(master)
    conf.setExecutorEnv(key='Auth', value='value', pairs=None)
    sc = SparkContext(conf=conf)

    # Quiet the logs
    sc.setLogLevel("WARN")

    # Set our spark database creation script and add all the files that are needed to be on the
    # remote hosts to the shall script
    ShellScript = "spark_blast.bash"
    sc.addFile("blastn")
    sc.addFile(ShellScript)
    sc.addFile(QUERY_FILE)

    # Get the file name part of QUERY_FILE
    Query_File = os.path.basename(QUERY_FILE)

    # this will be our root name for our DB names
    container = "blastdb_" + ",".join(sorted(OBJECT_STORES)) + "_" + str(TASKS)

    # log into swift
    conn = swiftclient.Connection(user=ST_USER, key=ST_KEY, authurl=ST_AUTH)

    # Verify the container we need is present
    if container not in [t['name'] for t in conn.get_account()[1]]:
        print("No database parition created for %s partition factor %d" % ("+".join(sorted(OBJECT_STORES)), TASKS))
        exit()

    # Get the list of objects we are oing to need
    dbs = {}
    print("Collecting DBs from " + container)
    for data in conn.get_container(container)[1]:
        (base, ext) = data['name'].split('.')
        if base not in dbs:
            dbs[base] = []
        dbs[base].append(data['name'])

    # Assemble our task list
    files = []
    for db in dbs:
        files.append("%s %s %s %s" % (Query_File, container, db, " ".join(dbs[db])))

    # Distribute our data
    distData = sc.parallelize(files, TASKS)

    # Pass our bash script our parameters, ideally we would like to pass the executor ID/Task ID, but
    # this doesn't appear to be available in ver 2.1.1
    pipeRDD = distData.pipe(ShellScript, {'ST_AUTH': ST_AUTH, 'ST_USER': ST_USER, 'ST_KEY': ST_KEY})

    # Now let the bash script do its work.  This will run blast using our query file across all the
    # DB partitions searching for matching genomic reads.
    # 
    # Failing to fetch me at first keep encouraged,
    # Missing me one place search another,
    # I stop somewhere waiting for you.
    #   -- Walt Whitman - Leaves of Grass: Book 3, Song of Myself, Verse 52
    print("Search through all the DBs for matching sequence")
    for line in pipeRDD.collect():
        print(line)

    # Map Reduce now

    # More code here


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

    if len(sys.argv) > 2:
        QUERY_FILE = sys.argv[1]
        MODE = sys.argv[2]
        OBJECT_STORES = sys.argv[3:]

        # Run
        main(ST_AUTH, ST_USER, ST_KEY, TASKS, QUERY_FILE, MODE, OBJECT_STORES)

    else:
        print("Usage: <fasta file to query> <search mode [1|2]> <object container[s] used to build blast databases>")
        print("       search mode 1: find top hit for each line in file, or")
        print("                   2: find top references|organisms referenced in query file")
