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

    if [ $LOCAL_FILE != '0' ]; then
        # Download the database files from the object store
        # TODO need to address files larger that 5GB
        swift -q download 'tmp' $QueryFile
    fi

    # Run Blast, it will tell us a story about our genomic poems

    #  I see the places of the sagas,
    #  I see pine-trees and fir-trees torn by northern blasts,
    #  I see granite bowlders and cliffs, I see green meadows and lakes,
    #  I see the burial-cairns of Scandinavian warriors,
    #  I see them raised high with stones by the marge of restless oceans,
    #      that the dead men's spirits when they wearied of their quiet
    #      graves might rise up through the mounds and gaze on the tossing
    #      billows, and be refresh'd by storms, immensity, liberty, action.
    #         -- Walt Whitman - Leaves of Grass: Book 6, Salut au Monde, verse 7
    $BLASTN -db $Database $OPTIONS \
        -num_threads $THREADS \
        -outfmt "10 qseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore stitle" \
        < $QueryFile

    # remove the downloaded DBs
    /bin/rm -rf ${array[@]:3}
done

# Remove the query file
if [ $LOCAL_FILE != '0' ]; then
    # TODO need to address files larger that 5GB
    /bin/rm -rf $QueryFile
fi

# And we don't need blast if we've copied it, e.g., it is a local file
if [ `dirname $BLASTN` == "." ] ; then
    /bin/rm -rf $BLASTN
fi
