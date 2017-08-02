Proof of Concept Code

- Assumes there are three nodes, spark1, spark2, spark3
    which have ssh equivalence set up for root

- Assumes this is run as root

- Assumes this is deployed under /root
    (so the current directory is /root/spark_blast/ProofOfConcept)


go.test - Downloads needed files, copies files over to spark2, spark3, runs code

SparkBlast.bash - bash wrapper that spark_blast.py calls

spark_blast.py - spark program



go.test downloads blast_data.tar.gz from dropbox if part1.fna.sqn does
    not exist and then untars the file and removes it.


Contents of blast_data.tar.gz are:

blastn - blastn linux standalone executable
makeblastdb - make blast db linux standalone executable

part1.fna.nhr - blastdb for part1 of the GEBA data
part1.fna.nin
part1.fna.nsq

part2.fna.nhr - blastdb for part2 of the GEBA data
part2.fna.nin
part2.fna.nsq

part3.fna.nhr - blastdb for part3 of the GEBA data
part3.fna.nin
part3.fna.nsq
