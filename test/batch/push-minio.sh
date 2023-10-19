#!/bin/sh
# Arg1: minio endpoint
mc alias set remote $1 "minio" "minio123"
for img in $(ls ./images | shuf);
do
    mc cp ./images/$img remote/images/$img
    sleep 5
done;