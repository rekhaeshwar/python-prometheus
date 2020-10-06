FROM  python:3.6

RUN mkdir /app /app/config
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY main.py /app/main.py

ENTRYPOINT ["/usr/local/bin/python", "/app/main.py"]
