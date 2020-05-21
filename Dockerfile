FROM ubuntu:latest

RUN echo "deb http://archive.canonical.com/ubuntu bionic partner" >> /etc/apt/sources.list

RUN apt update
RUN apt install python3-pip -y

RUN pip3 install flask
RUN pip3 install psycopg2-binary

COPY main.py /home/main.py

CMD python3 /home/main.py
