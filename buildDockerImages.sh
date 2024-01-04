#!/bin/bash

yes | docker system prune -a
docker build -t hadoop-image -f Hadoop.Dockerfile .
docker images