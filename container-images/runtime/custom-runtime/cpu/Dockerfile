FROM quay.io/modh/runtime-images@sha256:de57a9c7bd6a870697d27ba0af4e3ee5dc2a2ab05f46885791bce2bffb77342d

USER 0

WORKDIR /opt/app-root/bin

COPY requirements.txt ./

# Install packages and cleanup
# (all commands are chained to minimize layer size)
RUN echo "Installing softwares and packages" && \
    # Install Python packages \
    pip install -r requirements.txt

USER 1001

WORKDIR /opt/app-root/src
