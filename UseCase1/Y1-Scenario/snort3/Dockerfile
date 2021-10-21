FROM centos
RUN	yum update -y
RUN	dnf group install -y "Development Tools"
RUN dnf install epel-release -y
RUN	yum update -y
#can be deleted? 
RUN	yum install -y yum-utils nano 

# Required packages
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
RUN	yum install -y dnf-plugins-core
RUN	yum config-manager --set-enabled powertools
RUN	dnf -y --enablerepo=powertools install texinfo
RUN dnf clean all
RUN dnf update
RUN dnf upgrade
RUN echo -e "/usr/local/lib\n/usr/local/lib64" > /etc/ld.so.conf.d/local.conf
RUN ldconfig
RUN dnf install -y libnfnetlink-devel libnetfilter_queue-devel
RUN dnf install -y flex bison gcc gcc-c++ make cmake automake autoconf libtool libpcap
RUN dnf install -y libpcap-devel pcre-devel libdnet-devel hwloc-devel openssl-devel zlib-devel luajit-devel pkgconf libmnl-devel libunwind-devel
RUN ldconfig

WORKDIR /snort
RUN git clone https://github.com/snort3/libdaq.git
WORKDIR /snort/libdaq
RUN	./bootstrap
RUN	./configure
RUN	make
RUN	make install

RUN ldconfig
RUN dnf install -y xz-devel libuuid-devel
RUN dnf install -y hyperscan hyperscan-devel
RUN ldconfig

WORKDIR /snort
RUN	git clone https://github.com/google/flatbuffers.git
WORKDIR /snort/flatbuffers
RUN mkdir /snort/flatbuffers/fb-build
WORKDIR /snort/flatbuffers/fb-build
RUN cmake ../
RUN make -j$(nproc)
RUN make -j$(nproc) install 
RUN ldconfig

RUN dnf install -y libsafec libsafec-devel
RUN ln -s /usr/lib64/pkgconfig/safec-3.3.pc /usr/lib64/pkgconfig/libsafec.pc
RUN dnf install -y gperftools-devel

# Download, compile and install Snort3
WORKDIR /snort
RUN	git clone https://github.com/snort3/snort3.git
WORKDIR	/snort/snort3
ENV PKG_CONFIG_PATH=/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH
ENV PKG_CONFIG_PATH=/usr/local/lib64/pkgconfig:$PKG_CONFIG_PATH
ENV CFLAGS="-O3"
ENV CXXFLAGS="-O3 -fno-rtti"
RUN ./configure_cmake.sh --prefix=/usr/local/snort --enable-tcmalloc
WORKDIR /snort/snort3/build/
RUN make -j$(nproc)
RUN make -j$(nproc) install
RUN /usr/local/snort/bin/snort -v

# Download, compile and install Snort3 Extra
WORKDIR /snort
RUN git clone https://github.com/snort3/snort3_extra.git
WORKDIR /snort/snort3_extra
ENV PKG_CONFIG_PATH=/usr/local/snort/lib64/pkgconfig:$PKG_CONFIG_PATH
RUN ./configure_cmake.sh --prefix=/usr/local/snort/extra
WORKDIR /snort/snort3_extra/build
RUN make -j$(nproc)
RUN make -j$(nproc) install 

# Installing symlink to execute snort
RUN ln -sf /usr/local/snort/bin/snort /usr/local/bin/snort

# Snort configuration
RUN mkdir -p /usr/local/snort/{builtin_rules,rules,appid,intel}

WORKDIR /snort
RUN curl -Lo /snort/snort-community-rules.tar.gz https://www.snort.org/downloads/community/snort3-community-rules.tar.gz
RUN tar zxvf /snort/snort-community-rules.tar.gz --directory /snort
RUN cp /snort/snort3-community-rules/snort3-community.rules /usr/local/snort/rules/

RUN curl -Lo /snort/ip-blocklist https://www.talosintelligence.com/documents/ip-blacklist
RUN cp /snort/ip-blocklist /usr/local/snort/intel/
RUN touch /usr/local/snort/intel/ip-allowlist

COPY ./snort_defaults.lua /usr/local/snort/etc/snort/snort_defaults.lua
COPY ./snort.lua /usr/local/snort/etc/snort/snort.lua
RUN touch /var/log/snort
WORKDIR /

RUN rm -rf /snort