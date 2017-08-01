from pyspark import SparkContext, SparkConf

# Set the context
conf = SparkConf() # .setAppName("spark_blast").setMaster(master)
sc = SparkContext(conf=conf)

# Quiet the logs
sc.setLogLevel("WARN")

Home = "/root/spark_blast/ProofOfConcept/"
QueryFile = Home + "query.fasta"
ShellScript = Home + "SparkBlast.bash"

data = [" ".join((QueryFile, Home + "part1.fna")),
        " ".join((QueryFile, Home + "part2.fna")),
        " ".join((QueryFile, Home + "part3.fna"))]

distData = sc.parallelize(data,3)

pipeRDD = distData.pipe(ShellScript)

for line in pipeRDD.collect():
    print(line)
