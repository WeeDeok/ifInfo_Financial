FROM ubuntu:20.04

RUN apt update -y
RUN apt-get install python3.10 -y
RUN apt-get install pip -y

RUN pip3 install dash
RUN pip3 install requests
RUN pip3 install plotly
RUN pip3 install pandas
RUN pip3 install matplotlib
RUN pip3 install IPython
