FROM python:3.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    gdal-bin


COPY requirements/ /usr/src/app/requirements/
RUN pip install --no-cache-dir -r requirements/develop.txt

COPY . /usr/src/app
