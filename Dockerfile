FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip \
  && apt-get install -y mingw-w64 binutils \
  && mkdir -p /usr/src/app/

WORKDIR /fear-engine-CI/
COPY . /fear-engine-CI/

RUN echo "****" \
    && ls \
    && echo "****"
	
