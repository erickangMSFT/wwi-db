FROM python:2.7-alpine3.6 
RUN apk add --no-cache gcc g++ libc-dev unixodbc-dev && pip install pyodbc pyyaml

WORKDIR /user/src/wwi
COPY ./src .

CMD tail -f /dev/null
