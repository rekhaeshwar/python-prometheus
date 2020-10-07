from flask import Flask,Response
import requests
from prometheus_client import start_http_server, Histogram,  generate_latest,Summary,Info,Counter,Gauge
import config.config as cfg
import logging
import json
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# setting log level as per config/config.py
log_level=logging.getLevelName(cfg.log_level)
logging.basicConfig(format='%(asctime)s - %(message)s',level=log_level)

app = Flask(__name__)

# metrics for Prometheus
metrics = {}
metrics['response_time']=Gauge('sample_external_url_response_ms', 'Response Time of the url',['url'])
metrics['status']=Gauge('sample_external_url_up', 'Status of the url',['url'])

# reading config from config/config.py
REQUEST_TIMEOUT_SECONDS=cfg.request_timeout_in_seconds
QUERY_INTERVAL_IN_SECONDS=cfg.query_interval_in_seconds

def construct_url_response(url,status_code,status_up,response_time_in_ms):
    logging.info("constructing response for url - " +url)
    response_hash={}
    response_hash['status_code']=status_code
    response_hash['up']=status_up
    response_hash['response_time_in_ms']=response_time_in_ms
    return response_hash

def add_metrics(url,status_up,response_time_in_ms):
    metrics['status'].labels(url).set(status_up)
    metrics['response_time'].labels(url).set(response_time_in_ms)
    return

# endpoint to run url query
@app.route('/queryurl')
def checkurl():
    logging.info("Query url function started.")

    # reading config from config/config.py
    urls=cfg.urls
    result={}
    # uncomment below line to add status to response
    #result['response']={}
    for url in urls:
        try:
            logging.info("Querying url "+ url )
            response=requests.get(url,timeout=REQUEST_TIMEOUT_SECONDS)
            response_time_in_ms=response.elapsed.total_seconds()*1000
            if response.ok:
                logging.info( url + " url responded successfully.")
                # uncomment below line to add url status to response
                #result['response'][url]=construct_url_response(url,response.status_code,1,response_time_in_ms)
                add_metrics(url,1,response_time_in_ms)
            else:
                logging.info( url + " responded with unhealthy response code.")
                # uncomment below line to add url status to response
                #result['response'][url]=construct_url_response(url,response.status_code,0,response_time_in_ms)
                add_metrics(url,0,response_time_in_ms)
        except requests.Timeout as ex:
            logging.warning("Request timed out after " + str(REQUEST_TIMEOUT_SECONDS)+" seconds for url - "+ url)
            response_time_in_ms=REQUEST_TIMEOUT_SECONDS*1000
            # uncomment below line to add url status to response
            #result['response'][url]=construct_url_response(url,503,0,response_time_in_ms)
            add_metrics(url,1,response_time_in_ms)
        except Exception as ex:
            logging.warning("Something went wrong!")
            logging.exception(ex)
            result['response'][url]={"message":"Exception occured"}
    result['status']='ok'
    logging.info("Query url function completed.")
    return json.dumps(result)

@app.route("/metrics")
def requests_count():
    logging.info("metrics function.")
    res = []
    for k,v in metrics.items():
        res.append(generate_latest(v))
    return Response(res, mimetype="text/plain")

# endpoint to monitor health of the application
@app.route('/healthcheck')
def healthcheck():
    logging.info("healthcheck function.")
    return_json={"app_name":"query_url","app_status":"ok"}
    return return_json

# schedule running the query as a background job
scheduler = BackgroundScheduler()
scheduler.add_job(func=checkurl, trigger="interval", seconds=QUERY_INTERVAL_IN_SECONDS)
scheduler.start()

# shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
