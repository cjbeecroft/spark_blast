#!/usr/bin/bash

######################################################################
#                       _        _     _           _      _ _
#  ___ _ __   __ _ _ __| | __   | |__ | | __ _ ___| |_ __| | |__
# / __| '_ \ / _` | '__| |/ /   | '_ \| |/ _` / __| __/ _` | '_ \
# \__ \ |_) | (_| | |  |   <    | |_) | | (_| \__ \ || (_| | |_) |
# |___/ .__/ \__,_|_|  |_|\_\___|_.__/|_|\__,_|___/\__\__,_|_.__/
#     |_|                  |_____|
######################################################################

# ST_KEY, ST_AUTH, ST_USER should be in the environment

if [[ -z "${ST_KEY}" ]]; then
    echo "ST_KEY is not defined"
    exit
fi

if [[ -z "${ST_USER}" ]]; then
    echo "ST_KEY is not defined"
    exit
fi

if [[ -z "${ST_AUTH}" ]]; then
    echo "ST_KEY is not defined"
    exit
fi

# Get our auth keys from swfit
eval `swift auth`

# Assign a random number to make sure we have a unique name
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
while read LINE; do
    curl -H "X-Auth-Token: $OS_AUTH_TOKEN" $OS_STORAGE_URL/$LINE
done
) | zcat | ./makeblastdb -dbtype nucl -title part_$OutFile -out $OutFile

# Upload the files to swift
for var in $OutFile*; do
    swift upload $DBs $var
    /bin/rm $var
done
