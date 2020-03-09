FROM ubuntu:latest

RUN echo "deb http://archive.canonical.com/ubuntu bionic partner" >> /etc/apt/sources.list

RUN apt update
RUN apt install python3-pip -y

RUN pip3 install flask

COPY item.py /home/item.py
COPY main.py /home/main.py

CMD python3 /home/main.py
