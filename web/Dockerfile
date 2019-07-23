FROM python:3.6@sha256:715c905479b18933f54c92feb247d6ed64509c6adc9b64989fc041d597ed94b4

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    gdal-bin


COPY requirements/ /usr/src/app/requirements/
RUN pip install --no-cache-dir -r requirements/develop.txt

COPY . /usr/src/app
