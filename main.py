from flask import Flask,Response
import requests
from prometheus_client import start_http_server, Histogram,  generate_latest,Summary,Info,Counter,Gauge
import config.config as cfg
import logging
import json

app = Flask(__name__)

## metrics for Prometheus
metrics = {}
metrics['response_time']=Gauge('sample_external_url_response_ms', 'Response Time of the url',['url'])
metrics['status']=Gauge('sample_external_url_up', 'Status of the url',['url'])

REQUEST_TIMEOUT_SECONDS=cfg.request_timeout_in_seconds

@app.route('/queryurl')
def checkurl():
    logging.info("Query url function.")
    ## reading config from config/config.py
    urls=cfg.urls
    response_hash={}
    response_hash['status']='ok'
    response_hash['response']={}
    for url in urls:
        try:
            logging.info("Querying url "+ url )
            response=requests.get(url,timeout=REQUEST_TIMEOUT_SECONDS)
            response_time_in_ms=response.elapsed.total_seconds()*1000
            if response.ok:
                logging.info( url + " url responded successfully.")
                response_hash['response'][url]={}
                response_hash['response'][url]['status_code']=response.status_code
                response_hash['response'][url]['up']=1
                response_hash['response'][url]['response_time_in_ms']=response_time_in_ms
                metrics['status'].labels(url).set(1)
                metrics['response_time'].labels(url).set(response_time_in_ms)
            else:
                logging.info( url + " responded with unhealthy response code.")
                response_hash['response'][url]={}
                response_hash['response'][url]['status_code']=response.status_code
                response_hash['response'][url]['up']=0
                response_hash['response'][url]['response_time_in_ms']=response_time_in_ms
                metrics['status'].labels(url).set(0)
                metrics['response_time'].labels(url).set(response_time_in_ms)
        except requests.Timeout as ex:
            logging.warning("Request timedout after " + str(REQUEST_TIMEOUT_SECONDS)+" seconds!")
            response_time_in_ms=REQUEST_TIMEOUT_SECONDS*1000
            response_hash['response'][url]={}
            response_hash['response'][url]['status_code']=503
            response_hash['response'][url]['up']=0
            response_hash['response'][url]['response_time_in_ms']=response_time_in_ms
            metrics['status'].labels(url).set(0)
            metrics['response_time'].labels(url).set(response_time_in_ms)
        except Exception as ex:
            logging.warning("Something went wrong!")
            logging.warning(ex)

    response_json=json.dumps(response_hash)
    return json.loads(response_json)

@app.route("/metrics")
def requests_count():
    logging.info("metrics function.")
    res = []
    for k,v in metrics.items():
        res.append(generate_latest(v))
    return Response(res, mimetype="text/plain")

@app.route('/healthcheck')
def healthcheck():
    logging.info("healthcheck function.")
    return_json={"app_name":"query_url","app_status":"ok"}
    return return_json

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
