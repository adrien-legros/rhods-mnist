FROM image-registry.openshift-image-registry.svc:5000/redhat-ods-applications/minimal-gpu:py3.8-cuda-11.4.2-2

USER 0

WORKDIR /opt/app-root/bin

# Copying custom packages
COPY utils utils/
COPY requirements.txt start-notebook.sh ./

# Streamlit extension installation
COPY streamlit-launcher.sh ./
COPY streamlit-menu/dist/jupyterlab_streamlit_menu-0.1.0-py3-none-any.whl ./

# Copy Elyra setup to utils so that it's sourced at startup
COPY setup-elyra.sh ./utils/

RUN chmod +x /opt/app-root/bin/start-notebook.sh && \
    chmod +x /opt/app-root/bin/utils/process.sh

USER 1001

# Install packages and cleanup
# (all commands are chained to minimize layer size)
RUN echo "Installing softwares and packages" && \
    # Install Python packages \
    pip install -r requirements.txt && \
    pip install --no-cache-dir ./jupyterlab_streamlit_menu-0.1.0-py3-none-any.whl && \
    rm -f ./jupyterlab_streamlit_menu-0.1.0-py3-none-any.whl && \
    # Remove Elyra logo from JupyterLab because this is not a pure Elyra image \
    sed -i "s/widget\.id === \x27jp-MainLogo\x27/widget\.id === \x27jp-MainLogo\x27 \&\& false/" /opt/app-root/share/jupyter/labextensions/@elyra/theme-extension/static/lib_index_js.*.js && \
    # Remove default Elyra runtime-images \
    rm /opt/app-root/share/jupyter/metadata/runtime-images/*.json && \
    # Fix permissions to support pip in Openshift environments \
    chmod -R g+w /opt/app-root/lib/python3.8/site-packages && \
    fix-permissions /opt/app-root -P

# Copy Elyra runtime-images definitions and set the version
COPY runtime-images/ /opt/app-root/share/jupyter/metadata/runtime-images/
RUN sed -i "s/RELEASE/${RELEASE}/" /opt/app-root/share/jupyter/metadata/runtime-images/*.json 

WORKDIR /opt/app-root/src

ENTRYPOINT ["start-notebook.sh"]