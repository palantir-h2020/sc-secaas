FROM linton/docker-snort
RUN apt update -y
RUN apt upgrade -y
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt update -y
RUN apt install -y openjdk-11-jre nano

RUN echo 'alert icmp any any -> any any (msg:"Pinging...";sid:1000004;)' > /etc/snort/rules/local.rules

WORKDIR /opt/kafka
RUN wget https://downloads.apache.org/kafka/2.8.0/kafka_2.13-2.8.0.tgz
RUN tar zxvf kafka_2.13-2.8.0.tgz 
WORKDIR /opt/

ENV PATH=/opt/kafka/kafka_2.13-2.8.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

WORKDIR /opt/filebeat
RUN wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.13.3-amd64.deb
RUN dpkg -i filebeat-7.13.3-amd64.deb
COPY ./filebeat.yml /etc/filebeat/filebeat.yml
RUN filebeat modules enable snort
