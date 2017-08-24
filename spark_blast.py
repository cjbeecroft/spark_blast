import os
import sys
# import logging
import random
from pyspark import SparkContext, SparkConf
import swiftclient

'''                   _        _     _           _
 ___ _ __   __ _ _ __| | __   | |__ | | __ _ ___| |_
/ __| '_ \ / _` | '__| |/ /   | '_ \| |/ _` / __| __|
\__ \ |_) | (_| | |  |   <    | |_) | | (_| \__ \ |_
|___/ .__/ \__,_|_|  |_|\_\___|_.__/|_|\__,_|___/\__|
    |_|                  |_____|
'''

def maxByIndex(a, b, index):
    aScore = a[index]
    bScore = b[index]

    maxScore = max(aScore, bScore)

    if aScore == maxScore:
        return a
    else:
        return b

def setup():
    ''' setup the spark context and get the logger '''
    # Set the context
    conf = SparkConf()
    conf.setExecutorEnv(key='Auth', value='value', pairs=None)
    sc = SparkContext(conf=conf)
    logger = sc._jvm.org.apache.log4j.LogManager.getLogger(__name__)
    return sc, logger


def main(sc, logger, ST_AUTH, ST_USER, ST_KEY, TASKS, CORES, BLASTN, LOCAL_FILE, QUERY_FILE, MODE, OBJECT_STORES):
    ''' Main function
        ST_AUTH - Object storage auth string where fna containers are found
        ST_USER - Ojbect storage user token
        ST_KEY - Ojbect storage secret token
        TASKS - Number of tasks to launch, db partition factor
        CORES - Number of cores to devote to each task
        BLASTN - Location of blastn executable
        QUERY_FILE - fasta query file
        MODE - operation mode, 1 = top search, 2 = most common genome
        OBJECT_STORES - list of source containers that built the blast db
    '''

    # Quiet the logs
    sc.setLogLevel("WARN")

    # N = 5 # number of top results to take

    # Set our spark database creation script and add all the files that are needed to be on the
    # remote hosts to the shall script
    ShellScript = "spark_blast.bash"
    sc.addFile(ShellScript)

    # Copy over blastn if it is local
    if os.path.dirname(BLASTN) == "." or os.path.dirname(BLASTN) == "":
        sc.addFile(BLASTN)

    # Get the file name part of QUERY_FILE
    Query_File = os.path.basename(QUERY_FILE)

    # this will be our root name for our DB names
    container = "blastdb_" + "-".join(sorted(OBJECT_STORES)) + "_" + str(TASKS)

    # log into swift
    conn = swiftclient.Connection(user=ST_USER, key=ST_KEY, authurl=ST_AUTH)

    # Change LOCAL_FILE to true if our query file appears to be local
    if os.path.dirname(QUERY_FILE) == "." or os.path.dirname(QUERY_FILE) == "":
        LOCAL_FILE = "1"


    # Take care of the query file
    if LOCAL_FILE == '1':
        # put it in the object store
        # create a tmp container if it isn't there
        if 'tmp' not in [t['name'] for t in conn.get_account()[1]]:
            conn.put_container('tmp')
            # TODO need to verify that container was created

        # Name it something random, so if multiple runs are going we don't step on each other
        random.seed()
        Query_File = "query_" + str(random.randint(10000,99999)) + ".fasta"
        # write it out to the object store
        # TODO need to handle files larger than the object store maximum
        #      Thought here is to overload the LOCAL_FILE var to communicate the number of pieces
        #      (0 = not local, != 0 = in data store and in LOCAL_FILE pieces)
        with open(QUERY_FILE, 'r') as local:
            conn.put_object('tmp', Query_File, contents=local, content_type='text/plain')
    else:
        # if it is not a local file, just pass the name along
        Query_File = QUERY_FILE

    # Verify the container we need is present
    if container not in [t['name'] for t in conn.get_account()[1]]:
        logger.info("No database parition created for %s partition factor %d" % ("+".join(sorted(OBJECT_STORES)), TASKS))
        exit()

    # Get the list of objects we are going to need
    dbs = {}
    logger.info("Collecting DBs from " + container)
    for data in conn.get_container(container)[1]:
        base = data['name'].split('.', 1)[0]
        if base not in dbs:
            dbs[base] = []
        dbs[base].append(data['name'])

    # Assemble our task list
    files = []
    for db in dbs:
        files.append("%s %s %s %s" % (Query_File, container, db, " ".join(dbs[db])))

    # Distribute our data
    distData = sc.parallelize(files, TASKS)

    options = ""

    # Set our search options
    if MODE == "1":
        options = "-max_target_seqs 1"
    # elif MODE == "2":
    #     options = ??

    # Pass our bash script our parameters, ideally we would like to pass the executor ID/Task ID, but
    # this doesn't appear to be available in ver 2.1.1
    pipeRDD = distData.pipe(ShellScript, {'ST_AUTH': ST_AUTH, 'ST_USER': ST_USER, 'ST_KEY': ST_KEY,
                                          'THREADS': str(CORES), 'OPTIONS': options, 'BLASTN': BLASTN,
                                          'LOCAL_FILE': LOCAL_FILE})

    # Now let the bash script do its work.  This will run blast using our query file across all the
    # DB partitions searching for matching genomic reads.
    #
    # Failing to fetch me at first keep encouraged,
    # Missing me one place search another,
    # I stop somewhere waiting for you.
    #   -- Walt Whitman - Leaves of Grass: Book 3, Song of Myself, Verse 52
    logger.info("Search through all the DBs for matching sequence")
    if MODE == "1":
        query_count  = pipeRDD.map(lambda x : (x.split(',')[0], (x.split(',')[2], x.split('|')[-1:][0]) )) \
            .reduceByKey( lambda x, y : maxByIndex(x, y, 0)) \
            .sortByKey(True) \
            .map(lambda x : str(x[0]) + ", " + str(x[1][1]))
        for line in  query_count.collect():
            print line
    elif MODE == "2":

        specie_count = pipeRDD.map( lambda x : (x.split(',')[11].split(' ', 1)[-1], x.split(',')[0] )) \
            .distinct() \
            .map(lambda x : (x[0], 1)) \
            .reduceByKey(lambda x,y:x+y) \
            .sortByKey(False) \
            .map(lambda x:(str(x[0]) + ", " + str(x[1])))
        for line in specie_count.collect():
            print line

    # We are done, remove our uploaded file
    if LOCAL_FILE == '1':
        # TODO if there are multiple pieces, we need to address cleaning up
        conn.delete_object('tmp', Query_File)


