#!/bin/bash

#creates namespace and secret with docker registry credentails
kubectl apply -f kubernetes/utils.yaml

#creates configmap for external configs
kubectl apply -f kubernetes/configmap.yaml

#creates deployment
kubectl apply -f kubernetes/deploy.yaml

#creates service to expose the deployment
kubectl apply -f kubernetes/service.yaml
