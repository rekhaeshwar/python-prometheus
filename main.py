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

def construct_url_response(url,status_code,status_up,response_time_in_ms):
    logging.info("constructing response per url" )
    response_hash={}
    response_hash['status_code']=status_code
    response_hash['up']=status_up
    response_hash['response_time_in_ms']=response_time_in_ms
    metrics['status'].labels(url).set(status_up)
    metrics['response_time'].labels(url).set(response_time_in_ms)
    return response_hash

@app.route('/queryurl')
def checkurl():
    logging.info("Query url function.")

    ## reading config from config/config.py
    urls=cfg.urls
    result={}
    result['response']={}
    for url in urls:
        try:
            logging.info("Querying url "+ url )
            response=requests.get(url,timeout=REQUEST_TIMEOUT_SECONDS)
            response_time_in_ms=response.elapsed.total_seconds()*1000
            if response.ok:
                logging.info( url + " url responded successfully.")
                result['response'][url]=construct_url_response(url,response.status_code,1,response_time_in_ms)
            else:
                logging.info( url + " responded with unhealthy response code.")
                result['response'][url]=construct_url_response(url,response.status_code,0,response_time_in_ms)
        except requests.Timeout as ex:
            logging.warning("Request timedout after " + str(REQUEST_TIMEOUT_SECONDS)+" seconds!")
            response_time_in_ms=REQUEST_TIMEOUT_SECONDS*1000
            result['response'][url]=construct_url_response(url,503,0,response_time_in_ms)
        except Exception as ex:
            logging.warning("Something went wrong!")
            logging.warning(ex)
            result['response'][url]={"message":"Exception occured"}
    result['status']='ok'
    return json.dumps(result)

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
