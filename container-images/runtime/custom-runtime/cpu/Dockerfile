FROM quay.io/modh/runtime-images@sha256:910e0eef949fd853aa4b67cf17e0545c14252cafab7be1a2f648a1108bf0276b 

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
