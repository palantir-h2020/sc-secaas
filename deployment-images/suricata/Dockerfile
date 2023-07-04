FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install software-properties-common wget apt-transport-https net-tools apt-utils -y
RUN add-apt-repository universe
RUN wget https://packages.ntop.org/apt/22.04/all/apt-ntop.deb
RUN apt install ./apt-ntop.deb
RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt-get update -y
#RUN apt-get upgrade -y
RUN apt-get install ntap -y
RUN apt-get install -y openjdk-11-jre nano iproute2

WORKDIR /opt/filebeat
RUN wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.13.3-amd64.deb
RUN dpkg -i filebeat-7.13.3-amd64.deb
COPY ./filebeat.yml /etc/filebeat/filebeat.yml
RUN filebeat modules enable suricata

WORKDIR /home
RUN add-apt-repository -y ppa:oisf/suricata-stable
RUN apt-get install -y suricata
RUN suricata-update
COPY ./suricata.yaml /etc/suricata/suricata.yaml
COPY ./local.rules /etc/suricata/rules/local.rules
