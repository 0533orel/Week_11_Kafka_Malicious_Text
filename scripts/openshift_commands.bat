REM Minimal example commands (adjust project, registry, image names, and envs).

REM Log in first:
REM oc login --token=xxxxx --server=https://api.your.openshift:6443

REM Clean project (if needed)
oc delete all --all
oc delete pvc --all
oc delete configmap --all
oc delete secret --all

REM MongoDB (PVC + Deployment + Service)
oc apply -f scripts/openshift/mongo-pvc.yaml
oc apply -f scripts/openshift/mongo-deploy.yaml
oc apply -f scripts/openshift/mongo-svc.yaml

REM Kafka is often installed cluster-wide or via an Operator; if you deploy a single-broker container:
oc apply -f scripts/openshift/kafka-deploy.yaml
oc apply -f scripts/openshift/kafka-svc.yaml

REM Services (assumes you pushed images to a registry accessible by OpenShift)
oc apply -f scripts/openshift/retriever-deploy.yaml
oc apply -f scripts/openshift/preprocessor-deploy.yaml
oc apply -f scripts/openshift/enricher-deploy.yaml
oc apply -f scripts/openshift/persister-deploy.yaml
oc apply -f scripts/openshift/dataretrieval-deploy.yaml
oc apply -f scripts/openshift/dataretrieval-svc.yaml
oc apply -f scripts/openshift/dataretrieval-route.yaml
