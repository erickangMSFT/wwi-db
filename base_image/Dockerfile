FROM ericskang/sqltools:sqlcmd

RUN apt-get update && apt-get install -y python python-pip \ 
    && apt clean && pip install --upgrade pip \
    && pip install pyodbc pyyaml


