FROM python:3.7 

COPY . /src/pysdd/

RUN  pip install cysignals numpy cython && \
     cd /src/pysdd && \
     make build && \
     python setup.py install && \
     cd /src && \
     rm -rf pysdd

WORKDIR /src

CMD /bin/bash

