FROM quay.io/opendatahub-contrib/workbench-images:jupyter-datascience-ubi8-py38_2023b_latest

# Copying custom packages
COPY requirements.txt ./

# Install packages and cleanup
# (all commands are chained to minimize layer size)
RUN echo "Installing softwares and packages" && \
    # Install Python packages \
    pip install -r requirements.txt && \
    # Remove default image runtime
    rm /opt/app-root/share/jupyter/metadata/runtime-images/*.json && \
    # Fix permissions to support pip in Openshift environments \
    chmod -R g+w /opt/app-root/lib/python3.8/site-packages && \
    fix-permissions /opt/app-root -P

COPY runtime-images/ /opt/app-root/share/jupyter/metadata/runtime-images/

WORKDIR /opt/app-root/src

ENTRYPOINT ["start-notebook.sh"]