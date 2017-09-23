FROM python:2.7-alpine3.6
RUN \
    apk update && apk upgrade && \

    # install gcc g++ unixodbc-dev
    apk --no-cache add gcc g++ unixodbc-dev && \

    # clear after installation
    rm -rf /var/cache/apk/* && \

    pip install pyodbc pyyaml && \

    /bin/sh -c 'echo "[SQL Server]" | tee -i /etc/odbcinst.ini' && \
    /bin/sh -c 'echo "Description=SQL Server via FreeTDS" | tee -i /etc/odbcinst.ini' && \
    /bin/sh -c 'echo "Driver=/usr/lib/libtdsodbc.so.0.0.0" | tee -i /etc/odbcinst.ini'

WORKDIR /user/src/wwi
COPY src .

