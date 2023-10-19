FROM registry.redhat.io/rhel8/python-38@sha256:ff413c7793bca66c872667eadef98d77df900b5f24b288f233003e1201956c22

# Add application sources to a directory that the assemble script expects them
# and set permissions so that the container runs without root access
USER 0
ADD app-src /tmp/src
RUN /usr/bin/fix-permissions /tmp/src
USER 1001

# Install the dependencies
RUN /usr/libexec/s2i/assemble

# Set the default command for the resulting image
CMD /usr/libexec/s2i/run