FROM registry.redhat.io/ubi8/python-311:latest

USER 0
ADD src/model.py src/requirements.txt /opt/app-root/src
RUN pip install -r /opt/app-root/src/requirements.txt
USER 1001