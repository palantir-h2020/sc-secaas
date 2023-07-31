#sudo docker build -t ntopng_server .
FROM ubuntu:20.04

#Avoid the warning debconf: delaying package configuration, since apt-utils is not installed
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NOWARNINGS="yes"

RUN set -xe \
    && apt-get update \
    && apt-get install python3-pip -y
RUN apt-get update && apt-get install -y --no-install-recommends \
    init

RUN apt-get install --reinstall systemd -y

RUN pip install --upgrade pip
RUN apt-get install wget gnupg software-properties-common -y
RUN wget https://packages.ntop.org/apt/20.04/all/apt-ntop.deb
RUN dpkg -i apt-ntop.deb
RUN apt-get update -y
RUN apt-get install pfring-dkms nprobe ntopng n2disk cento -y

RUN python3 -m pip install ntopng==5.5.230127  
RUN python3 -m pip install ops
RUN python3 -m pip install psutil
RUN python3 -m pip install Flask
RUN apt-get install rrdtool -y
RUN rm apt-ntop.deb

RUN mkdir API
COPY app.py API/

RUN apt-get update -y
RUN apt-get upgrade -y

ENTRYPOINT ["python3"]
CMD ["API/app.py"]
