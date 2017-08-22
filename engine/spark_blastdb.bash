#!/usr/bin/bash

######################################################################
#                       _        _     _           _      _ _
#  ___ _ __   __ _ _ __| | __   | |__ | | __ _ ___| |_ __| | |__
# / __| '_ \ / _` | '__| |/ /   | '_ \| |/ _` / __| __/ _` | '_ \
# \__ \ |_) | (_| | |  |   <    | |_) | | (_| \__ \ || (_| | |_) |
# |___/ .__/ \__,_|_|  |_|\_\___|_.__/|_|\__,_|___/\__\__,_|_.__/
#     |_|                  |_____|
######################################################################

# Generate the authentication tokens
eval `swift auth`

# Assign a random number to make sure we have a unique name
# across all of the workers
OutFile=blast_db_$RANDOM"_"$RANDOM

# Pass back a status
echo
echo Generating BlastDB $OutFile on `uname -n`

# A list of our genomic data is coming in from stdin, pipe it to
# makeblastdb to create our database.  These 'compressed' dbs
# are expected to be 1/4 the size of the original files and will
# contain all the genomic mysteries of the source data hidden in
# its bits and bytes

# Proud music of the storm,
# Blast that careers so free, whistling across the prairies,
# Strong hum of forest tree-tops--wind of the mountains,
# Personified dim shapes--you hidden orchestras
#   -- Walt Whitman - Leaves of Grass: Book 15, Proud music of the storm
(
while i; do
    hdfs dfs -get $i
done
) | zcat | $MAKEBLASTDB -dbtype nucl -title part_$OutFile -out $OutFile -max_file_sz 2GB

# Upload the files to swift
hdfs dfs -moveFromLocal  $OutFile

# Remove our output
/bin/rm -rf $OutFile*

