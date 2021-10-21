FROM debian
RUN apt update -y
RUN apt upgrade -y 
RUN apt install -y nmap nano wget gnupg apt-transport-https openjdk-11-jre build-essential git libssl-dev autoconf automake libpcap-dev libpcap0.8 libpcap0.8-dev tcl tcl-dev man
COPY ./init.sh /root/init.sh

#WORKDIR /root/attacker 
#RUN wget https://artifacts.elastic.co/GPG-KEY-elasticsearch 
#RUN apt-key add GPG-KEY-elasticsearch 
#COPY ./elastic-7.x.list /etc/apt/sources.list.d/elastic-7.x.list
#RUN apt update -y
#RUN apt install -y filebeat

#COPY ./filebeat.yml /etc/filebeat/filebeat.yml

#RUN update-rc.d filebeat defaults 95 10

WORKDIR /root/kafka
RUN wget https://downloads.apache.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz
RUN tar zxvf kafka_2.13-2.8.0.tgz 
WORKDIR /root/

ENV PATH=/root/kafka/kafka_2.13-2.8.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN git clone https://github.com/shekyan/slowhttptest.git
WORKDIR /root/slowhttptest
RUN ./configure --prefix=/usr/local/
RUN make
RUN make install
WORKDIR /root/


RUN git clone https://github.com/antirez/hping
WORKDIR /root/hping
RUN ./configure
RUN ln -s /usr/include/pcap/bpf.h /usr/include/net/bpf.h
RUN ldconfig
RUN make
RUN make install

WORKDIR /root/