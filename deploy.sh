#!/bin/bash

#creates namespace and secret with docker registry credentails
kubectl apply -f kubernetes/utils.yaml

#creates configmap for external configs
kubectl apply -f kubernetes/configmap.yaml

#creates deployment
kubectl apply -f kubernetes/deploy.yaml

#creates service to expose the deployment
kubectl apply -f kubernetes/service.yaml

counter=1
while [ $counter -le 3 ]
do
  if [[ "$(kubectl rollout status deployment/query-url -n query-url)" =~ .*"successfully rolled out".* ]]; then
    echo "deployment is successfully rolled out"
    break
  else
    if [[ $counter -eq 3 ]]; then
     echo "deployment failed" 
     exit 1
    else
     echo "waiting for deployment rollout"
     sleep 10s
   fi
  fi
  ((counter++))
done
