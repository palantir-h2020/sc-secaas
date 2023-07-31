#sudo docker build -t wireguard_server .
FROM jrei/systemd-ubuntu:20.04

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
RUN apt-get install wireguard -y
RUN pip install ops
RUN apt-get install dnsutils -y #command dig
RUN apt-get install iproute2 -y
RUN apt-get install iptables -y
RUN pip install psutil
RUN touch /etc/wireguard/wg0.conf
RUN apt-get update -y
RUN apt-get upgrade -y

CMD ["/usr/sbin/init"]
