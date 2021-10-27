FROM python:3.9

ADD requirements/ /opt/app/requirements

WORKDIR /opt/app

RUN pip install -r requirements/tests.txt
ADD . .

ENTRYPOINT ["sh", "tests/functional/docker-entrypoint.sh"]