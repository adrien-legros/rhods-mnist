# Rhods Mnist

## Introduction

This lab demonstrates how to build and serve a machine learning model through pipelines (MLOPS) by leveraging Red Hat OpenShift Data Science. We will deploy a web application as an example of interactions with the model through REST API calls. This web application is a nodejs frontend that calls a Knative service endpoint linked to a serverless function. The serverless function acts as a pre-processor of the data between the client and the model. In more concrete terms, the model is a neural network to predict handwritten digits and the webapp is a UI where you can draw and make a predictions.  

Furthermore, we have the abilty to use GPU hardware thanks to Nvida GPU Operator, Node Feature Discovery and the Cuda library.

This is what you get trough the user interface:

![final-result.gif](./docs/gif/final-result.gif)

## [Lab instructions](./docs/lab-instructions.md)

Here are the [lab instructions](./docs/lab-instructions.md).  
This is the lab architecture:

![archi-schema](./docs/now.png)

Once you have deployed the lab, you can find step by step instructions here: [lab instructions](./docs/lab-instructions.md).  
You will build, train, test, deploy, serve and consume a predictive model throughout this lab.


## Deploy on your own cluster

### Set your cluster domain as a variable

First of all connect to your Openshift cluster, with your oc client or through the web console.

#### Using the CLI

```shell
CLUSTER_DOMAIN=$(oc whoami --show-server | grep -oP 'https://api.\K(.*)(?=:6443)')
sed -i "s/CLUSTER_DOMAIN/${CLUSTER_DOMAIN}/g" openshift-data-science/kustomization.yaml
sed -i "s/CLUSTER_DOMAIN/${CLUSTER_DOMAIN}/g" lab/solve/base/kustomization.yaml
sed -i "s/CLUSTER_DOMAIN/${CLUSTER_DOMAIN}/g" gitops/model-serving/kustomization.yaml
```

#### Manually

Find you cluster domain name and modify CLUSTER_DOMAIN variable in files:
- openshift-data-science/kustomization.yaml
- solve/base/kustomization.yaml

### Deploy operators and their CR

Install the operators and their custom resources:

```shell
# First deploy the operators and wait for completion
oc apply -f ./pre-requisites/operators/
# Then deploy few operators CRDs and wait for completion
oc apply -f ./pre-requisites/operators-instance/
```

### Deploy the data Science Project

```shell
# Deploy the data science components
oc apply -k ./openshift-data-science/
#Create the initialization job that pull the dataset to minio bucket called *rhods*.
oc apply -k ./lab/init/
```

### Do the lab

You can now go to this link and do the lab: [Lab instructions](./docs/lab-instructions.md)

### Lab Solution

This will deploy the notebooks, the correct runtime settings, as well as the model mesh server:
- Using CPU
```shell
oc apply -k ./lab/solve/overlays/cpu
oc create -f ./lab/solve/job.yaml
```
- Using GPU
```shell
oc apply -k ./lab/solve/overlays/gpu
oc create -f ./lab/solve/job.yaml
```
Then deploy the serverless function and the web UI:

```shell
oc apply -k ./openshift-serverless/manifests/
oc apply -k ./webapp/manifests/
```

## Reset lab

**Warning:** This will delete all your work.  
When finished, you can clean your lab by running:

```shell
# Reset configurations
oc apply -k ./lab/reset/
# Reset job
oc create -f ./lab/reset/job.yaml
# Reset cron job
oc create -f ./lab/reset/cron-job.yaml
```