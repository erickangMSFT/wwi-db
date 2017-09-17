FROM ericskang/sqltools:sqlcmd

RUN apt-get update && apt-get install -y  python python-pip && apt clean && pip install --upgrade pip && pip install pyodbc pyyaml

WORKDIR /user/src/wwi
COPY src .

CMD tail -f /dev/null
