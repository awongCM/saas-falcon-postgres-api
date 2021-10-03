FROM python:3.8
LABEL maintainer="Andy Chee Ming Wong <awong.cm@gmail.com>"

WORKDIR /src
COPY . .

RUN pip install -r requirements.txt

WORKDIR app

EXPOSE 5000