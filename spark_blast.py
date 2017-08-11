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

N = 3

def main(ST_AUTH, ST_USER, ST_KEY, TASKS, CORES, BLASTN, QUERY_FILE, MODE, OBJECT_STORES):
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
    # Set the context
    conf = SparkConf()
    conf.setExecutorEnv(key='Auth', value='value', pairs=None)
    sc = SparkContext(conf=conf)

    # Quiet the logs
    sc.setLogLevel("WARN")

    # Set our spark database creation script and add all the files that are needed to be on the
    # remote hosts to the shall script
    ShellScript = "spark_blast.bash"
    sc.addFile(ShellScript)
    sc.addFile(QUERY_FILE)

    # Copy over blastn if it is local
    if os.path.dirname(BLASTN) == "." or os.path.dirname(BLASTN) == "":
        sc.addFile(BLASTN)

    # Get the file name part of QUERY_FILE
    Query_File = os.path.basename(QUERY_FILE)

    # this will be our root name for our DB names
    container = "blastdb_" + "-".join(sorted(OBJECT_STORES)) + "_" + str(TASKS)

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

    # Set our search options
    if MODE == "1":
        options = "-max_target_seqs 1"
    # elif MODE == "2":
    #     options = ??

    # Pass our bash script our parameters, ideally we would like to pass the executor ID/Task ID, but
    # this doesn't appear to be available in ver 2.1.1
    pipeRDD = distData.pipe(ShellScript, {'ST_AUTH': ST_AUTH, 'ST_USER': ST_USER, 'ST_KEY': ST_KEY,
                                          'THREADS': str(CORES), 'OPTIONS': options, 'BLASTN': BLASTN})

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
    if mode == "1":
        # map "query, score, name" to (query, (score, name))
        query_count  = pipeRDD.map (lambda x : (x.split(',')[0], x.split(',')[2:3])) \
            .reduceByKey( lambda x, y : max(x[0], y[0])) # reduce by key, picking the one with the highest score

        print query_count

    elif mode == "2":
        # grab the genus_species string. map to (genus_species, 1)
        specie_count = pipeRDD.map( lambda x : (x.split(',')[11:].split(' ')[1:], 1) ) \
            .reduceByKey(lambda x, y : x + y) # count the number of occurrences of each string (genus, count)
            .map(lambda x:(x[1],x[0])) # map to (count, genus)
            .sortByKey(False)  # sort descending

        print specie_count.take(N)


    else:
        print "error -- mode not implemented"
    # More code here


def usage():
    ''' Usage: print home help information '''
    print("Usage: <fasta file to query> <search mode [1|2]> <object container[s] used to build blast databases>")
    print("       search mode 1: find top hit for each line in file, or")
    print("                   2: find top references|organisms referenced in query file\n")
    print("Envionment variables:")
    print("       ST_AUTH - Object store auth token URL")
    print("       ST_USER - Object store user name of account on cluster")
    print("       ST_KEY - Object store user password of account on cluster")
    print("       TASKS_TO_USE - The number of workers to devote to the task/number of db partitions to use")
    print("       CORES_TO_USE - The number of cores each worker should use")
    print("       BLASTN - The name and location of the blastn program")


if __name__ == '__main__':

    # Get our environment
    ST_AUTH = os.getenv('ST_AUTH')
    ST_USER = os.getenv('ST_USER')
    ST_KEY = os.getenv('ST_KEY')
    TASKS = os.getenv('TASKS_TO_USE')
    CORES = os.getenv('CORES_TO_USE')
    BLASTN = os.getenv('BLASTN', './blastn')

    if ST_AUTH is None or ST_USER is None or ST_KEY is None or TASKS is None:
        print("Environment does not contain ST_AUTH, ST_USER, ST_KEY, or TASKS_TO_USE")
        print("Please set these values object store before running\n")
        usage()
        exit()

    if not os.path.exists(BLASTN):
        print("BLASTN env variable not set or blastn not in current directory")
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

        if CORES is None:
            CORES = 1

        if MODE not in ('1', '2'):
            print("search mode is not 1 or 2\n")
            usage()

        else:
            # Run
            main(ST_AUTH, ST_USER, ST_KEY, TASKS, CORES, BLASTN, QUERY_FILE, MODE, OBJECT_STORES)

    else:
        usage()
