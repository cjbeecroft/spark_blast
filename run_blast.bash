#!

######################################################################
#                       _     _           _
#  _ __ _   _ _ __     | |__ | | __ _ ___| |_
# | '__| | | | '_ \    | '_ \| |/ _` / __| __|
# | |  | |_| | | | |   | |_) | | (_| \__ \ |_
# |_|   \__,_|_| |_|___|_.__/|_|\__,_|___/\__|
#                 |_____|
######################################################################

# Review our environment
echo Master: $MASTER
echo ST_USER: $ST_USER
echo ST_KEY: $ST_KEY
echo ST_AUTH: $ST_AUTH

echo DB partition factor: $TASKS_TO_USE
echo Genomic collections to use: $@

# Run
$SPARK_HOME/bin/spark-submit --conf "spark.task.cpus=${CORES_TO_USE:-1}" --name "spark_blast" --master ${MASTER:-local} spark_blast.py $@