def usage(logger):
    ''' Usage: print home help information '''
    logger.warn("Usage: <fasta file to query> <search mode [1|2]> <object container[s] used to build blast databases>")
    logger.warn("       search mode 1: find top hit for each line in file, or")
    logger.warn("                   2: find top references|organisms referenced in query file\n")
    logger.warn("Envionment variables:")
    logger.warn("       ST_AUTH - Object store auth token URL")
    logger.warn("       ST_USER - Object store user name of account on cluster")
    logger.warn("       ST_KEY - Object store user password of account on cluster")
    logger.warn("       TASKS_TO_USE - The number of workers to devote to the task/number of db partitions to use")
    logger.warn("       CORES_TO_USE - The number of cores each worker should use")
    logger.warn("       BLASTN - The name and location of the blastn program")


if __name__ == '__main__':

    sc, logger = setup()

    # Get our environment
    ST_AUTH = os.getenv('ST_AUTH')
    ST_USER = os.getenv('ST_USER')
    ST_KEY = os.getenv('ST_KEY')
    LOCAL_FILE = os.getenv('COPY_FILE_TO_OBJECT_STORE', '0')
    TASKS = os.getenv('TASKS_TO_USE')
    CORES = os.getenv('CORES_TO_USE')
    BLASTN = os.getenv('BLASTN', './blastn')

    if ST_AUTH is None or ST_USER is None or ST_KEY is None or TASKS is None:
        logger.error("Environment does not contain ST_AUTH, ST_USER, ST_KEY, or TASKS_TO_USE")
        logger.error("Please set these values object store before running\n")
        usage(logger)
        exit()

    if not os.path.exists(BLASTN):
        logger.error("BLASTN env variable not set or blastn not in current directory")
        exit()

    try:
        TASKS = int(TASKS)
    except:
        logger.error("TASKS_TO_USE is not defined as an integer")
        exit()

    if len(sys.argv) > 2:
        QUERY_FILE = sys.argv[1]
        MODE = sys.argv[2]
        OBJECT_STORES = sys.argv[3:]

        if CORES is None:
            CORES = 1

        if MODE not in ('1', '2'):
            logger.error("search mode is not 1 or 2\n")
            usage(logger)

        else:
            # Run
            main(sc, logger, ST_AUTH, ST_USER, ST_KEY, TASKS, CORES, BLASTN, LOCAL_FILE, QUERY_FILE, MODE, OBJECT_STORES)

    else:
        usage(logger)
