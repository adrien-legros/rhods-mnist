FROM quay.io/opendatahub-contrib/runtime-images:minimal-ubi8-py38_2023b_latest

USER 0

WORKDIR /opt/app-root/bin

COPY requirements.txt ./

# Install packages and cleanup
# (all commands are chained to minimize layer size)
RUN echo "Installing softwares and packages" && \
    # Install Python packages \
    pip install -r requirements.txt && \
    # Fix permissions to support pip in Openshift environments \
    chmod -R g+w /opt/app-root/lib/python3.8/site-packages && \
    fix-permissions /opt/app-root -P

USER 1001

WORKDIR /opt/app-root/src