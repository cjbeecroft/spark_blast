#!

# Our environment
echo Master: $MASTER
echo ST_USER: $ST_USER
echo ST_KEY: $ST_KEY
echo ST_AUTH: $ST_AUTH

# Shet the shard factor to cluster size - 1
export SLAVES=`wc -l $SPARK_HOME/conf/slaves | cut -d" " -f1`
export SHARD_FACTOR=$(($SLAVES - 1))

echo Shard Factor: $SHARD_FACTOR
echo Genomic Collections to use: $@

# Run
$SPARK_HOME/bin/spark-submit --name "spark_blastdb" --master ${MASTER:-local} spark_blastdb.py $SHARD_FACTOR $@
