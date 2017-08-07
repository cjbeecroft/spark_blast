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
    
    # Download the database files from the object store
    swift -q download $Container ${array[@]:3}

    $BLASTN -db $Database $OPTIONS \
        -num_threads $THREADS \
        -outfmt "10 qseqid pident length mismatch gapopen qstart qend sstart ssend evalue bitscore stitle" \
        < $QueryFile
done

# And we don't need blast if we've copied it, e.g., it is a local file
if [ `dirname $BLASTN` == "." ] ; then
    /bin/rm -rf $BLASTN
fi

