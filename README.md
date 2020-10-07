# python-prometheus

<!-- TOC START min:3 max:5 link:true update:true -->
- [Requirements](#requirements)
- [Design](#design)
 - [Unit Tests](#unit-tests)
- [Build](#build)
- [Deploy](#deploy)
  - [External Configs](#external-configs)
- [Application Usage](#application-usage)
<!-- TOC END -->

This project runs an application which queries status of specified urls and is written in Python.

## Requirements

Run the application on http server which queries status of specified urls and these metrics are output to /metrics endpoint

## Design

This application is written in Python using [Flask](https://flask.palletsprojects.com/en/1.1.x/) framework. The application can be accessed at ```<application-url>/queryurl``` and the metrics can be accessed at  ```<application-url>/metrics```. A docker image is built to run the application as container, the project also includes deployment scripts to run the application on Kubernetes. As part of design, I have considered to have a timeout of 30s which is part of external configuration and can be adjusted as needed. The application has a background job which can be set to run at desired interval to query the urls periodically.
  
### Unit Tests
Unit Tests are written in file ``` python-prometheus/unit_tests.py ```. With http server running, execute this file to run unit tests.

```bash
$ python unit_tests.py
..
----------------------------------------------------------------------
Ran 2 tests in 184.769s

OK
```

## Build

Please make sure docker is installed for below steps to work.

Steps for docker build.
```bash
$ cd python-prometheus/
$ cat ~/GH_TOKEN.txt | docker login docker.pkg.github.com -u <username> --password-stdin 
$ docker build -t query-url:<version> .
$ docker tag <IMAGE_ID> docker.pkg.github.com/<username>/<project-name>/query-url:<VERSION>
$ docker push docker.pkg.github.com/<username>/<project-name>/query-url:<VERSION>
```

Please replace username, project-name, IMAGE_ID and VERSION with appropriate values.

## Deploy

This application can be hosted on kubernetes. 

These softwares need to be installed on the host for deploying the application.
- [Docker](https://www.docker.com/)
- [kubernetes](https://kubernetes.io/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)

### External Configs

This application takes the configurations from config/config.py

```bash
$ cat python-prometheus/config/config.py
urls=["https://httpstat.us/503", "https://httpstat.us/200"]
request_timeout_in_seconds=30
query_interval_in_seconds=300
log_level="INFO"
```
Each configuration purpose and expected values are describe below:

<table>
  <tr>
    <th>Config Key</th>
    <th>Purpose</th>
    <th>Data type</th>
    <th>Expected Value</th>
  </tr>
  <tr>
    <td>urls</td>
    <td>All the urls to be queried</td>
    <td>List(containing urls)</td>
    <td>["https://httpstat.us/503", "https://httpstat.us/200"] (addidtional urls can be added as needed)</td>
  </tr>
  <tr>
    <td>request_timeout_in_seconds</td>
    <td>This config is to time out requesting an url after the mentioned seconds</td>
    <td>Integer</td>
    <td>30(or as per need)</td>
  </tr>
 <tr>
    <td>query_interval_in_seconds</td>
    <td>This config is to periodically run the function which querying urls after the mentioned seconds</td>
    <td>Integer</td>
    <td>300(or as per need)</td>
  </tr>
 <tr>
    <td>log_level</td>
    <td>To control log level</td>
    <td>String</td>
    <td>one of DEBUG, INFO, WARNING, ERROR, CRITICAL</td>
  </tr>
</table>

Steps to deploy
```bash
$ cd python-prometheus/
$ sh deploy.sh 
```

Above deploy scripts creates:
- New namespace called query-url on k8s cluster. All the resources are created inside this namespace( so it can be easier ti delete everything related to this application in one shot)
- ConfigMap called query-url-config. This contains the queries that the application queries. In case we need to add more urls, we can update the configmap and restart deployment.
- Secret called git-reg-cred which had READ packages token to download docker image from Github.
- Deployment called query-url. This uses the configmap and secret that are created above. configmap is mounted as a volume. It also contains readinessProbe to check the container health before it is ready to requests.
- Service called query-url-service which exposes query-url deployment at port 32000 on Node and at 8080 inside the cluster.

When the deployment is complete the resources on k8s cluster should look something like this:

<img src="images/k8s_resources.PNG" height="250">

### Adding the application endpoints to Prometheus
The pods running the application are deployed with below annaotations.

```bash
  annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
```
So Prometheus(that's setup on the same k8s cluster) will start scraping metrics when the pods are created.

## Application Usage
The application can be accessed at ```<application-url>/queryurl``` and the metrics can be accessed at ```<application-url>/metrics``` .
  
A sample of /queryurl and /metrics can be seen here:


Screenshot of metrics on Prometheus:

Screenshot of metrics on Grafana:
