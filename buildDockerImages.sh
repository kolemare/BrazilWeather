#!/bin/bash

yes | docker system prune -a
docker build -t hadoop-image -f Hadoop.dockerfile .
docker build -t loader-hadoop-image -f HadoopLoader.dockerfile .

docker images