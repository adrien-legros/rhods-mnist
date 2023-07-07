#!/bin/sh
mc alias set remote "https://minio-mnist.apps.cluster-l7lrt.l7lrt.sandbox2852.opentlc.com/" "minio" "minio123"
for img in $(ls ./images | shuf);
do
    mc cp ./images/$img remote/images/$img
    sleep 5
done;