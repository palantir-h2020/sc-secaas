FROM ubuntu:20.04
#RUN dnf clean all && rm -r /var/cache/dnf  && dnf upgrade -y && dnf update -y
#RUN git clone https://gitlab.com/palantir-project/ti-re
ENV DEBIAN_FRONTEND=noninteractive
COPY ./fprobe /etc/default/fprobe
RUN apt-get -y update && apt-get -y install python3 python3-pip fprobe iptables wget
RUN apt-get -y install ulogd2
RUN apt-get -y install traceroute iputils-ping iproute2
RUN apt-get -y install openssh-server
COPY ./ulogd.conf /etc/ulogd.conf
RUN service ulogd2 restart
WORKDIR /opt/filebeat
RUN wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.13.3-amd64.deb
RUN dpkg -i filebeat-7.13.3-amd64.deb
COPY ./filebeat.yml /etc/filebeat/filebeat.yml
RUN filebeat modules enable iptables
