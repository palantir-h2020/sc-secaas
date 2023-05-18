FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install python3 python3-pip wget -y
RUN apt-get install gcc openssl libssl-dev bison flex libdnet autoconf libtool -y
RUN apt-get install libpcap-dev -y
RUN apt-get install libnghttp2-dev -y
RUN apt-get install libdumbnet-dev -y
RUN apt-get install libpcre3-dev zlib1g-dev libluajit-5.1-dev -y

RUN wget https://www.snort.org/downloads/snort/daq-2.0.7.tar.gz
RUN wget https://www.snort.org/downloads/snort/snort-2.9.20.tar.gz

RUN tar xvzf daq-2.0.7.tar.gz
RUN tar xvzf snort-2.9.20.tar.gz

WORKDIR /daq-2.0.7
RUN autoreconf -f -i
RUN ./configure && make && make install

WORKDIR /snort-2.9.20
RUN ./configure --enable-sourcefire && make && make install

RUN ldconfig
RUN ln -s /usr/local/bin/snort /usr/sbin/snort
RUN mkdir -p /etc/snort/rules
RUN mkdir /var/log/snort
RUN mkdir /usr/local/lib/snort_dynamicrules
RUN touch /etc/snort/rules/white_list.rules
RUN touch /etc/snort/rules/black_list.rules
RUN touch /etc/snort/rules/local.rules
RUN cp etc/*.conf* /etc/snort
RUN cp etc/*.map /etc/snort

RUN alias python=python3

WORKDIR /opt/filebeat
RUN wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.13.3-amd64.deb
RUN dpkg -i filebeat-7.13.3-amd64.deb
COPY ./filebeat.yml /etc/filebeat/filebeat.yml
#COPY ./portscanning.rules /etc/snort/rules/local.rules
#RUN rm /etc/snort/snort.conf
#COPY ./snort.conf /etc/snort/snort.conf
COPY ./etc /etc/snort/etc/
COPY ./preproc_rules /etc/snort/preproc_rules/
COPY ./so_rules /etc/snort/so_rules/
COPY ./rules /etc/snort/rules/
COPY ./portscanning.rules /etc/snort/rules/local.rules
RUN filebeat modules enable snort
WORKDIR /home

#Install ntap_collector
RUN apt-get install software-properties-common wget apt-utils -y
RUN add-apt-repository universe
RUN wget https://packages.ntop.org/apt/22.04/all/apt-ntop.deb
RUN apt install ./apt-ntop.deb
RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt-get update -y
RUN apt-get install ntap -y
