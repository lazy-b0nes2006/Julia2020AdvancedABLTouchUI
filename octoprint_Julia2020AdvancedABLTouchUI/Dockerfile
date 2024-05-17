FROM ubuntu:18.04

# Update package lists and install necessary dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-dev \
    python3-pip \
    wget \
    qt4-dev-tools \
    qt4-qmake \
    libqt4-dev \
    libqtcore4 \
    && apt-get clean

# Install SIP
RUN pip3 install sip

# Copy PyQt4 source files to the Docker image
COPY PyQt4_gpl_x11-4.12.3 /PyQt4_gpl_x11-4.12.3

# Change directory to the PyQt4 source directory and run configuration, make, and make install
RUN cd /PyQt4_gpl_x11-4.12.3 && \
    python3 configure-ng.py && \
    make && \
    make install

