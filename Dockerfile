FROM debian:bullseye-slim

# Don't buffer stdout and stderr as it breaks realtime logging
ENV PYTHONUNBUFFERED 1

# Create an unprivileged user to run the application process
ENV AUTO_VPA_UID 1001
ENV AUTO_VPA_USER auto-vpa
RUN useradd \
      --no-create-home \
      --user-group \
      --shell /sbin/nologin \
      --uid $AUTO_VPA_UID \
      $AUTO_VPA_USER

# Install tini, which we will use to marshal the processes, and Python
RUN apt-get update && \
    apt-get install -y git python3 python3-pip tini && \
    rm -rf /var/lib/apt/lists/*

# Installing dependencies separately ensures better use of the build cache
COPY requirements.txt /opt/auto-vpa/
RUN pip3 install --no-deps --requirement /opt/auto-vpa/requirements.txt

COPY . /opt/auto-vpa
RUN pip3 install --no-deps -e /opt/auto-vpa

USER $AUTO_VPA_UID
ENTRYPOINT ["/usr/bin/tini", "-g", "--"]
CMD ["kopf", "run", "--module", "auto_vpa", "--all-namespaces"]
