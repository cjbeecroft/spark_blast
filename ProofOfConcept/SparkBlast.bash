#!/usr/bin/bash

Home=/root/spark_blast/ProofOfConcept

while read LINE; do
    read -r -a array <<< "$LINE"
    QueryFile=${array[0]}
    DataBase=${array[1]}

    $Home/blastn -db $DataBase -max_target_seqs 1 \
        -outfmt "10 qseqid pident length mismatch gapopen qstart qend sstart ssend evalue bitscore stitle" \
        < $QueryFile
done
