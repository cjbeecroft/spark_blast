#
######################################################################
# Environment settings
######################################################################


######################################################################
#        _     _           _         _
#   ___ | |__ (_) ___  ___| |_   ___| |_ ___  _ __ ___
#  / _ \| '_ \| |/ _ \/ __| __| / __| __/ _ \| '__/ _ \
# | (_) | |_) | |  __/ (__| |_  \__ \ || (_) | | |  __/
#  \___/|_.__// |\___|\___|\__| |___/\__\___/|_|  \___|
#           |__/
######################################################################

# Set the swift object store credentials
export ST_USER="SLO..."
export ST_KEY="748..."
export ST_AUTH="https://sjc01.objectstorage.service.networklayer.com/auth/v1.0"

# Specify if the query file is to be transferred via the object store (1)
# otherwise (value 0 or unset) it is assumed that the file is visible to
# all of the workers (via a shared file system or pre-copied to each node)
export COPY_FILE_TO_OBJECT_STORE=1


######################################################################
#                       _           _           _
#  ___ _ __   __ _ _ __| | __   ___| |_   _ ___| |_ ___ _ __
# / __| '_ \ / _` | '__| |/ /  / __| | | | / __| __/ _ \ '__|
# \__ \ |_) | (_| | |  |   <  | (__| | |_| \__ \ ||  __/ |
# |___/ .__/ \__,_|_|  |_|\_\  \___|_|\__,_|___/\__\___|_|
#     |_|
######################################################################

export MASTER="spark://`hostname -f`:7077"

# Set the partition factor to cluster size - 1.  This assumes
# that .../conf/slaves has no extra lines
SLAVES=`wc -l $SPARK_HOME/conf/slaves | cut -d" " -f1`
export TASKS_TO_USE=$(($SLAVES - 1))


######################################################################
#  _     _           _              _   _   _
# | |__ | | __ _ ___| |_   ___  ___| |_| |_(_)_ __   __ _ ___
# | '_ \| |/ _` / __| __| / __|/ _ \ __| __| | '_ \ / _` / __|
# | |_) | | (_| \__ \ |_  \__ \  __/ |_| |_| | | | | (_| \__ \
# |_.__/|_|\__,_|___/\__| |___/\___|\__|\__|_|_| |_|\__, |___/
#                                                   |___/
######################################################################

# This will set the number of cores blast will use along
# with telling spark each task needs this many cores
export CORES_TO_USE=2
export MAX_FILE_SIZE=2GB

# Location of blastn and makeblastdb that is accesible to all nodes
# setting these will prevent blast from being copied over
#export BLASTN=
#export MAKEBLASTDB=
