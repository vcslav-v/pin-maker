FROM python:3-slim

RUN mkdir -p /usr/src/app/pin_maker

ENV CONTAINER_HOME=/usr/src/app/pin_maker
ENV API_PASSWORD=uE4F3^bh0IPzHI
ENV API_USERNAME=api

ADD . $CONTAINER_HOME
WORKDIR $CONTAINER_HOME

RUN pip install -r requirements.txt
RUN apt update && apt install ffmpeg -y

CMD gunicorn -w 4 -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker pin_maker.main:app

EXPOSE 8000