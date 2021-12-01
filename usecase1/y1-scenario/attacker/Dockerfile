FROM debian
RUN apt update -y
RUN apt upgrade -y 
RUN apt install -y nmap nano wget gnupg apt-transport-https openjdk-11-jre build-essential git libssl-dev autoconf automake libpcap-dev libpcap0.8 libpcap0.8-dev tcl tcl-dev man
COPY ./init.sh /root/init.sh

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
