FROM ubuntu:22.04

# install essentials
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        tar \
        wget \
    && rm -rf /var/lib/apt/lists/*


RUN apt-get install -y libcjson-dev

# install gcc compiler
RUN apt-get install -y gcc

# cleanup
WORKDIR /
RUN rm -rf /setup

# command
COPY ./stol_its_coding /
COPY ./stol_its_testing /

RUN gcc -o decode *.c -lcjson
RUN ./decode