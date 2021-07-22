FROM python:3.8-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql \
  && apt-get clean
RUN apt-get install libpq-dev
# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

# CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
CMD gunicorn main:app  -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

