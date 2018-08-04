FROM resin/rpi-raspbian:stretch

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install \
  python \
  python-dev \
  python-serial \
  python-setuptools \
  python-virtualenv \
  --no-install-recommends

RUN apt-get -y install git nano jed

RUN cd /tmp

RUN git clone https://github.com/tuomassalo/ib.victron   && cd ib.victron && python setup.py install
RUN git clone https://github.com/fishpepper/pyUSBtin.git && cd pyUSBtin   && python setup.py install

# RUN pip install pyserial

# *.py and forever.sh
# COPY bridge-scripts /opt/shared-dir/

# RUN chmod a+x /opt/shared-dir/forever.sh

RUN /bin/bash
