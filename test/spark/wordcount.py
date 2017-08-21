from __future__ import print_function

import sys
from operator import add
import requests
from sparkjobserver.api import SparkJob, build_problems

from pyspark.sql import SparkSession

class WordCountSparkJob(SparkJob):

    def validate(self, context, runtime, config):
        print("validate")

    def run_job(self, context, runtime, data):
        return context.parallelize(["hi", "there", "hi", "there", "dolly"]).countByValue()
        #self.main()


    def main(self):
        # get the data
        #url = "https://wdc.objectstorage.softlayer.net/v1/AUTH_580704c6-c8ed-4329-8bcf-41ed080ccf5d/ttc"
        url = "http://5D039.http.wdc01.cdn.softlayer.net/ttc/ttc.txt"
        response = requests.get(url, stream=True)
        #response.raise_for_status()

        # save the data
        with open('/data/test/ttc.txt', 'wb') as handle:
            for block in response.iter_content(1024):
                handle.write(block)

        spark = SparkSession\
            .builder\
            .appName("PythonWordCount")\
            .getOrCreate()

        lines = spark.read.text("file:///data/test/ttc.txt").rdd.map(lambda r: r[0])
        counts = lines.flatMap(lambda x: x.split(' ')) \
                      .map(lambda x: (x, 1)) \
                      .reduceByKey(add)
        output = counts.collect()
        for (word, count) in output:
            print("%s: %i" % (word.encode('utf-8'), count))

        spark.stop()


