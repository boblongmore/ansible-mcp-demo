ARG VARIANT=3
FROM --platform=linux/amd64 mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

COPY .devcontainer/requirements.txt /tmp/pip-tmp/
COPY .devcontainer/requirements.yml /tmp/ansible-tmp/

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install -y software-properties-common

# Install Dependencies
RUN apt -y install \
    ca-certificates \
    curl \
    gnupg \
    libonig-dev \
    libssh-dev

RUN apt update

# Install Python Packages
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

# Install Ansible Dependencies
USER vscode
RUN ansible-galaxy collection install -r /tmp/ansible-tmp/requirements.yml

USER root
RUN rm -rf /tmp/ansible-tmp
