FROM python:3.8
LABEL maintainer="Andy Chee Ming Wong"

WORKDIR /src/app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000