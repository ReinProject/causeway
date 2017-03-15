FROM ubuntu:latest

MAINTAINER Arsen A. Gutsal <a.gutsal@softsky.com.ua>

RUN apt update && apt upgrade -y && apt install git python3-pip sqlite3 -y
RUN pip3 install --upgrade pip

ENV WD /app/causeway
WORKDIR ${WD}
ADD . $WD
RUN pip3 install -r requirements.txt
RUN sqlite3 causeway.db < schema.sql

EXPOSE 8332 2016
COPY default_settings.py settings.py

CMD python3 cserver.py
