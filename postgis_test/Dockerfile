FROM mdillon/postgis

ADD https://github.com/ohmu/pghoard/archive/1.2.0.tar.gz pghoard.tar.gz
RUN tar xzf pghoard.tar.gz
RUN apt-get update && apt-get install -y \
  python3 \
  python3-dev \
  python3-pip \
  libsnappy-dev \
  postgresql-server-dev-9.5 \
  libffi-dev
RUN python3 pghoard-1.2.0/setup.py bdist_egg
RUN easy_install3 pghoard-1.2.0/dist/pghoard-1.2.0-py3.4.egg
RUN pip3 install boto httplib2 google-api-python-client
RUN mkdir /backups

COPY ./docker-entrypoint.sh /
