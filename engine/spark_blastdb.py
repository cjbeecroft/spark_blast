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


def main(ST_AUTH, ST_USER, ST_KEY, MAX_FILE_SIZE, TASKS, MAKEBLASTDB, OBJECT_STORES):
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

    # Quiet the logs
    sc.setLogLevel("WARN")

    # Set our spark database creation script and add all the files that are needed to be on the
    # remote hosts to the shall script
    ShellScript = "spark_blastdb.bash"
    sc.addFile(ShellScript)

    # Copy over makeblastdb if it is local
    if os.path.dirname(MAKEBLASTDB) == "." or os.path.dirname(MAKEBLASTDB) == "":
        sc.addFile(MAKEBLASTDB)

    # this will be our root name for our DB names
    db_container = "blastdb_" + "-".join(sorted(OBJECT_STORES)) + "_" + str(TASKS)

    # log into swift
    conn = swiftclient.Connection(user=ST_USER, key=ST_KEY, authurl=ST_AUTH)

    # Create the continer for our results if it does not exist
    if db_container not in [t['name'] for t in conn.get_account()[1]]:
        print("Creating container " + db_container + " to contain our blast dbs")
        conn.put_container(db_container)
    else:
        # Container already existed, remove any contents
        print("Container " + db_container + " already exists, removing contents")
        for data in conn.get_container(db_container)[1]:
            conn.delete_object(db_container, data['name'])

    # Get the list of objects we are going to need
    files = []
    for fna_container in OBJECT_STORES:
        # Check to see if the fna_container exists, if not exit
        if fna_container not in [t['name'] for t in conn.get_account()[1]]:
            print("Container %s does not exist" % fna_container)
            exit()

        print("Collecting files from " + fna_container)
        for data in conn.get_container(fna_container)[1]:
            files.append("%s/%s" % (fna_container, data['name']))

    # Distribute our data, shuffle it in case there is any size ordering going on
    shuffle(files)
    distData = sc.parallelize(files, TASKS)

    # Pass our bash script our parameters, ideally we would like to pass the executor ID/Task ID, but
    # this doesn't appear to be available in ver 2.1.1
    pipeRDD = distData.pipe(ShellScript, {'ST_AUTH': ST_AUTH, 'ST_USER': ST_USER, 'ST_KEY': ST_KEY,
                                          'DBs': db_container, 'MAX_FILE_SIZE': MAX_FILE_SIZE, 'MAKEBLASTDB': MAKEBLASTDB})

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

    # Get our environment
    ST_AUTH = os.getenv('ST_AUTH')
    ST_USER = os.getenv('ST_USER')
    ST_KEY = os.getenv('ST_KEY')
    TASKS = os.getenv('TASKS_TO_USE')
    MAX_FILE_SIZE = os.getenv('MAX_FILE_SIZE')
    # Get the blast program, default to local copy of makeblastdb
    MAKEBLASTDB = os.getenv('MAKEBLASTDB', './makeblastdb')

    if ST_AUTH is None or ST_USER is None or ST_KEY is None or TASKS is None:
        print("Environment does not contain ST_AUTH, ST_USER, ST_KEY, or TASKS_TO_USE")
        print("Please set these values object store before running")
        usage()
        exit()

    if not os.path.exists(MAKEBLASTDB):
        print("MAKEBLASTDB env variable not set or makeblastdb not in current directory")
        usage()
        exit()

    try:
        TASKS = int(TASKS)
    except:
        print("TASKS_TO_USE is not defined as an integer")
        usage()
        exit()

    if len(sys.argv) > 1:
        OBJECT_STORES = sys.argv[1:]

        # Run
        main(ST_AUTH, ST_USER, ST_KEY, MAX_FILE_SIZE, TASKS, MAKEBLASTDB, OBJECT_STORES)
    else:
        print("No object containers listed, please provide a list of object containers containing fna files")
        usage()
