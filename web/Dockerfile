FROM python:2.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y gdal-bin

RUN curl -LO http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
RUN bash Miniconda-latest-Linux-x86_64.sh -p /miniconda -b
RUN rm Miniconda-latest-Linux-x86_64.sh
ENV PATH=/miniconda/bin:${PATH}
RUN conda update -y conda

RUN conda install -y\
    numpy \
    matplotlib \
    pandas \
    scipy \
    seaborn \
    gunicorn

COPY requirements/ /usr/src/app/requirements/
RUN pip install --no-cache-dir -r requirements/core.txt



COPY . /usr/src/app
