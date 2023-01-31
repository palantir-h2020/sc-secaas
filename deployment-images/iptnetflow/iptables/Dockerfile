FROM ubuntu:20.04
#RUN dnf clean all && rm -r /var/cache/dnf  && dnf upgrade -y && dnf update -y
#RUN git clone https://gitlab.com/palantir-project/ti-re
ENV DEBIAN_FRONTEND=noninteractive
COPY ./fprobe /etc/default/fprobe
RUN apt-get -y update && apt-get -y install python3 python3-pip fprobe iptables wget software-properties-common net-tools nano
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
RUN apt-get install softflowd -y

#Install Zeek
WORKDIR /zeeklogs
RUN apt-get -y install curl
RUN echo 'deb http://download.opensuse.org/repositories/security:/zeek/xUbuntu_20.04/ /' | tee /etc/apt/sources.list.d/security:zeek.list
RUN curl -fsSL https://download.opensuse.org/repositories/security:zeek/xUbuntu_20.04/Release.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/security_zeek.gpg > /dev/null
RUN apt-get -y update
RUN apt-get -y install zeek
ENV PATH $PATH:/opt/zeek/bin

#Install Ntap
RUN add-apt-repository universe
RUN wget https://packages.ntop.org/apt/22.04/all/apt-ntop.deb
RUN apt install ./apt-ntop.deb
RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y ntap
