FROM python:3-alpine

WORKDIR /opt/redis2LEDs
COPY requirements.txt ./

ADD "https://api.github.com/repos/FF-Woernitz/CAS_lib/git/refs/heads/master" skipcache
RUN pip install --no-cache-dir -r requirements.txt
COPY src .

CMD [ "python3", "-u", "./main.py" ]
