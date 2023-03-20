FROM quay.io/minio/mc

RUN curl https://vault.centos.org/centos/8/BaseOS/x86_64/os/Packages/tar-1.30-5.el8.x86_64.rpm -o /tmp/tar.rpm && \
    curl https://vault.centos.org/centos/8/BaseOS/x86_64/os/Packages/unzip-6.0-45.el8_4.x86_64.rpm -o /tmp/unzip.rpm && \
    rpm -i --force /tmp/tar.rpm &&\
    rpm -i --force /tmp/unzip.rpm &&\
    mkdir -m 0777 /.mc

USER 1001

ENTRYPOINT ["/bin/sh"]