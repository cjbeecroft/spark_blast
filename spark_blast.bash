#!/usr/bin/bash

######################################################################
#                       _        _     _           _
#  ___ _ __   __ _ _ __| | __   | |__ | | __ _ ___| |_
# / __| '_ \ / _` | '__| |/ /   | '_ \| |/ _` / __| __|
# \__ \ |_) | (_| | |  |   <    | |_) | | (_| \__ \ |_
# |___/ .__/ \__,_|_|  |_|\_\___|_.__/|_|\__,_|___/\__|
#     |_|                  |_____|
######################################################################

while read LINE; do
    read -r -a array <<< "$LINE"
    QueryFile=${array[0]}
    Container=${array[1]}
    Database=${array[2]}
    
    files=${#array[@]}

    # Download the database files from the object store
    for (( i=3; i<${#array[@]}; i++ )); do
        swift -q download $Container ${array[$i]}
    done

    ./blastn -db $Database -max_target_seqs 1 \
        -outfmt "10 qseqid pident length mismatch gapopen qstart qend sstart ssend evalue bitscore stitle" \
        < $QueryFile
done
