## Introduction

This lab demonstrates how to build and serve a machine learning model through pipelines (MLOPS) by leveraging Openshift Data Science (RHODS). We will deploy a web application as an example of interactions with the model through REST API calls. This web application is a nodejs frontend that calls a Knative service endpoint linked to a serverless function. The serverless function acts as a pre-processor of the data between the client and the model. In more concrete terms, the model is a neural network to predict handwritten digits and the webapp is a UI where you can draw and make a predictions.  

Furthermore, we have the abilty to use GPU hardware thanks to Nvida GPU Operator, Node Feature Discovery and the Cuda library.

![archi-schema](./docs/now.png)

## Deploy


```shell
# Get the model serving endpoint
oc -n mnist get route mnist -ojsonpath='{.status.ingress[0].host}'
```

```shell
# First deploy the operators and wait for completion
oc apply -f ./pre-requisites/operators/
# Then deploy few operators CRDs and wait for completion
oc apply -f ./pre-requisites/operators-instance/
# Deploy the data science components
oc apply -k ./openshift-data-science/
# Deploy the frontend webapp
oc apply -k ./webapp/v2/manifests/
# Deploy the serverless function
oc apply -k ./openshift-serverless/manifests/
```

## Reference

Notebook originally from Thmomas Masson on kaggle: https://www.kaggle.com/code/tcmaso/mnist-guide-cnn-augmentation-tuning-99-5